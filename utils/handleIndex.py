# _author : litufu
# date : 2018/4/7
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()

from bs4 import BeautifulSoup
import pandas as pd
pd.set_option('mode.chained_assignment','raise')
import re
import datetime
import numpy as np
from sqlalchemy import create_engine
engine = create_engine(r'sqlite:///H:\data_extract\db.sqlite3')
from collections import OrderedDict
from utils import mytools
from collections import Counter

import logging
from log.logs import setup_logging
  #临时数据库
from utils.mytools import del_same_item_from_list
from utils.mytools import cnToArab,compute_num_list,compare_num_list,comput_no
from report_data_extract import models
from utils.autoGetIndexPattern import get_index_format,get_std_index

class NoIntegrityException(Exception):
    def __init__(self,err='索引不连续'):
        Exception.__init__(self,err)

class NoFoundIndexException(Exception):
    def __init__(self,err='没有在文中找到索引对应的元素'):
        Exception.__init__(self,err)

class FilenameErrorException(Exception):
    def __init__(self,err='文件名解析错误'):
        Exception.__init__(self,err)



class HtmlPage(object):

    def __init__(self, file, pgNum):
        self.file = file
        self.pgNum = pgNum

    # @property
    def get_page_content(self):
        '''
        获取当前页面的内容，删除页眉页脚和内容为空的行（不包括内容为空的单元格）
        :param pf: pf = soup.find(id=re.compile('pf'))
        :return: 列表格式pc = pf.find(class_='pc').childern
        '''
        pf = self.file.page_contents_base_pgCount[self.pgNum]
        pc = pf.find(class_='pc')
        # 删除没有内容的标签，前3个div(包括页眉、页脚和空行）
        tags = []
        pattern = re.compile('^[^年]*?\d+(/\d+)?[^年]*?$')
        for child in pc.children:
            text = re.sub('\s+','',child.get_text())
            if pattern.match(text):
                tags.append(child)
                break
            else:
                tags.append(child)


        #删除大部分页面都存在的重复元素（class相同，内容相同),
        for child in pc.children:
            cell_text = re.sub('\s+','',child.get_text())
            cell_class = '_'.join(child['class'])
            for k,v in self.file.del_duplicated_cells_dict.items():
                if k == cell_class and v == cell_text and child not in tags:
                    tags.append(child)

        for tag in tags:
            tag.decompose()

        all_text_tags = pc.find_all('div', class_='t')
        if all_text_tags != None:
            for tag in all_text_tags:
                if re.sub('\s+', '', tag.get_text()) == '' and tag.previous_sibling is None:
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
        self.filepath = filepath
        #解析市场、股票代码、报告期间
        self.get_market_code_accper()
        #解析html
        self.soup = BeautifulSoup(open(filepath, 'r', encoding='utf-8'), 'lxml')
        #所有的页文件
        self.pfs =  self.soup.find_all(id=re.compile('pf'))
        #获取文件总页数
        self.pageCount =  len(self.pfs)
        #获取html的pageid
        self.pageId = [pf['id'] for pf in self.pfs]
        #将html的pageid与真实的页码对应气啦
        self.pageIdToNum = OrderedDict(zip(self.pageId,range(1,self.pageCount+1)))
        #将真实页码与其页面文件内容对应起来
        self.page_contents_base_pgCount = OrderedDict(zip(range(1, self.pageCount + 1), self.pfs))
        #删除大多数页面中同时存在的元素的class 和get_text() 的字典
        self.del_duplicated_cells_dict = self.most_duplicated_cells()
        #将页码(页码，元素内容，元素分类）存储到df中
        self.file_cells = []
        self.df_all_cells = self.all_cells_to_df()

    def most_duplicated_cells(self):
        # 删除大多数页中同时存在的元素
        all_cells = []
        cells_text = []
        cells_class = []
        page_nums = []
        for pageNum in range(1,self.pageCount+1):
            pf = self.page_contents_base_pgCount[pageNum]
            pc = pf.find(class_='pc')
            all_cells.extend(list(pc.children))
            page_nums.extend([pageNum for i in range(len(list(pc.children)))])
        for cell in all_cells:
            cells_text.append(re.sub('\s+','',cell.get_text()))
            cells_class.append('_'.join(cell['class']))

        data = {'pgnum':page_nums,'cellText':cells_text,'cells_class':cells_class,'cells':all_cells}
        df = pd.DataFrame(data=data)
        df_count = df.groupby(['cells_class', 'cellText']).count()
        df_duplicated = df_count[df_count['pgnum'] > 70]
        df_duplicated = df_duplicated.reset_index()

        if len(df_duplicated)>0:
            return dict(zip(list(df_duplicated['cells_class']),list(df_duplicated['cellText'])))
        else:
            return {}

    def get_market_code_accper(self):
        '''
        通过文件名获取市场、证券代码和报告日期信息
        文件名命名规则举例：’sz'+'000001'+'20171231'
        :return:
        self.market = 'sz'
        self.code = '000001'
        self.accper = 'date(2017,12,31)
        '''
        filename = os.path.basename(self.filepath)
        pattern = re.compile('(.*?).html')
        try:
            self.market,self.code,self.accper = pattern.match(filename).groups()[0].split('_')
            if self.market not in ['sz','sh']:
                raise FilenameErrorException
            if len(self.code)!=6:
                raise FilenameErrorException
            if not self.code.startswith(('0','3','6')):
                raise FilenameErrorException
            self.accper = datetime.datetime.strptime(self.accper,'%Y%m%d').date()
        except Exception as e:
            raise FilenameErrorException

    def all_cells_to_df(self):
        '''
        将文件的页码、cell元素，元素分类，元素id保存到DataFrame中
        :return:
        '''
        page_num = []
        cells_text = []
        cells_category = []
        cells_class = []

        for pageNum in range(1,self.pageCount+1):
            page = HtmlPage(self,pageNum)
            page_content = page.get_page_content()
            page_content_length = len(page_content)
            page_num.extend([pageNum for i in range(page_content_length)])
            self.file_cells.extend(page_content)
        for cell in self.file_cells:
            cells_text.append(re.sub('\s+','',cell.get_text()))
            cells_class.append(cell['class'])
            cells_category.append(cell['class'][0])

        data = {'id':[i for i in range(len(page_num))],'pageNum':page_num,'cellText':cells_text,'cellCategory':cells_category}
        df = pd.DataFrame(data=data)
        return df

    def get_std_dir(self,root,market,layer=0, fatherid=''):
        '''
        初始化深圳交易所标准库
        根据一份已有的报告生成标准的索引，然后再在这个标准索引的基础上进行增加
        :param root:bs4.Beautifulsoup root = file.soup.find('div',id='outline')
        :param layer:默认为0
        :param fatherid:默认为空字符串
        :return:
        '''
        layer = layer + 1
        ul = root.find('ul')
        for k, child in enumerate(ul.children):
            k = str(hex(k+1))[2:]
            #补足两位
            if len(k) == 1:
                k = '0' + k

            if child.find('ul'):
                print('父级编码', fatherid, end=' ')
                print('层次编码', layer, end=' ')
                print('序列编号：', k, end=' ')
                last_num = '{}{}'.format(fatherid,k)
                last_num=last_num + ''.join(['0' for i in range(8 - len(last_num))])
                print('最终编码',last_num,end=' ')
                no_name = child.a.get_text()
                no_name = re.sub('\s+','',no_name)
                print(no_name)
                print('页码',self.pageIdToNum[child.a['href'][1:]])
                name = self.extract_index_content(no_name)
                name = re.sub('\s+','',name)
                print(name)
                if models.StdContentIndex.objects.filter(market='sz', no=last_num):
                    obj = models.StdContentIndex.objects.get(market='sz', no=last_num)
                    obj.has_child = '1'
                    obj.save()
                else:
                    models.StdContentIndex.objects.create(market=market,name=name,no_name=no_name,fatherno=fatherid,level=layer,\
                                        selfno=k,no=last_num,has_child='1')
                self.get_std_dir(child, layer=layer,fatherid=fatherid + '{}'.format(k),market=market)
            else:
                last_num = '{}{}'.format(fatherid, k)
                last_num = last_num + ''.join(['0' for i in range(8 - len(last_num))])
                no_name = child.a.get_text()
                no_name = re.sub('\s+', '', no_name)
                name = self.extract_index_content(no_name)
                name = re.sub('\s+', '', name)
                if models.StdContentIndex.objects.filter(market='sz', no=last_num):
                    obj = models.StdContentIndex.objects.get(market='sz', no=last_num)
                    obj.has_child = '0'
                    obj.save()
                else:
                    models.StdContentIndex.objects.create(market=market,name=name,no_name=no_name,fatherno=fatherid,level=layer,\
                                        selfno=k,no=last_num,has_child='0')

    def clearTempIndexCellCount(self):
        # 清空数据库TempIndexCellCount
        models.TempIndexCellCount.objects.all().delete()

    def clearTempParseHtml(self):
        # 清空数据库TempParseHtml
        models.TempParseHtml.objects.all().delete()

    def get_dir_pos_base_index(self,root,market,layer=0,fatherno=''):
        '''
        如果解析后发现了索引，则根据索引对元素进行分类，生成TempIndexCellCount
        :param root:bs4.Beautifulsoup root = file.soup.find('div',id='outline')
        :param market:'sz','sh'
        :param layer:从第0层开始
        :param fatherno:初始为空
        :return:索引名，索引编码（根据标准索引而来），元素开始位置
        '''
        layer = layer + 1
        ul = root.find('ul')
        if ul:
            for k, child in enumerate(ul.children):
                pageNum = self.pageIdToNum[child.a['href'][1:]]
                no_name = child.a.get_text()
                no_name = re.sub('\s+', '', no_name)
                name = self.extract_index_content(no_name)
                name = re.sub('\s+', '', name)
                if fatherno == '':
                    pass
                else:
                    if layer == 1:
                        pass
                    else:
                        fatherno = fatherno[:2*(layer-1)]
                if models.StdContentIndex.objects.filter(market=market,name=name,level=layer,fatherno=fatherno):
                    if len(models.StdContentIndex.objects.filter(market=market,name=name,level=layer,fatherno=fatherno))>1:
                        no = models.StdContentIndex.objects.filter(market=market, level=layer, name=name, fatherno=fatherno)[1].no
                    else:
                        no = models.StdContentIndex.objects.get(market=market, level=layer,name=name,fatherno=fatherno).no
                    if models.TempParseHtml.objects.filter(pageNum=pageNum,cellText=no_name):
                        start_id = models.TempParseHtml.objects.get(pageNum=pageNum,cellText=no_name).id
                        # print(start_id)
                        if models.TempIndexCellCount.objects.filter(no=no):
                            pass
                        else:
                            models.TempIndexCellCount.objects.create(name=name,no=no,start_id=start_id,cell_text=no_name)
                    else:
                        print('未在文件中找到该索引，请确认索引是否正确：{}'.format(name))
                        k=1
                        page_cells = models.TempParseHtml.objects.filter(pageNum=pageNum)
                        for page_cell in page_cells:
                            if mytools.similar(no_name,page_cell.cellText):
                                start_id = page_cell.id
                                if models.TempIndexCellCount.objects.filter(no=no):
                                    pass
                                else:
                                    models.TempIndexCellCount.objects.create(name=name, no=no, start_id=start_id,\
                                                                             cell_text=page_cell.cellText)

                                    k=0
                        if k==0:
                            print('通过近似分析已经存储')
                        else:
                            raise NoFoundIndexException
                else:
                    print('没有找到对应的索引，考虑是否新增索引:{}'.format(name))
                    choice = input('是否选择新增')
                    if choice == 'yes':
                        if child.find('ul'):
                            has_child = '1'
                        else:
                            has_child = '0'
                        self.add_new_index_in_std(market, layer, fatherno, name, no_name, has_child)
                        self.get_dir_pos_base_index(root,market,layer=0,fatherno='')
                    else:
                        raise Exception

                if child.find('ul'):
                    self.get_dir_pos_base_index(child, layer=layer, fatherno=no, market=market)

    def extract_index_content(self,content):

        pattern0 = re.compile('^第([一二三四五六七八九十]{1,2})节(.*?)$')
        pattern1 = re.compile('^([一二三四五六七八九十]{1,2})、(.*?)$')
        pattern2 = re.compile('^(\d+)[、\.](.*?)$')
        pattern3 = re.compile('[\(（](\d+)[\)）](.*?)$')

        patterns = [pattern0,pattern1,pattern2,pattern3]
        for pattern in patterns:
            result = pattern.match(content)
            if result:
                return result.groups()[1]

    def add_new_index_in_std(self,market,layer,fatherno,name,no_name,has_child):
        '''
        向标准索引中增加索引
        :param market: 市场
        :param layer: 索引层级
        :param fatherno: 父级索引编码
        :param name: 索引名称
        :param no_name: 带编号索引名称
        :param has_child: 是否有子索引
        :return:
        '''
        sibilings = models.StdContentIndex.objects.filter(market=market, level=layer, fatherno=fatherno)
        selfno = len(sibilings) + 1
        if fatherno == '0':
            fatherno = ''
        last_num = '{}{}'.format(fatherno, selfno)
        last_num = last_num + ''.join(['0' for i in range(8 - len(last_num))])
        models.StdContentIndex.objects.create(market=market, name=name, no_name=no_name, fatherno=fatherno,
                                              level=layer,
                                              selfno=selfno, no=last_num, has_child=has_child)

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
        df_all_cells = self.df_all_cells.loc[:]
        #扣除目录页
        dir_pagenum = df_all_cells.loc[df_all_cells.cellText == '目录'].pageNum.values[0]
        all_cells = df_all_cells.loc[df_all_cells.pageNum != dir_pagenum]
        if self.market == 'sz':
            # # 扣除审计报告页
            start_cell = df_all_cells.loc[df_all_cells.cellText == '一、审计报告'].id.values[0]
            end_cell = df_all_cells.loc[df_all_cells.cellText == '二、财务报表'].id.values[0]
            all_cells = all_cells.loc[(all_cells.id<=start_cell) | (all_cells.id>=end_cell)]
        # #只筛选文本区域，不包含报表区域
        all_cells = all_cells.loc[all_cells.cellCategory=='t']
        # 深圳年报解析不同级别索引的正则表达式
        sz_pattern0 = re.compile('^第([一二三四五六七八九十]{1,2})节([^；。]*?)$')
        sz_pattern1 = re.compile('^([一二三四五六七八九十]{1,2})、([^；。]*?)$')
        sz_pattern2 = re.compile('^(\d+)、([^；。]*?)$')
        sz_pattern3 = re.compile('\（(\d+)\）([^；。]*?)$')
        sz_pattern_dict = {1: sz_pattern0, 2: sz_pattern1, 3: sz_pattern2, 4: sz_pattern3}
        #上证年报
        sh_pattern0 = re.compile('^第([一二三四五六七八九十]{1,2})节([^；。]*?)$')
        sh_pattern1 = re.compile('^([一二三四五六七八九十]{1,2})、([^；。]*?)$')
        sh_pattern2 = re.compile('^[\(（]([一二三四五六七八九十]{1,2})[\)）]([^；。]*?)$')
        sh_pattern3 = re.compile('^(\d+)[\.\、]?([^；。]*?)$')
        sh_pattern4 = re.compile('[\(（](\d+)[\)）][\.\、]?([^；。]*?)。?$')
        sh_pattern_dict = {1: sh_pattern0, 2: sh_pattern1, 3: sh_pattern2, 4: sh_pattern3,5:sh_pattern4}

        if self.market == 'sz':
            pattern_dict = sz_pattern_dict
        elif self.market == 'sh':
            pattern_dict = sh_pattern_dict

        self.parse_dir_structure(all_cells,level=0,pattern_dict=pattern_dict,fatherno='',pattern_last='')

    def parse_dir_structure(self,cells,level,pattern_dict,fatherno,pattern_last):
        '''
        解析文件，生成目录索引对应的其实元素位置。
        :param cells: 该目录下所有的元素
        :param level: 第几层
        :param pattern_dict: 匹配索引的正则表达式
        :param fatherno: 父索引的编码
        :param exempt_next_ananlye_items: 不进行下一步解析的索引
        :return:
        '''
        if self.market =='sz':
            if level>=4:
                return '解析完成'
        elif self.market =='sh':
            if level>=5:
                return '解析完成'

        if fatherno == '':
            pass
        else:
            fatherno = fatherno[:level * 2]
        level = level + 1

        #当前目录的最后一个元素的id
        print(cells.id)
        cells_length = list(cells.id)[-1]
        #匹配当前目录的正则表达式
        if self.market == 'sz':
            pattern = pattern_dict[level]
        elif self.market == 'sh':
            if level == 1 or level == 2:
                pattern = pattern_dict[level]
            elif level == 3:
                pattern = pattern_dict[3]
                if len(cells.loc[cells.loc[:,'cellText'].str.match(pattern)])>0:
                    if len(cells.loc[cells.loc[:,'cellText'].str.match(pattern_dict[4])])>0 and \
                            (cells.loc[cells.loc[:, 'cellText'].str.match(pattern_dict[4])].cellText.str.contains('编制基础').any() or \
                             cells.loc[cells.loc[:, 'cellText'].str.match(pattern_dict[4])].cellText.str.contains( '货币资金').any() or
                             cells.loc[cells.loc[:, 'cellText'].str.match(pattern_dict[4])].cellText.str.contains(
                                 '会计期间').any()
                                ):
                        pattern = pattern_dict[4]
                    else:
                        pass
                elif len(cells.loc[cells.loc[:,'cellText'].str.match(pattern_dict[4])])>0:
                    pattern = pattern_dict[4]
                else:
                    print('level3匹配出差了')
                    return
            elif level == 4:
                if pattern_last == pattern_dict[3]:
                    pattern = pattern_dict[4]
                elif pattern_last == pattern_dict[4]:
                    pattern = pattern_dict[5]
                else:
                    print('level4匹配出差了')
                    return
            elif level == 5:
                if pattern_last == pattern_dict[4]:
                    pattern = pattern_dict[5]
                else:
                    print('level5匹配出差了')
                    return

        #目录匹配结果
        objs = get_std_index(self.market, fatherno, level)
        df_index_level = cells.loc[cells.loc[:,'cellText'].str.match(pattern)]
        #如果没有找到对应的索引，可以尝试自动匹配
        if len(df_index_level)<len(objs):
            print('自动索引开始')
            pattern = get_index_format(cells,self.market,fatherno,level)
            if pattern is not None:
                df_index_level = cells.loc[cells.loc[:, 'cellText'].str.match(pattern)]
        #如果没有匹配成功，则
        if len(df_index_level) == 0:
            pass
        else:
            #检查索引的完整性,如果完整则返回；如果存在重复的索引，则比较重复索引的长短，短的留下长的删除；
            #如果存在不连续的情况，则直接报错
            print(df_index_level)
            df_index_level = self.check_index_integrity(df_index_level,pattern,fatherno,level)
            print(df_index_level)
            # 检查是否需要新增索引,应该注销掉
            self.comput_new_index(list(df_index_level.cellText), pattern, level, fatherno)

        #求下一层的cells,level,pattern_dict,fatherid
        for i in range(len(df_index_level.cellText)):
            #包含序号的索引名
            index_text = list(df_index_level.cellText)[i]
            #去除序号的索引名
            indextext_content = pattern.match(index_text).groups()[1]
            #求出该索引的起始和终止位置
            start_id = df_index_level.loc[df_index_level.cellText == index_text].id.values[0]
            print('start_id',start_id)
            if i+1>=len(df_index_level.cellText):
                next_id = cells_length+1
            else:
                next_text = list(df_index_level.cellText)[i+1]
                next_id = df_index_level.loc[df_index_level.cellText == next_text].id.values[0]
            print('next_id', next_id)
            next_df = cells.loc[(cells.id >= int(start_id)) & (cells.id < int(next_id))]

            # 信息按照标准索引进行修改
            #如果没有在标准表中找到索引，则检查是否近似相等
            print(self.market)
            print(level)
            print(indextext_content)
            if not (models.StdContentIndex.objects.filter(market=self.market,fatherno=fatherno,level=level,name=indextext_content)
                    or models.StdCompareIndex.objects.filter(market=self.market,fatherno=fatherno,compare_name=indextext_content)):
                pass

                # std_names_objs = models.StdContentIndex.objects.filter(level=level,fatherno=fatherno)
                # for std_name_obj in std_names_objs:
                #     if mytools.similar(std_name_obj.name, indextext_content):
                #         # df_index_level.loc[df_index_level.index_content == indextext_content].cellText = std_name_obj.no_name
                #         indextext_content = std_name_obj.name
            else:
                if models.StdContentIndex.objects.filter(market=self.market,level=level,name=indextext_content):
                    objs = models.StdContentIndex.objects.filter(market=self.market,level=level,fatherno=fatherno,name=indextext_content)
                    if len(objs) > 1:
                        if objs[0].name == '其他综合收益':
                            if '现金流量' in next_text:
                                no = models.StdContentIndex.objects.filter(market=self.market,level=level, fatherno=fatherno,
                                                                           name=indextext_content)[1].no
                            else:
                                no = models.StdContentIndex.objects.filter(market=self.market,level=level, fatherno=fatherno,
                                                                           name=indextext_content)[0].no
                        else:
                            print('出错了')
                    else:
                        print([(obj.name, obj.no) for obj in objs])
                        print(level, fatherno, indextext_content)
                        no = models.StdContentIndex.objects.filter(market=self.market,level=level, fatherno=fatherno,
                                                              name=indextext_content)[0].no
                else:
                    no = models.StdCompareIndex.objects.filter(market=self.market,fatherno=fatherno,compare_name=indextext_content)[0].index_name.no

                #如果临时索引统计表已经存储了，则不再统计
                if models.TempIndexCellCount.objects.filter(no=no):
                    pass
                else:
                #增加改索引至临时索引表
                    models.TempIndexCellCount.objects.create(cell_text=index_text, name=indextext_content, no=no,start_id=start_id)
                #如果该索引没有下一层索引，则继续改成的下一个索引
                if len(models.StdContentIndex.objects.filter(market=self.market,level=level, fatherno=fatherno, name=indextext_content))>0:
                    if models.StdContentIndex.objects.filter(market=self.market,level=level, fatherno=fatherno, name=indextext_content)[0].has_child=='0':
                        continue
                    else:
                        self.parse_dir_structure(next_df, level, pattern_dict, no,pattern)
                elif len(models.StdCompareIndex.objects.filter(market=self.market,fatherno=fatherno,compare_name=indextext_content))>0:
                    if models.StdCompareIndex.objects.filter(market=self.market,fatherno=fatherno,compare_name=indextext_content)[0].index_name.has_child == '0':
                        continue
                    else:
                        self.parse_dir_structure(next_df, level, pattern_dict, no,pattern)
                else:
                    raise Exception
                    #如果该索引有下一层索引，则继续下一层索引
                    # self.parse_dir_structure(next_df, level, pattern_dict, no)

    def check_index_integrity(self,df_index_level,pattern,fatherno,level):
        # 检查索引的完整性
        #第一步：自行排序比较是否连续，如果连续则返回目录，不连续则与标准目录进行精确匹配
        celltexts = list(df_index_level.cellText)
        num_list = compute_num_list(celltexts, pattern)
        #删除序号超过索引长度的索引
        remain_index = []
        for k,v in enumerate(num_list):
            if v <= (len(num_list) + 10):
                remain_index.append(k)

        df_index_level = df_index_level.iloc[remain_index, :]
        celltexts = list(df_index_level.cellText)
        num_list = compute_num_list(celltexts, pattern)
        comp = compare_num_list(num_list)
        if comp == 1:
            return df_index_level
        else:
            #第二步：与标准目录进行匹配，生成精确匹配结果，检查标准匹配结果是否连续
            #如果连续则返回精确匹配目录，对剩余部分：
            # （1）删除与匹配一致结果相同的序号目录，
            # （2）比较对照库检验是否连续
            comm_index, diff_index,origin_index_names_remain = self.compare_with_std(celltexts,pattern,fatherno,level)
            celltexts_compare_with_std = [celltexts[index] for index in comm_index]
            celltexts_compare_with_std_num = [num_list[index] for index in comm_index]
            celltexts_compare_with_std_remain = [celltexts[index] for index in diff_index if num_list[index] not in celltexts_compare_with_std_num]
            print('第一步还剩下：',celltexts_compare_with_std_remain)
            num_list_1 = sorted(compute_num_list(celltexts_compare_with_std, pattern))
            print('num_list_1',num_list_1)
            comp_1 = compare_num_list(num_list_1)
            print('comp_1',comp_1)
            if comp_1 == 1:
                return df_index_level.iloc[comm_index,:]
            else:
                #第三步：剩余部分与对照库进行比较,如果连续则返回标准库匹配结果+对照库匹配结果
                #如果不连续的话，则检查剩余部分中是否存在唯一性目录
                comm_index_comp, diff_index_comp,compare_index_name_remain = self.compare_with_std_comp(celltexts_compare_with_std_remain, pattern, fatherno, level)
                celltexts_compare_with_std_comp = [celltexts_compare_with_std_remain[index] for index in comm_index_comp]
                celltexts_compare_with_std_comp_num = [num_list[celltexts.index(celltexts_compare_with_std_remain[index])] for index in comm_index_comp]
                celltexts_compare_with_std_remain_comp = [celltexts_compare_with_std_remain[index] for index in diff_index_comp if num_list[celltexts.index(celltexts_compare_with_std_remain[index])] not in celltexts_compare_with_std_comp_num]

                print('第二步剩下的：{}'.format(celltexts_compare_with_std_remain_comp))
                if not celltexts_compare_with_std_comp :
                    comm_index_std_and_comp = comm_index
                else:
                    index_compare_with_std_comp = list(map(lambda x: celltexts.index(x), celltexts_compare_with_std_comp))
                    comm_index.extend(index_compare_with_std_comp)
                    comm_index_std_and_comp = sorted(comm_index)
                celltexts_compare_with_std_and_comp = [celltexts[index] for index in comm_index_std_and_comp]
                num_list_2 = sorted(compute_num_list(celltexts_compare_with_std_and_comp, pattern))
                comp_2 = compare_num_list(num_list_2)
                print('num_list_2',num_list_2)
                print('comp_2',comp_2)
                if comp_2 == 1:
                    return df_index_level.iloc[comm_index_std_and_comp, :]
                else:
                    #第四步：检查是否存在唯一性目录 取剩余的标准目录和剩余的标准对照目录，与剩下的唯一索引进行近似匹配
                    #如果匹配一致，则在标准对照目录中增加该对照信息，否则的话人工判断是否插入该
                    #信息到对照目录
                    single_indexes = []
                    duplicated_counter = Counter(num_list)
                    for k, v in duplicated_counter.items():
                        if v == 1:
                            single_indexes.append(num_list.index(k))
                    single_indextexts = [celltexts[i] for i in single_indexes]
                    #取剩下的索引与唯一索引的交集
                    single_indextexts_remain = list(set(single_indextexts) & set(celltexts_compare_with_std_remain_comp))
                    single_indextexts_remain_content = list(map(lambda x: pattern.match(x).groups()[1],list(single_indextexts_remain)))
                    print('单一索引内容：',single_indextexts_remain_content)

                    single_result = self.compare_similar_with_std_and_comp(
                        cellstexts=single_indextexts_remain,
                        origin_index_names_remain=origin_index_names_remain,
                        compare_index_name_remain=compare_index_name_remain,
                        pattern=pattern,
                        level=level,
                        fatherno=fatherno
                    )

                    comm_index_std_and_comp.extend(list(map(lambda x: celltexts.index(x), single_result)))
                    comm_index_std_and_comp_and_unique = sorted( comm_index_std_and_comp )
                    celltexts_compare_with_std_and_comp_and_unique = [celltexts[index] for index in comm_index_std_and_comp_and_unique]
                    num_list_3 = sorted(compute_num_list(celltexts_compare_with_std_and_comp_and_unique, pattern))
                    comp_3 = compare_num_list(num_list_3)
                    print('num_lis_3:',num_list_3)
                    print('comp_3:',comp_3)
                    if comp_3 == 1:
                        return df_index_level.iloc[comm_index_std_and_comp_and_unique, :]
                    else:
                        #第五步，剩余部分进行相似性检验，如果一致，则插入对照库，不一致，根据长度
                        #去除重复。
                        have_handled = celltexts_compare_with_std_and_comp
                        have_handled.extend(single_indextexts_remain)
                        remain_celltexts = set(celltexts).difference(set(have_handled))
                        remain_celltexts_content = list(map(lambda x: pattern.match(x).groups()[1],
                                                               list(remain_celltexts)))
                        remain_celltexts_content_new  = list(remain_celltexts)
                        remain_result = self.compare_similar_with_std_and_comp(
                            cellstexts=remain_celltexts_content_new,
                            origin_index_names_remain=origin_index_names_remain,
                            compare_index_name_remain=compare_index_name_remain,
                            pattern=pattern,
                            level=level,
                            fatherno=fatherno
                        )
                        comm_index_std_and_comp_and_unique.extend(list(map(lambda x: celltexts.index(x), remain_result)))
                        comm_index_std_and_comp_and_unique_and_remain = sorted(comm_index_std_and_comp_and_unique)
                        celltexts_compare_with_std_and_comp_and_unique_and_remain = [celltexts[index] for index in
                                                                          comm_index_std_and_comp_and_unique_and_remain]
                        num_list_4 = sorted(
                            compute_num_list(celltexts_compare_with_std_and_comp_and_unique_and_remain, pattern))
                        comp_4 = compare_num_list(num_list_4)
                        print('num_lis_4:', num_list_4)
                        print('comp_4:', comp_4)
                        if comp_4 == 1:
                            return df_index_level.iloc[comm_index_std_and_comp_and_unique_and_remain, :]
                        #第六步：去除重复后，将去除重复的数据增加到索引中
                        else:
                            result_df = df_index_level.iloc[comm_index_std_and_comp_and_unique_and_remain, :]
                            logger = logging.getLogger(__name__)
                            setup_logging()
                            logger.warning('{}{}索引不完整：{}'.format(self.code,self.accper,result_df.to_string()))
                            return result_df
                            # remain_celltexts_content_new!=None and len(remain_celltexts_content_new)>0:
                            # drop_duplicted_celltexts = self.drop_dumplicate_index_base_length(remain_celltexts_content_new, pattern)
                            # choice = input('是否增加到标准库{}'.format(drop_duplicted_celltexts))
                            # if choice == 'yes':
                            #     self.comput_new_index(drop_duplicted_celltexts, pattern, level, fatherno)
                            # else:
                            #     pass


    def drop_dumplicate_index_base_length(self,cellstexts,pattern):
        '''
        根据索引长度删除索引数据
        :param df_index_level:
        :param pattern:
        :return:
        '''
        print('去除重复前', cellstexts)
        num_list = compute_num_list(cellstexts,pattern)
        duplicated_item_index = {}
        duplicated_counter = Counter(num_list)
        for k, v in duplicated_counter.items():
            if v > 1:
                temp_list = [i for i in range(len(num_list) - 1, -1, -1) if num_list[i] == k]
                duplicated_item_index[k] = temp_list
        print(duplicated_item_index)
        if len(duplicated_item_index.keys()) > 0:
            min_indexs = []
            for k, values in duplicated_item_index.items():
                temp_comp = [len(cellstexts[v]) for v in values]
                min_temp_comp = min(temp_comp)
                min_temp_comp_index = temp_comp.index(min_temp_comp)
                min_indexs.append(min_temp_comp_index)
            drop_duplicated_celltexts = [cellstexts[index] for index in min_indexs]
            print('去除重复索引后返回')
            return drop_duplicated_celltexts
        else:
            raise NoIntegrityException

    def compare_with_std(self,celltexts,pattern,fatherno,level):
        '''
        与标准库进行比较,找出一致的项目，并对不一致的项目中与一致项目编号重复的项目予以删除。
        :param celltexts匹配到的索引名称列表
        :param pattern:匹配的正则表达式
        :param fatherno:父级索引
        :param level:层级
        :return:与标准库匹配的列表索引和不匹配的列表索引
        '''
        # 获取数据库中已经存储的标准索引信息
        origin_indexes = models.StdContentIndex.objects.filter(market=self.market,level=level, fatherno=fatherno)
        origin_index_names = [origin_index.name for origin_index in origin_indexes]
        indextext_contents = list(map(lambda x: pattern.match(x).groups()[1],celltexts))
        print(fatherno)
        print(origin_index_names)
        print(indextext_contents)
        # 检查索引与数据库中的标准信息的交集是否连续，连续的话则返回该连续的部分
        comm = set(indextext_contents) & set(origin_index_names)
        # diff = set(indextext_contents).difference(set(origin_index_names))
        comm_index = [indextext_contents.index(item) for item in comm]
        if indextext_contents.count('其他综合收益') == 2:
            other_com_income_id = []
            for i,v in enumerate(indextext_contents):
                if v == '其他综合收益':
                    other_com_income_id.append(i)
            comm_index.append(max(other_com_income_id))
        comm_index = sorted(comm_index)
        indextext_contents_indexes = [k for k,v in enumerate(indextext_contents)]
        diff_index = sorted(list(set(indextext_contents_indexes).difference(comm_index)))
        # diff_index = sorted([indextext_contents.index(item) for item in diff])
        origin_index_names_remain = set(origin_index_names).difference(indextext_contents)

        return comm_index,diff_index,origin_index_names_remain

    def compare_with_std_comp(self,celltexts,pattern,fatherno,level):
        '''
        比较剩余部分与对照数据库是否匹配，返回匹配的列表索引和不匹配的列表索引
        :param celltexts: 通过比较标准库剩余的索引字符串列表
        :param pattern: 正则表达式
        :param fatherno: 父索引
        :param level: 层级
        :return:
        '''
        indextext_contents = list(map(lambda x: pattern.match(x).groups()[1], celltexts))
        origin_indexes = models.StdContentIndex.objects.filter(market=self.market,level=level, fatherno=fatherno)
        all_compare_index_quereyset = [origin_index.stdcompareindex_set for origin_index in origin_indexes]
        all_compare_index_objects = []
        for qureyset in all_compare_index_quereyset:
            if qureyset.all():
                all_compare_index_objects.append(qureyset.all())

        all_compare_index_name = [compare_index_object[0].compare_name for compare_index_object in (compare_index_object_all for compare_index_object_all \
                                  in all_compare_index_objects)]
        print(all_compare_index_name)
        comm = set(indextext_contents) & set(all_compare_index_name)
        # diff = set(indextext_contents).difference(set(all_compare_index_name))
        comm_index = sorted([indextext_contents.index(item) for item in comm])
        comm_index = sorted(comm_index)
        indextext_contents_indexes = [k for k, v in enumerate(indextext_contents)]
        diff_index = sorted(list(set(indextext_contents_indexes).difference(comm_index)))
        # diff_index = sorted([indextext_contents.index(item) for item in diff])
        compare_index_name_remain = set(all_compare_index_name).difference(set(indextext_contents))
        return comm_index, diff_index,compare_index_name_remain

    def compare_similar_with_std_and_comp(self,cellstexts,origin_index_names_remain,compare_index_name_remain,pattern,level,fatherno):
        logger = logging.getLogger(__name__)
        setup_logging()
        indextexts_content = list(map(lambda x: pattern.match(x).groups()[1], cellstexts))
        cell_texts_dict = dict(zip(indextexts_content,cellstexts))
        temp = indextexts_content[:]
        print('相似性检验项目：',indextexts_content)
        for single_index in indextexts_content:
            similar_std_index = mytools.similar_item_with_list(single_index, origin_index_names_remain)
            if similar_std_index != None:
                if len(models.StdCompareIndex.objects.filter(market=self.market,fatherno=fatherno,compare_name=single_index))>0:
                    continue
                # choice = input('增加{}到对照库：'.format(single_index, ))
                choice = 'yes'
                if choice == 'yes':
                    index_name_id = \
                    models.StdContentIndex.objects.filter(market=self.market, level=level, fatherno=fatherno,
                                                          name=similar_std_index)[0].id
                    self.add_compare_index(self.market,single_index,fatherno,index_name_id)

                # temp.remove(single_index)
            else:
                similar_std_index_comp = mytools.similar_item_with_list(single_index, compare_index_name_remain)
                if similar_std_index_comp != None:
                    # choice = input('增加{}到对照库：'.format(single_index))
                    choice = 'yes'
                    if choice == 'yes':
                        index_name_id = \
                        models.StdCompareIndex.objects.filter(market=self.market,fatherno=fatherno, compare_name=similar_std_index_comp)[
                            0].index_name_id
                        self.add_compare_index(self.market, single_index,fatherno, index_name_id)
                    # temp.remove(single_index)
                else:
                    # choice = input('是否增加到标准库{}'.format(single_index))
                    choice = 'no'
                    if choice == 'yes':
                        self.comput_new_index([cellstexts[indextexts_content.index(single_index)], ], pattern, level, fatherno)
                        # temp.remove(single_index)
                    else:
                        logger.warning('{}{}的{}没有被增加到标准库中'.format(self.code, self.accper, single_index))
                        # choice1 = input('是否增加到对照库{}'.format(single_index))
                        choice1 = 'no'
                        if choice1 == 'yes':
                            index_name_id = input('请输入对照索引的id')
                            self.add_compare_index(self.market,single_index,fatherno,index_name_id)
                            # temp.remove(single_index)
                        else:
                            logger.warning('{}{}的{}没有被增加到对照库中'.format(self.code,self.accper,single_index))
                            temp.remove(single_index)
        if len(temp) == 0:
            return []
        else:
            return [cell_texts_dict[item] for item in temp]

    def add_compare_index(self,market,compare_name,fatherno,index_name_id):
        models.StdCompareIndex.objects.create(
            market=market,
            compare_name=compare_name,
            fatherno=fatherno,
            index_name_id=index_name_id
        )


    def comput_new_index(self,cellstexts,pattern,level,fatherno):
        '''
        新增索引，并自动排序
        #第一步：计算需要新增的内容
        #第二步：计算新增内容的编号
        #第三步：计算新增内容的父级id
        :return:
        '''
        logger = logging.getLogger(__name__)
        setup_logging()
        #第一步
        #获取数据库中已经存储的标准索引信息
        origin_index_df = models.StdContentIndex.objects.filter(market=self.market,level=level,fatherno=fatherno)
        #已经存储的索引名称
        origin_index_name = [origin_index.name for origin_index in origin_index_df]
        origin_index_no_name = [origin_index.no_name for origin_index in origin_index_df]
        #获取新的索引内容
        # index_content_list = list(df_index_level.cellText.map(lambda x: pattern.match(x).groups()[1]))
        # if 'index_content' not in df_index_level.columns:
        #     df_index_level['index_content'] = index_content_list
            # df_index_level.insert(len(df_index_level.columns),'index_content',index_content_list)
        # df_index_level.loc[:,'index_content'] =
        new_no_name = cellstexts
        new_index_name = list(map(lambda x: pattern.match(x).groups()[1],cellstexts))
        #需要新增的内容
        add_index_name = list(set(new_index_name).difference(set(origin_index_name)))
        del_index_name = []
        if len(add_index_name)>0:
            #检查索引是否近似相等
            for add_name in add_index_name:
                for i,origin_name in enumerate(origin_index_name):
                    if mytools.similar(origin_name, add_name):

                        origin_obj_id = models.StdContentIndex.objects.filter(market=self.market,level=level,fatherno=fatherno,name=origin_name)[0].id
                        if not models.StdCompareIndex.objects.filter(market=self.market,fatherno=fatherno,compare_name=add_name):
                            # choice = input('是否新增近似{}索引{}'.format(add_name,origin_name))
                            choice = 'yes'
                            if choice == 'yes':
                                self.add_compare_index(self.market,add_name,fatherno,origin_obj_id)
                        # df_index_level.loc[df_index_level.index_content==add_name].cellText=origin_index_no_name[i]
                        del_index_name.append(add_name)
            add_index_name = list(set(add_index_name).difference(set(del_index_name)))

        if add_index_name!=None and len(add_index_name)>0:
            #按照新增内容的顺序排列
            add_index_name.sort(key=lambda x:new_index_name.index(x))
            print('计划新增索引',add_index_name)
            # 第二步
            # 计算新增内容的编号
            # 1、读取数据库中该级别的最后一个编号
            temp_df = [obj.no for obj in origin_index_df]

            if self.market == 'sh':
                selfnos,whole_num_fixed_length = comput_no(temp_df,level,add_index_name,fatherno,num_len=10)
            elif self.market ==  'sz':
                selfnos, whole_num_fixed_length = comput_no(temp_df, level, add_index_name, fatherno, num_len=8)
            else:
                raise Exception
            names = add_index_name
            no_names = [new_no_name[new_index_name.index(name)] for name in names]

            for name,no_name,selfno,no in zip(names,no_names,selfnos,whole_num_fixed_length):
                print(name,no_name,fatherno,selfno,no)
                if models.StdContentIndex.objects.filter(market=self.market, no=no) or \
                    models.StdCompareIndex.objects.filter(market=self.market, compare_name=name,
                                                          fatherno=fatherno):

                    continue
                else:
                    # choice = input('是否输入下列信息到标准库：{}'.format(name))
                    choice = 'no'
                    if choice == 'yes':
                        models.StdContentIndex.objects.create(
                            market=self.market,
                            name=name,
                            no_name=no_name,
                            fatherno=fatherno,
                            level=level,
                            selfno=selfno,
                            no=no,
                            has_child='1'
                        )
                    else:
                        logger.info('{}{}的{}没有被增加到标准库中'.format(self.code, self.accper, ','.join(names)))
                        # choice = input('是否输入下列信息到对照库：{}'.format(name))
                        choice = 'no'
                        if choice == 'yes':
                            index_name_id = input('请输入{}标准库对应索引id:'.format(name))
                            self.add_compare_index(market=self.market,compare_name=name,fatherno=fatherno,index_name_id=index_name_id)
                        else:
                            logger.info('{}{}的{}没有被增加到对照库中'.format(self.code, self.accper, ','.join(names)))
        else:
            pass



def get_std_dir_sh():
    objs = models.StdContentIndex.objects.filter(market='sh')
    objs.delete()
    path = r'H:\data_extract\utils\stdcom1.xlsx'
    io = open(path, 'rb')
    df = pd.read_excel(io, sheetname='Sheet2')
    new_df = pd.DataFrame()
    new_df['id'] = list(df.id)
    new_df['cellText'] = list(df.no_name)
    filepath = r'H:\data_extract\report\shanghai\sh_600312_20171231.html'
    file = HtmlFile(filepath)
    file.parse_all_dir(new_df)

    objs = models.StdContentIndex.objects.filter(market='sh')
    fathernos = [obj.fatherno for obj in objs]
    for obj in objs:
        sts = str(obj.fatherno) + str(obj.selfno)
        print(sts)
        if sts in fathernos:
            pass
        else:
            obj.has_child = '0'
            obj.save()



