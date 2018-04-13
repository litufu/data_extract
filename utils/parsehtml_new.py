# _author : litufu
# date : 2018/4/7
from bs4 import BeautifulSoup
import pandas as pd
import re
from sqlalchemy import create_engine
from collections import OrderedDict

from itertools import chain

from collections import Counter
engine = create_engine(r'sqlite:///H:\data_extract\db.sqlite3')   #临时数据库
from utils.tools import del_same_item_from_list
from report_data_extract import models

class NoIntegrityException(Exception):
    def __init__(self,err='索引不连续'):
        Exception.__init__(self,err)

def cnToArab(x):
    '''
    将大写汉字转换为数字
    :param x: 汉字数字，只转换一到九十九
    :return: 阿拉伯数字
    '''
    comparison_sheet= {'一':'1','二':'2','三':'3','四':'4','五':'5','六':'6','七':'7','八':'8','九':'9','十':'10'}
    comparison_sheet1 = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9',
                        '十': '1'}
    comparison_sheet2 = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9',
                         '十': '0'}
    if re.match('\d+',x):
        return x
    else:
        if len(x)==1:
            return int(comparison_sheet[x])
        elif len(x)==2:
            if x not in ['二十','三十','四十','五十','六十','七十','八十','九十',] :
                return int(comparison_sheet1[x[0]]+comparison_sheet1[x[1]])
            else:
                return int(comparison_sheet2[x[0]] + comparison_sheet2[x[1]])
        elif len(x)==3:
            return int(comparison_sheet1[x[0]]+comparison_sheet1[x[2]])
        else:
            raise Exception

class HtmlPage(object):

    def __init__(self, file, pgNum):
        self.file = file
        self.pgNum = pgNum

    def get_page_content(self):
        '''
        获取当前页面的内容
        :param pf: pf = soup.find(id=re.compile('pf'))
        :return: 列表格式pc = pf.find(class_='pc').childern
        '''
        pf = self.file.page_contents_base_pgCount[self.pgNum]
        pc = pf.find(class_='pc')
        # 删除没有内容的标签，前3个div(包括页眉、页脚和空行）
        img = pc.img
        title = img.next_sibling
        origin_page_number = title.next_sibling
        tags = [img,title,origin_page_number]
        for tag in tags:
            tag.decompose()
        # 查找pc所有的子元素
        # 获取当前页的pc_children,并删除换行符
        page_content = del_same_item_from_list(list(pc.children), '\n')
        return page_content



class HtmlFile(object):

    def __init__(self,filepath):
        '''

        :param filepath: 文件路径地址
        '''
        #网页文件
        self.soup = BeautifulSoup(open(filepath,'r',encoding='utf-8'),'lxml')
        #所有的页文件
        self.pfs =  self.soup.find_all(id=re.compile('pf'))
        self.pageCount =  len(self.pfs)
        self.page_contents_base_pgCount = OrderedDict(zip(range(1, self.pageCount + 1), self.pfs))

    def to_database(self):
        '''
        将文件的页码、cell元素，元素分类，元素id保存到数据库
        :return:
        '''
        page_num = []
        file_cells = []
        cells_text = []
        cells_category = []
        cells_class = []

        for pageNum in range(1,self.pageCount+1):
            page = HtmlPage(self,pageNum)
            page_content = page.get_page_content()
            page_content_length = len(page_content)
            page_num.extend([pageNum for i in range(page_content_length)])
            file_cells.extend(page_content)

        for cell in file_cells:
            cells_text.append(re.sub('\s+','',cell.get_text()))
            cells_class.append(cell['class'])
            cells_category.append(cell['class'][0])


        data = {'id':[i for i in range(len(page_num))],'pageNum':page_num,'cellText':cells_text,'cellCategory':cells_category}
        df = pd.DataFrame(data=data)
        df.to_sql('report_data_extract_tempparsehtml', engine, index=False, if_exists='replace')

    def parse_all_dir(self):
        '''
                解析报告目录结构
                解析的编码规则：
                第一层：第一节；第二节；第n节；可以从目录中查询到
                第二层：一、二、三、
                第三层：1,2,3
                第四层：(1),(2),(3)
                :return:
        '''
        # 取得所有的cells
        df_all_cells = pd.read_sql('report_data_extract_tempparsehtml', engine)
        #扣除目录页
        dir_pagenum = df_all_cells[df_all_cells.cellText == '目录'].pageNum.values[0]
        all_cells = df_all_cells[df_all_cells.pageNum != dir_pagenum]
        # 扣除审计报告页
        start_cell = df_all_cells[df_all_cells.cellText == '一、审计报告'].id.values[0]
        end_cell = df_all_cells[df_all_cells.cellText == '二、财务报表'].id.values[0]
        all_cells = all_cells[(all_cells.id<=start_cell) | (all_cells.id>=end_cell)]
        #只筛选文本区域，不包含报表区域
        all_cells = all_cells[all_cells.cellCategory=='t']

        pattern0 = re.compile('^第([一二三四五六七八九十]{1,2})节([^：；。]*?)$')
        pattern1 = re.compile('^([一二三四五六七八九十]{1,2})、([^：；。]*?)$')
        pattern2 = re.compile('^(\d+)、([^：；。]*?)$')
        pattern3 = re.compile('\（(\d+)\）([^：；。]*?)$')

        pattern_dict = {0:pattern0,1:pattern1,2:pattern2,3:pattern3}
        #不进行下一步解析的索引
        exempt_next_ananlye_items = ['报告期内公司从事的主要业务', '核心竞争力分析', '概述', '公司未来发展的展望','重要会计政策和会计估计变更']
        self.parse_dir_structure(all_cells,level=0,pattern_dict=pattern_dict,fatherid=0,exempt_next_ananlye_items=exempt_next_ananlye_items)

    def parse_dir_structure(self,cells,level,pattern_dict,fatherid,exempt_next_ananlye_items):
        '''
        解析文件，生成目录索引
        :param cells: 该目录下所有的元素
        :param level: 第几层
        :param pattern_dict: 匹配索引的正则表达式
        :param fatherid: 父索引的id
        :param exempt_next_ananlye_items: 不进行下一步解析的索引
        :return:
        '''

        # print('cells',cells)
        #当前目录的最后一个元素的id
        cells_length = list(cells.id)[-1]
        #匹配当前目录的正则表达式
        pattern = pattern_dict[level]
        #目录匹配结果
        df_index_level = cells[cells.cellText.str.match(pattern)]
        #如果没有匹配成功，则
        if len(df_index_level) == 0:
            pass
            # print('没有发现目录')
        else:
            #检查索引的完整性,如果完整则返回；如果存在重复的索引，则比较重复索引的长短，短的留下长的删除；
            #如果存在不连续的情况，则直接报错
            # print(df_index_level)
            df_index_level = self.check_index_integrity(df_index_level,pattern)
            #检查是否需要新增索引
            df = self.comput_new_index(df_index_level, pattern, level, fatherid)
            #如果需要新增的话，新增索引
            if df is not None and len(df)>0:
                self.add_new_index_to_db(df)
            else:
                print('无新增索引')

        #求下一层
        level = level + 1
        #求下一层的cells,level,pattern_dict,fatherid,exempt_next_ananlye_items
        for i in range(len(df_index_level.cellText)):
            index_text = list(df_index_level.cellText)[i]
            id = df_index_level[df_index_level.cellText == index_text].id.values[0]

            if i+1>=len(df_index_level.cellText):
                next_id = cells_length+1
            else:
                next_text = list(df_index_level.cellText)[i+1]
                next_id = df_index_level[df_index_level.cellText == next_text].id.values[0]

            next_df = cells[(cells.id >= int(id)) & (cells.id < int(next_id))]

            indextext_content = pattern.match(index_text).groups()[1]
            if indextext_content in exempt_next_ananlye_items:
                continue
            df_content_index = pd.read_sql('report_data_extract_contentindex', engine)
            fatherid = df_content_index[df_content_index.name==indextext_content].id.values[0]
            fatherno = df_content_index[df_content_index.name==indextext_content].no.values[0]
            models.TempIndexCellCount.objects.create(name=indextext_content,no=fatherno,start_id=id,end_id=next_id)
            self.parse_dir_structure(next_df,level,pattern_dict,fatherid,exempt_next_ananlye_items)

    def check_index_integrity(self,df_index_level,pattern):
        # 检查索引的完整性
        # 提取索引汉字数字

        df_index_level.loc[:,'cn_num'] = df_index_level.cellText.map(lambda x: pattern.match(x).groups()[0])
        # 将汉字数字转换为阿拉伯数字
        df_index_level.loc[:,'arab_num'] = df_index_level.cn_num.map(cnToArab)
        num_list = list(df_index_level.arab_num)
        print(num_list)
        comp = len(set([(k - int(v)) for k, v in enumerate(num_list)]))
        #检查是否存在重复的索引
        duplicated_item_index = {}
        duplicated_counter = Counter(num_list)
        for k, v in duplicated_counter.items():
            if v > 1:
                temp_list = [i for i in range(len(num_list) - 1, -1, -1) if num_list[i] == k]
                duplicated_item_index[k] = temp_list
        print(duplicated_item_index)
        if comp == 1:
            return df_index_level
        #是否存在重复编码
        elif len(duplicated_item_index.keys())>0:
            for k,values in duplicated_item_index.items():
                # print('比较{}'.format(k))
                temp_comp = [len(list(df_index_level.cellText)[v]) for v in values]
                min_temp_comp = min(temp_comp)
                min_temp_comp_index = temp_comp.index(min_temp_comp)
                for s,v in enumerate(values):
                    if s == min_temp_comp_index:
                        pass
                    else:
                        df_index_level = df_index_level[df_index_level.cellText!=list(df_index_level.cellText)[v]]
            return df_index_level
        else:
            raise NoIntegrityException

    def comput_new_index(self,df_index_level,pattern,level,fatherid):
        '''
        新增索引，并自动排序
        #第一步：计算需要新增的内容
        #第二步：计算新增内容的编号
        #第三步：计算新增内容的父级id
        :return:
        '''
        #第一步
        #获取数据库中已经存储的索引信息
        origin_index_df = pd.read_sql('report_data_extract_contentindex',engine)
        #已经存储的索引名称
        origin_index_name = set(origin_index_df.name)
        #获取新的索引内容
        df_index_level['index_content'] = list(df_index_level.cellText.map(lambda x: pattern.match(x).groups()[1]))
        new_index_name = set(df_index_level.index_content)
        #需要新增的内容
        add_index_name = list(new_index_name.difference(origin_index_name))
        if len(add_index_name)>0:
            #按照新增内容的顺序排列
            add_index_name.sort(key=lambda x:list(df_index_level.index_content).index(x))

            # 第二步
            # 计算新增内容的编号
            # 1、读取数据库中该级别的最后一个编号
            temp_df = origin_index_df[origin_index_df.fatherid == fatherid]
            if len(temp_df) == 0:
                last_num = 0
            else:
                last_num = max(list(temp_df.no.map(lambda x: x[level * 2:(2 * (level+1))]).map(lambda x: int(x, 16))))
            # 自己编号
            self_num = [str(hex(last_num + i))[2:] for i in range(1, len(add_index_name) + 1)]
            # 将自己编号变为固定的长度---2位
            self_num_fixed_length = []
            for num in self_num:
                if len(num) == 1:
                    self_num_fixed_length.append('0' + num)
                else:
                    self_num_fixed_length.append(num)
            # 2、读取数据库中该级别的父级别的编号
            print('fatherid',fatherid)
            if len(origin_index_df) == 0:
                father_no = '0000000000'
            else:
                father_no = origin_index_df[origin_index_df.id==fatherid].no.values[0]
            # 3、父级别编号+自己的编号
            if level >= 1:
                whole_num = [father_no[:2*level] + num for num in self_num_fixed_length]
                #将编号补成10位数
                whole_num_fixed_length = [num+''.join(['0' for i in range(10-len(num))]) for num in whole_num]
                data = {'id':[i for i in range(len(origin_index_df),(len(origin_index_df)+len(whole_num_fixed_length)))],'fatherid': [fatherid for i in range(len(whole_num_fixed_length))], 'name': add_index_name,\
                        'no': whole_num_fixed_length}
            else:
                whole_num = [num for num in self_num_fixed_length]
                whole_num_fixed_length = [num + ''.join(['0' for i in range(10 - len(num))]) for num in whole_num]
                data = {'id':[i for i in range(len(origin_index_df),len(origin_index_df)+len(whole_num_fixed_length))],'fatherid': [0 for i in range(len(whole_num))], 'name': add_index_name, \
                        'no': whole_num_fixed_length}

            df = pd.DataFrame(data)
            confirm = input('是否输入下列信息：{}'.format(df))
            if confirm == 'yes':
                df = pd.concat([origin_index_df, df])
            else:
                df = origin_index_df

            return df
        else:
            return None

    def add_new_index_to_db(self,df):
        #4、新增编号到数据库
        df.to_sql('report_data_extract_contentindex', engine, if_exists='replace', index=False)

    def parse_dir_structure_1(self):
        '''
        解析报告目录结构
        解析的编码规则：
        第一层：第一节；第二节；第n节；可以从目录中查询到
        第二层：一、二、三、
        第三层：1,2,3
        第四层：(1),(2),(3)
        :return:
        '''
        #读取数据
        df = pd.read_sql('report_data_extract_tempparsehtml', engine)
        #找到目录所在页
        dir_pagenum = df[df.cellText == '目录'].pageNum.values[0]
        #将目录页去除掉，防止筛选的时候重复
        del_dir_df = df[df.pageNum != dir_pagenum]
        #确认一级索引所对应的正则表达式
        pattern0 = re.compile('^第[一二三四五六七八九十]{1,2}节.*?$')
        #匹配正则表达式找到一级索引
        df_index_level_0 = del_dir_df[del_dir_df.cellText.str.match(pattern0)]
        #将取得的一级索引保存到索引对应的临时数据库，便于以后对页面cell进行分类
        df_index_level_0.to_sql('first_index', engine, index=False, if_exists='replace')



    def check_index_integrity_1(self):
        df_index_level_0 = pd.read_sql('first_index',engine)
        # 检查索引的完整性
        pattern1 = re.compile('^第([一二三四五六七八九十]{1,2})节.*?')
        # 提取索引汉字数字
        df_index_level_0['cn_num'] = df_index_level_0.cellText.map(lambda x: pattern1.match(x).groups()[0])
        # 将汉字数字转换为阿拉伯数字
        df_index_level_0['arab_num'] = df_index_level_0.cn_num.map(cnToArab)
        num_list = list(df_index_level_0.arab_num)
        comp = len(set([k - v for k, v in enumerate(num_list)]))
        if comp == 1:
            return True
        else:
            return False



    def comput_new_index_1(self):
        '''
        新增索引，并自动排序
        #第一步：计算需要新增的内容
        #第二步：计算新增内容的编号
        #第三步：计算新增内容的父级id
        :return:
        '''
        #第一步
        #获取数据库中已经存储的索引信息
        origin_index_df = pd.read_sql('content_index',engine)
        #已经存储的索引名称
        origin_index_name = set(origin_index_df.name)
        #新的索引表
        new_index_df = pd.read_sql('first_index', engine)
        pattern = re.compile('^第[一二三四五六七八九十]{1,2}节(.*?)$')
        #获取新的索引内容
        new_index_df['index_content'] = new_index_df.cellText.map(lambda x: pattern.match(x).groups()[0])
        new_index_name = set(new_index_df.index_content)
        #需要新增的内容
        add_index_name = list(new_index_name.difference(origin_index_name))
        #按照新增内容的顺序排列
        add_index_name.sort(key=lambda x:list(new_index_df.index_content).index(x))
        return add_index_name

    def compute_new_index_num_1(self,origin_index_df,add_index_name):
        #第二步
        #计算新增内容的编号
        #1、读取数据库中该级别的最后一个编号
        last_num = max(list(origin_index_df.no.map(lambda x:x[(1-1)*2:(1*2-1)]).map(lambda x:int(x,16))))
        #自己编号
        self_num = [str(hex(last_num+i))[2:] for i in range(1,len(add_index_name)+1)]
        #将自己编号变为固定的长度---2位
        self_num_fixed_length = []
        for num in self_num:
            if len(num) == 1:
                self_num_fixed_length.append('0'+num)
            else:
                self_num_fixed_length.append(num)
        #2、读取数据库中该级别的父级别的编号
        level = 1
        if level == 1:
            pass
        # 3、父级别编号+自己的编号
        if level == 1:
            whole_num = [num+'00000000' for num in self_num_fixed_length]

        return whole_num

    def add_new_index_to_db_1(self,whole_num,add_index_name):
        #4、新增编号到数据库
        add_num_data = {'father':[0 for i in range(len(whole_num))],'name':add_index_name,'no':whole_num}
        df = pd.DataFrame(add_num_data)
        df.to_sql('content_index', engine, if_exists='append', index=False)




    def parse_dir_structure_2(self):
        '''
        解析报告目录结构
        解析的编码规则：
        第一层：第一节；第二节；第n节；可以从目录中查询到
        第二层：一、二、三、
        第三层：1,2,3
        第四层：(1),(2),(3)
        :return:
        '''
        df_all_cells = pd.read_sql('tempparsehtml', engine)
        df_index_level_1 = pd.read_sql('first_index', engine)
        df_content_index = pd.read_sql('content_index', engine)
        # 根据df_index_level_1中的index筛选第一级索引对应的所有元素
        next_df = df_all_cells[(df_all_cells.index >= 152) & (df_all_cells.index < 381)]
        pattern1 = re.compile('^[一二三四五六七八九十]{1,2}、.*?$')
        df_index_level_1 = next_df[next_df.cellText.str.match(pattern1)]
        if len(next_df) == 0:
            pass
        else:
            df_index_level_1.to_sql('temp_index_02', engine, index=False, if_exists='replace')

    def check_index_integrity_2(self):
        df_index_level_1 = pd.read_sql('temp_index_02',engine)
        # 检查索引的完整性
        pattern1 = re.compile('^([一二三四五六七八九十]{1,2})、.*?$')
        # 提取索引汉字数字
        df_index_level_1['cn_num'] = df_index_level_1.cellText.map(lambda x: pattern1.match(x).groups()[0])
        # 将汉字数字转换为阿拉伯数字
        df_index_level_1['arab_num'] = df_index_level_1.cn_num.map(cnToArab)
        num_list = list(df_index_level_1.arab_num)
        comp = len(set([k - v for k, v in enumerate(num_list)]))
        if comp == 1:
            print('索引连贯')
            return True
        else:
            return False

    def comput_new_index_2(self):
        '''
        新增索引，并自动排序
        #第一步：计算需要新增的内容
        #第二步：计算新增内容的编号
        #第三步：计算新增内容的父级id
        :return:
        '''
        #第一步
        #获取数据库中已经存储的索引信息
        origin_index_df = pd.read_sql('content_index',engine)
        #已经存储的索引名称
        origin_index_name = set(origin_index_df.name)
        #新的索引表
        new_index_df = pd.read_sql('temp_index_02', engine)
        pattern = re.compile('^[一二三四五六七八九十]{1,2}、(.*?)$')
        #获取新的索引内容
        new_index_df['index_content'] = new_index_df.cellText.map(lambda x: pattern.match(x).groups()[0])
        new_index_name = set(new_index_df.index_content)
        #需要新增的内容
        add_index_name = list(new_index_name.difference(origin_index_name))
        #按照新增内容的顺序排列
        add_index_name.sort(key=lambda x:list(new_index_df.index_content).index(x))
        return add_index_name

    def compute_new_index_num_2(self,origin_index_df,add_index_name):
        #第二步
        #计算新增内容的编号
        #1、读取数据库中该级别的最后一个编号
        last_num = max(list(origin_index_df.no.map(lambda x:x[(2-1)*2:(2*2-1)]).map(lambda x:int(x,16))))
        #自己编号
        self_num = [str(hex(last_num+i))[2:] for i in range(1,len(add_index_name)+1)]
        #将自己编号变为固定的长度---2位
        self_num_fixed_length = []
        for num in self_num:
            if len(num) == 1:
                self_num_fixed_length.append('0'+num)
            else:
                self_num_fixed_length.append(num)
        #2、读取数据库中该级别的父级别的编号
        level = 2
        if level == 2:
            fatherid = 2
            father_num = '02'
        # 3、父级别编号+自己的编号
        if level == 1:
            whole_num = [father_num+num+'000000' for num in self_num_fixed_length]

        return whole_num


    def add_new_index_to_db_2(self,whole_num,add_index_name):
        #4、新增编号到数据库
        add_num_data = {'father':[0 for i in range(len(whole_num))],'name':add_index_name,'no':whole_num}
        df = pd.DataFrame(add_num_data)
        df.to_sql('content_index', engine, if_exists='append', index=False)

class HtmlTable(object):

    pass



if __name__ == '__main__':
    # df = pd.read_sql('content_index',engine)
    # print(df[0:2])

    origin_index_df = pd.read_sql('report_data_extract_contentindex', engine)
    # origin_index_df = origin_index_df[origin_index_df.id==1]
    # origin_index_df.to_sql('report_data_extract_contentindex',engine,if_exists='replace',index=False)
    print(origin_index_df)
    # print('df_index_level_1',df_index_level_1)
    #


    # # #第一步：保存文件到数据库
    # filepath = r'H:\data_extract\report\shenzhen\1204618902.html'
    # file = HtmlFile(filepath)
    # file.parse_all_dir()
    # file.to_database()

    #第一步：得到索引
    # df = pd.read_sql('report_data_extract_tempparsehtml',engine)
    # df_length = len(df)
    # print(df_length)
    # print(df[:10])
    # # df.to_csv('re.csv')
    # remain = df
    # # print(set(df.cellCategory))
    # # 查找目录
    # dir_pagenum = df[df.cellText=='目录'].pageNum.values[0]
    # df = df[df.pageNum!=dir_pagenum]
    # #找到索引
    # # pattern = re.compile('^(第[一二三四五六七八九十]{1,2}节.*?)\.*?(\d+)')
    # pattern0 = re.compile('^第[一二三四五六七八九十]{1,2}节.*?$')
    # df = df[df.cellText.str.match(pattern0)]
    # print(df)
    # df.to_sql('first_index',engine,index=False,if_exists='replace')
    # 检验索引的完整性
    # df = pd.read_sql('first_index',engine)
    # pattern = re.compile('^第([一二三四五六七八九十]{1,2})节.*?')
    # df['dir'] = df.cellText.map(lambda x: pattern.match(x).groups()[0])
    # df['num'] = df.dir.map(f)
    # num_list = list(df.num)
    # comp = len(set([k-v for k,v in enumerate(num_list)]))
    # if comp == 1:
    #     print('目录顺序连贯')
    # else:
    #     raise Exception
    # #保存索引
    # #编码格式:共分为5层，每层从01-ff,采用16进制
    # # 总索引1；第一层：01 00 00 00 00-ff 00 00 00 00；第二层：0101000000-ffff000000；
    # index_data = {'name':['总索引',],'father':[0,],'no':['0000000000',]}
    # df = pd.DataFrame(index_data)
    # df.to_sql('content_index',engine,if_exists='append',index=True)
    #检查是否已经存在该索引,层级是否正确
    # origin_index_df = pd.read_sql('content_index',engine)
    # origin_index_name = set(origin_index_df.name)
    # print(origin_index_df)
    # new_index_df = pd.read_sql('first_index', engine)
    # pattern = re.compile('^第[一二三四五六七八九十]{1,2}节(.*?)$')
    # new_index_df['index_content'] = new_index_df.cellText.map(lambda x: pattern.match(x).groups()[0])
    # new_index_name = set(new_index_df.index_content)
    # # #需要新增的内容
    # add_index_name = list(new_index_name.difference(origin_index_name))
    # # #按照新增内容的顺序排列
    # add_index_name.sort(key=lambda x:list(new_index_df.index_content).index(x))
    # # #计算新增内容的编号
    # # #1、读取数据库中该级别的最后一个编号
    # last_num = max(list(origin_index_df.no.map(lambda x:x[(1-1)*2:(1*2-1)]).map(lambda x:int(x,16))))
    # # #自己编号
    # self_num = [str(hex(last_num+i))[2:] for i in range(1,len(add_index_name)+1)]
    # self_num_fixed_length = []
    # for num in self_num:
    #     if len(num) == 1:
    #         self_num_fixed_length.append('0'+num)
    #     else:
    #         self_num_fixed_length.append(num)
    #
    # print(self_num)
    # print(self_num_fixed_length)
    # # #2、读取数据库中该级别的父级别的编号
    # level = 1
    # if level == 1:
    #     pass
    # # # 3、父级别编号+自己的编号
    # if level == 1:
    #     whole_num = [num+'00000000' for num in self_num_fixed_length]
    # #
    # # # #4、新增编号到数据库
    # add_num_data = {'father':[0 for i in range(len(whole_num))],'name':add_index_name,'no':whole_num}
    # df = pd.DataFrame(add_num_data)
    # print(df)
    # df.to_sql('content_index', engine, if_exists='append', index=False)

    # df = pd.read_sql('content_index',engine)
    # df = df.dropna()
    # df.to_sql('content_index',engine,if_exists='replace',index=False)
    # print(df)
    #
    # print(new_index_df)
    # print(add_index_name)

    # pattern = re.compile('^第[一二三四五六七八九十]{1,2}节(.*?)')
    # new_index_df['index_content'] = new_index_df.cellText.map(lambda x: pattern.match(x).groups()[0])
    # print(new_index_df)

    # print(comp)



    # df['dir'] = df.cellText.map(lambda x:pattern.match(x).groups()[0])
    # df['dir_pageNum'] = df.cellText.map(lambda x: pattern.match(x).groups()[1])
    #找到各个索引对应的页码
    # dirs = list(df.dir)
    # print(dirs)
    # remain2 = remain[remain.pageNum != dir_pagenum]
    # print(remain2[:25])
    # dir_pageNums = []
    # for dir in dirs:
    #     print(dir)
    #     page_num = remain2[remain2.cellText==dir].pageNum.values[0]
    #     dir_pageNums.append(page_num)
    # print(dir_pageNums)

    #求下一级索引
    # next_df = remain[(remain.pageNum>=5) & (remain.pageNum<9) ]
    # pattern1 = re.compile('^[一二三四五六七八九十]{1,2}、.*?$')
    # next_df = next_df[next_df.cellText.str.match(pattern1)]
    # next_df['dir'] = next_df.cellText.map(lambda x: pattern1.match(x).groups()[0])
    # 找到各个索引对应的页码
    # dirs = list(next_df.dir)
    # print(dirs)
    # remain2 = remain[remain.pageNum != dir_pagenum]
    # print(remain2[:25])
    # dir_pageNums = []
    # for dir in dirs:
    #     print(dir)
    #     page_num = next_df[next_df.cellText == dir].pageNum.values[0]
    #     dir_pageNums.append(page_num)
    # print(dir_pageNums)


    # print(next_df)
