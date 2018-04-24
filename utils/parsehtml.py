# _author : litufu
# date : 2018/4/7
from bs4 import BeautifulSoup
import pandas as pd
import re
from collections import OrderedDict
from utils.tools import del_same_item_from_list,check_if_pure_digital
from itertools import chain

class NotFoundLongestRowException(Exception):
    def __init__(self,err='未在表格中发现最大的行'):
        Exception.__init__(self,err)


class HtmlFile(object):
    '''
    流程：

    '''

    def __init__(self,filepath):
        '''

        :param filepath: 文件路径地址
        '''
        #网页文件
        self.soup = BeautifulSoup(open(filepath,'r',encoding='utf-8'),'lxml')
        #所有的页文件
        self.pfs =  self.soup.find_all(id=re.compile('pf'))
        self.pageCount =  len(self.pfs)
        self.pageId =  [pf['id'] for pf in self.pfs]
        self.page_contents_base_pgid = OrderedDict(zip(self.pageId,self.pfs))
        self.page_contents_base_pgCount = OrderedDict(zip(range(1,self.pageCount+1),self.pfs))

        #文件的所有内容
        self.file_content = []
        # 文件中所有的表格单元格列表
        self.file_page_tables = self.get_all_page_tables()
        self.spreed_file_tables = self.spreed_all_page_tables()
        self.cells_text_dict = self.get_file_cells_text()
        self.cells_text_keys = list(self.cells_text_dict.keys())







    def dirlist(self,root,layer=0,fatherid='00_'):
        '''递归遍历目录树,生成对应的编码:父级编码+父级编码+...+当前编码'''
        layer = layer+1
        ul = root.find('ul')
        for k,child in enumerate(ul.children):
            if child.find('ul'):
                print('父级编码', fatherid, end=' ')
                print('层次编码', layer, end=' ')
                print('序列编号：', k, end=' ')
                print(child.a.get_text())
                self.dirlist(child,layer=layer,fatherid=fatherid + '{}_'.format(k))
            else:
                print('父级编码',fatherid,end= ' ')
                print('层次编码',layer,end=' ')
                print('序列编号：',k,end=' ')
                print(child.get_text())




    def get_file_content(self):
        '''
            将文件所有的cells传入，生成文件全部content:
            :return: self.filecontent
            '''
        for i in range(1,self.pageCount+1):
            page = HtmlPage(self,pgNum=i)
            self.file_content.append(page.pgContent)
        return self.file_content

    def get_file_cells_text(self):
        file_cells_text_dict = OrderedDict()
        for k,page in enumerate(self.get_file_content()):
            for cell in page:
                file_cells_text_dict[str(k)+'_'+'_'.join(cell['class'])] = re.sub('\s+','',cell.get_text())
        return file_cells_text_dict


    def get_all_page_tables(self):
        file_page_tables = []
        for i in range(1,self.pageCount+1):
            page = HtmlPage(self,pgNum=i)
            if page.pgHaveTableNum > 0:
                file_page_tables.append(page.pg_fill_merge_tables)
            else:
                file_page_tables.append([])
        return file_page_tables

    def spreed_all_page_tables(self):
        for i in range(1,self.pageCount+1):
            page = HtmlPage(self,i)
            if page.pgHaveTableNum > 0:
                if self.is_spreedsheet(i):
                    for k in range(i,0,-1):
                        if len(self.file_page_tables[k-1]) >0:
                            self.spreedtable(k,i+1)
                            break
                        else:
                            continue
        return self.file_page_tables

    def is_spreedsheet(self,pgnum):
        '''
                判断是否需要连表
                :param pgNum:
                :return:
                '''
        current_page = HtmlPage(self, pgnum)
        if pgnum+1 <= self.pageCount:
            next_page = HtmlPage(self, (pgnum + 1))
        else:
            return False


        # 如果当前页的最后一行内容存在class_='c'
        if current_page.pgContent[-1].has_attr('class') and current_page.pgContent[-1].attrs['class'][0] == 'c':
            # 如果下一页的第一行也是class='c'
            if next_page.pgContent[0].has_attr('class') and next_page.pgContent[0].attrs['class'][0] == 'c':
                # 求当前页最后一个表格信息
                # 如果两个坐标一致，则将两个表格连接起来
                # 最后一个表格所有的单元格
                current_page_tables = current_page.pg_ordered_table_list
                current_page_last_table = current_page_tables[-1]
                last_line_x = [cell.attrs['class'][1] for cell in current_page_last_table[-1]]
                # 获取下一页第一个表的信息
                # 第一个表格所有的单元格
                next_page_tables = next_page.pg_ordered_table_list
                next_page_first_table = next_page_tables[0]
                first_line_x = [cell.attrs['class'][1] for cell in next_page_first_table[0]]

                if last_line_x == first_line_x:
                    return True
        return False

    def spreedtable(self,currentPageNum,nextPageNum):
        current_page_last_table = self.file_page_tables[currentPageNum-1][-1]
        next_page_first_table = self.file_page_tables[nextPageNum-1][0]
        current_page_last_table.extend(next_page_first_table)
        self.file_page_tables[nextPageNum - 1].pop(0)

    def spreedsheet(self,pgnum,next_pgnum):
        '''
        废弃
        :param pgNum:
        :return:
        '''
        current_page = HtmlPage(self,pgnum)
        # 最后一个表格所有的单元格
        current_page_tables = current_page.pg_fill_merge_tables
        current_page_last_table = current_page_tables[-1]
        last_line_x = [cell.attrs['class'][1] for cell in current_page_last_table[-1]]
        # 获取下一页第一个表的信息
        # 第一个表格所有的单元格
        next_page = HtmlPage(self,(next_pgnum))
        next_page_tables = next_page.pg_fill_merge_tables
        next_page_first_table = next_page_tables[0]
        first_line_x = [cell.attrs['class'][1] for cell in next_page_first_table[0]]

        #如果当前页的最后一行内容存在class_='c'
        if current_page.pgContent[-1].has_attr('class') and current_page.pgContent[-1].attrs['class'][0] == 'c':
            #如果下一页的第一行也是class='c'
            if next_page.pgContent[0].has_attr('class') and next_page.pgContent[0].attrs['class'][0] == 'c':
                # 求当前页最后一个表格信息
                # 如果两个坐标一致，则将两个表格连接起来
                if last_line_x == first_line_x:
                    next_page_tables.pop(0)
                    current_page_last_table.extend(next_page_first_table)
        return current_page_tables,next_page_tables

    def get_table_previous_text_2(self,table):
        table_in_paId = table[0][0].find_parent('div',class_=re.compile('pf'))['id']
        pgnum = self.pageId.index(table_in_paId)
        cell_index = str(pgnum) + ''.join(table[0][0]['class'])
        first_cell_index = self.cells_text_keys.index(cell_index)
        if first_cell_index>3:
            pre_3_content = self.cells_text_keys[first_cell_index-3:first_cell_index]
            return ''.join([self.cells_text_dict[cell] for cell in pre_3_content])
        elif first_cell_index>2:
            pre_2_content = self.cells_text_keys[first_cell_index - 2:first_cell_index]
            return ''.join([self.cells_text_dict[cell] for cell in pre_2_content])
        elif first_cell_index>1:
            pre_1_content = self.cells_text_keys[first_cell_index - 1:first_cell_index]
            return ''.join([self.cells_text_dict[cell] for cell in pre_1_content])
        else:
            return '没有发现'

    def get_all_table_previous_text_2(self):
        temp_file_pre_texts = []
        for pg_tables in self.spreed_file_tables:
            temp_page_pre_texts = []
            for table in pg_tables:
                pre_text = self.get_table_previous_text_2(table)
                temp_page_pre_texts.append(pre_text)
            temp_file_pre_texts.append(temp_page_pre_texts[:])
        return temp_file_pre_texts

    def get_table_previous_text_1(self,table):
        table_first_cell = table[0][0]
        file_content = self.get_file_content()
        first_cell_index = file_content.index(table_first_cell)
        if first_cell_index>3:
            pre_3_content = file_content[first_cell_index-3:first_cell_index]
            return ''.join([cell.get_text() for cell in pre_3_content])
        elif first_cell_index>2:
            pre_2_content = file_content[first_cell_index - 2:first_cell_index]
            return ''.join([cell.get_text() for cell in pre_2_content])
        elif first_cell_index>1:
            pre_1_content = file_content[first_cell_index - 1:first_cell_index]
            return ''.join([cell.get_text() for cell in pre_1_content])
        else:
            return '没有发现'

    def get_all_table_previous_text(self):
        temp_file_pre_texts = []
        for pg_tables in self.spreed_file_tables:
            temp_page_pre_texts = []
            for table in pg_tables:
                pre_text = self.get_table_previous_text_1(table)
                temp_page_pre_texts.append(pre_text)
            temp_file_pre_texts.append(temp_page_pre_texts[:])
        return temp_file_pre_texts

    def create_html_table(self,table):
        '''
        #为表格添加table,td,tr等html形式元素
        :param table: orderedtable
        :return:Beautifulsoup(table节点对象）
        '''
        html_table = self.soup.new_tag('table')
        for line in table:
            tr = self.soup.new_tag('tr')
            for cell in line:
                new_td = cell.wrap(self.soup.new_tag('td'))
                tr.append(BeautifulSoup(str(new_td), 'lxml').find('td'))  # 不能直接append td，否则会出现浅拷贝情况
            html_table.append(BeautifulSoup(str(tr), 'lxml').find('tr'))  # 不能直接append tr，否则会出现浅拷贝情况
        return html_table

    def create_file_table_soup(self):
        table_soup = BeautifulSoup('<html></html>', 'lxml')
        for pg_tables in self.spreed_file_tables:
            for table in pg_tables:
                html_table = self.create_html_table(table)
                table_soup.append(html_table)
        return table_soup

class HtmlPage(object):

    def __init__(self,file,pgNum):
        self.file = file
        self.pgNum = pgNum
        self.pgContent = self.get_page_content()
        self.pgHaveTableNum = len(self.get_tables_cells())
        self.pg_tables_cells_dict = OrderedDict(zip(range(1, self.pgHaveTableNum + 1), \
                                                 [self.create_cells_dict(table_cells) for table_cells in\
                                                  self.get_tables_cells()])) if self.pgHaveTableNum>0 else None
        self.pg_ordered_table_list =self.create_pg_ordered_table_cells_list() if self.pgHaveTableNum>0 else None
        self.pg_split_tables = self.create_pg_split_table_list() if self.pgHaveTableNum>0 else None
        self.pg_fill_merge_tables = self.create_pg_fill_merge_tables() if self.pgHaveTableNum>0 else None

    def get_origin_page_num(self):
        '''
        #获取文件原来的页码
        :return:

        '''
        pf = self.file.page_contents_base_pgCount[self.pgNum]
        pc = pf.find(class_='pc')
        img = pc.img

        title = re.sub('\s+','',img.next_sibling.get_text())
        origin_page_number = re.sub('\s+','',img.next_sibling.next_sibling.get_text())
        return title,origin_page_number

    def get_page_content(self):
        '''
        获取当前页面的内容
        :param pf: pf = soup.find(id=re.compile('pf'))
        :return: 列表格式pc = pf.find(class_='pc').childern
        '''
        pf = self.file.page_contents_base_pgCount[self.pgNum]
        pc = pf.find(class_='pc')
        # 删除没有内容的标签，前3个div(包括页眉、页脚和空行）
        # ,如果是竖向的话为y1,y2,y3如果是横向的话变为h2,h3,h4，
        class_attrs = ['y1','y2','y3','h2','h3','h4']
        tag_names = ['img']
        for class_attr in class_attrs:
            tag = pc.find(class_=class_attr)
            if tag:
                tag.decompose()

        for tag_name in tag_names:
            tag = pc.find(tag_name)
            if tag:
                tag.decompose()

        # 查找pc所有的子元素
        # 获取当前页的pc_children,并删除换行符
        page_content = del_same_item_from_list(list(pc.children), '\n')
        return page_content

    def get_tables_cells(self):
        '''
        将表格元素从所有元素中抽取出来。
        原理：表格与表格中间存在非表格元素：
                    表格单元格html元素的属性class为以’c'开头的div
                    非表格html元素的属性class为以’t'开头的div
                    把文件元素中所有相连的c组成列表放在一起即为一个表格所有的单元格，如果出现非表格html元素，
                    说明表格结束。
            根据传入的所有div(class_='pc')下的children,生成tablecells:
            # [[table1.cell1,table1.cell2],[table2.cell1,table2.cell2]...]
            :param content: 包含div列表，可以是一页的page_content,也可以是全部的file_content
            :return: 传入数据可以生成的表格
            '''
        content = self.get_page_content()
        tables_cells = []  # [[table1.cell1,table1.cell2],[table2.cell1,table2.cell2]...]
        # 定义的临时表格，用于存放一个表格的所有单元格
        temp = []
        # 遍历所有的子元素
        for cell in content:
            # 判断元素是否为div

            if cell.name == 'div':
                # 判断是否有class属性，判断第一个属性是否为'c'
                if cell.has_attr('class') and cell.attrs['class'][0] == 'c':
                    temp.append(cell)
                # 如果已经不是单元格了，说明表格已经中断，将temp储存到结果中，并清空temp
                else:
                    if len(temp) > 0:
                        tables_cells.append(temp[:])
                        temp = []
                    else:
                        pass
            else:
                pass
        if len(temp) > 0:
            tables_cells.append(temp[:])
        return tables_cells

    def create_cells_dict(self, table_cells):
        '''
        获取单个表格的单元格所对应的坐标位置
        :param table: cells list
        :return: cells_dict:格式如下：
        {('x16', 'y85', 'w17', 'h1d')：cell1，('x28', 'y88', 'w18', 'h14')：cell2,\
        ('x29', 'y88', 'w19', 'h14'):cell3,('x28', 'y89', 'w18', 'h14'):cell4...}
        '''
        cells_dict = OrderedDict()
        for cell in table_cells:
            cells_dict[tuple(cell.attrs['class'][1:])] = cell
        return cells_dict

    def create_pg_ordered_table_cells_list(self):
        pg_tables = []
        for i in self.pg_tables_cells_dict:
            table = HtmlTable(self.pg_tables_cells_dict[i]).ordered_table_cells
            pg_tables.append(table[:])
        return pg_tables

    def create_pg_split_table_list(self):
        pg_tables = []
        for i in self.pg_tables_cells_dict:
            table = HtmlTable(self.pg_tables_cells_dict[i]).split_tables
            pg_tables.extend(table[:])
        return pg_tables

    def create_pg_fill_merge_tables(self):
        pg_tables = []
        for i in self.pg_tables_cells_dict:
            table = HtmlTable(self.pg_tables_cells_dict[i]).fill_merge_cells_table
            pg_tables.extend(table[:])
        return pg_tables

class HtmlTable(object):

    def __init__(self,table_cells_dict):
        self.table_cells_dict = table_cells_dict
        self.longest_row_x = self.get_longest_row_x()
        self.ordered_table = self.order_table_cell_by_longest_row() if self.longest_row_x != None \
            else self.order_table_cell_by_experience()
        self.ordered_table_cells = self.get_ordered_table_cells()
        self.split_or_not = self.need_splittable_or_not()
        self.split_tables = self.splittable()
        self.fill_merge_cells_table =[self.fill_merge_cells(table) for table in self.split_tables]

    def get_longest_row_x(self):
        '''
        获取表格中最长的行对应的x索引
        根据各单元格的x坐标确认表格有多少列，然后从表格起始位置x向后数表格对应的列数，
        如果没有重复值，则该序列为表格所有列所对应的位置
        :param table: cells list
        :return: 表格各列对应的x坐标[x1,x2,x3]
        '''
        table_cells_pos_x = [cell_pos[0] for cell_pos in self.table_cells_dict.keys()]
        columns = set(table_cells_pos_x)
        col_len = len(columns)
        test_cell_items = table_cells_pos_x[:]
        # 求各列数的位置
        first_item = table_cells_pos_x[0]
        while True:
            try:
                num = test_cell_items.index(first_item)
                if len(set(test_cell_items[num:col_len])) == col_len:
                    return test_cell_items[num:col_len]
                else:
                    test_cell_items.remove(first_item)
                    if first_item in test_cell_items:
                        start_num = test_cell_items.index(first_item)
                        test_cell_items = test_cell_items[start_num:]
                    else:
                        return None
                        # print('101:没有找到最长的行,该表格所在的页码是{}'.format(self.get_table_page_num(table)))
                        # raise NotFoundLongestRowException
            except Exception as e:
                # print('101:没有找到最长的行,该表格所在的页码是{}'.format(self.get_table_page_num(table)))
                raise None

    def order_table_cell_by_longest_row(self):
        '''

        :return: 按照最长行排序后的所有单元格坐标信息
        '''
        # 零散的单元格信息
        cell_items = [td for td in self.table_cells_dict]
        # 按照信息最全的行排列零散的单元格信息，做成初始表格
        ordered_table = []
        # 代表一行数据
        tr = []
        for i in range(len(cell_items)):
            if i == 0:
                tr.append(cell_items[0])
            else:
                if self.longest_row_x.index(cell_items[i][0]) > self.longest_row_x.index(cell_items[i - 1][0]):
                    tr.append(cell_items[i])
                else:
                    ordered_table.append(tr[:])
                    tr = []
                    tr.append(cell_items[i])
        if len(tr)>0:
            ordered_table.append(tr[:])
        return ordered_table

    def order_table_cell_by_experience(self):

        # 零散的单元格信息
        cell_items = [td for td in self.table_cells_dict]
        # 按照信息最全的行排列零散的单元格信息，做成初始表格
        ordered_table = []
        # 代表一行数据
        tr = []
        tr_set = set()
        first_cell_x = cell_items[0][0]
        for cell in cell_items:
            if cell[0] == first_cell_x:
                if len(tr)>0:
                    ordered_table.append(tr[:])
                    tr = []
                    tr_set = set()
                    tr.append(cell)
                    tr_set.add(cell[0])
                else:
                    tr_set = set()
                    tr.append(cell)
                    tr_set.add(cell[0])
            else:
                if cell[0] not in tr_set:
                    tr.append(cell)
                    tr_set.add(cell[0])
                elif cell[0] in tr_set:
                    ordered_table.append(tr[:])
                    tr = []
                    tr_set = set()
                    tr.append(cell)
                    tr_set.add(cell[0])
        if len(tr)>0:
            ordered_table.append(tr[:])
        return ordered_table

    def get_ordered_table_cells(self):
        table_cells = []
        for tr_pos in self.ordered_table:
            tr_cells = []
            for td_pos in tr_pos:
                td = self.table_cells_dict[td_pos]
                tr_cells.append(td)
            table_cells.append(tr_cells[:])
        return table_cells

    def need_splittable_or_not(self):
        row_length = [len(tr) for tr in self.ordered_table_cells]
        row_have_1_cell = [i for i, length in enumerate(row_length) if length == 1]
        columns_max_length = max(row_length)
        if self.longest_row_x == None:
            return True
        elif columns_max_length > 1 and len(row_have_1_cell)>=1:
            return True
        else:
            return False

    def splittable(self):
        '''
        将表格进行拆分
        :param table:
        #第一种情况：如果有一行，占满了所有的列
        #第二种情况：如果一行全部为空白内容
        如果下一行中存在纯数字，则直接删除该行
        如果下一行不存在纯数字，则分成两个表
        :return:[[table1],[table2]...]
        '''
        #取得每一行的长度
        after_splite_table = self.ordered_table_cells[:]
        row_length = [len(tr) for tr in self.ordered_table_cells]
        #检查是否存在一行只有一个单元格的情况,求出该行的索引
        row_have_1_cell = [i for i,length in enumerate(row_length) if length==1]
        columns_max_length = max(row_length)
        temp_tables = []
        temp = []
        if columns_max_length > 1 and len(row_have_1_cell)>=1:
            for i in row_have_1_cell:
                if i+1 <len(self.ordered_table_cells):
                    next_row = self.ordered_table_cells[i+1]
                    if self.check_row_have_pure_digital(next_row):
                        after_splite_table[i] = 0
                    else:
                        after_splite_table[i] = 1
                else:
                    after_splite_table[i] = 0
            for tr in after_splite_table:
                if tr == 1:
                    if len(temp)>0:
                        temp_tables.append(temp[:])
                        temp = []
                elif tr==0:
                    pass
                else:
                    temp.append(tr[:])
            if len(temp)>0:
                temp_tables.append(temp[:])
            return temp_tables
        else:
            return [after_splite_table]

    def check_row_have_pure_digital(self,row):
        #判断该行是否存在纯数字的单元格
        for cell in row:
            if check_if_pure_digital(re.sub('\s+','',cell.get_text())):
                return True
        return False

    def fill_merge_cells(self,table):
        '''
        返回表格所有单元格的坐标信息，对于合并单元格采用先向下填充，再向左填充的方法，确保所有的行拥有相同的列数
        :return: table 将同一行的单元格放在一个列表，将行按照顺序添加到table中：格式如下
        [[cell1, cell2, cell3], \
        [ [cell4, cell5, 'cell6]
        ...
        ]
        '''
        # 计算所有行的单元格数量
        line_lengths = [len(line) for line in table]
        # 找出最大行所有的单元格
        maxlength = max(line_lengths)
        # 找出拥有最多单元格所在的行数
        max_len_row_in_line = line_lengths.index(maxlength)
        # 找到最大的单元格所在的行
        max_tr = table[max_len_row_in_line]

        # 单元格向下填充
        for i, tr in enumerate(table):
            # 如果已经拥有与最长行相同的单元格数量则跳过
            if len(tr) == maxlength:
                pass
            else:
                if i == 0:
                    pass
                else:
                    # 根据上一行向下填充
                    pre_row = table[i - 1]
                    now_row = tr
                    pre_row_col = [td.attrs['class'][1] for td in pre_row]
                    now_row_col = [td.attrs['class'][1] for td in now_row]
                    pre_row_set_col = set(pre_row_col)
                    now_row_set_col = set(now_row_col)
                    pre_now_diff = pre_row_set_col.difference(now_row_set_col)
                    for x in pre_now_diff:
                        diff_col_num = pre_row_col.index(x)
                        now_row.insert(diff_col_num, pre_row[diff_col_num])

        # 单元格想左填充
        for i, tr in enumerate(table):
            # 如果已经是最大行跳过
            if len(tr) == maxlength:
                pass
            else:
                # 最大行
                max_row = max_tr
                # 现在循环行
                now_row = tr
                # 最大行所有的单元格
                max_row_col = [td.attrs['class'][1] for td in max_row]
                # 现在行所有的单元格
                now_row_col = [td.attrs['class'][1] for td in now_row]
                # 最大航所有的单元格转换为set便于求差集
                max_row_set_col = set(max_row_col)
                # 现在行所有的单元格转换为set便于求差集
                now_row_set_col = set(now_row_col)
                # 求最大行与现在行的单元格差集
                max_now_diff_set = max_row_set_col.difference(now_row_set_col)
                # 将差集按照max_row原来的顺序排列
                max_now_diff_list = list(max_now_diff_set)
                sorted_max_now_diff_list = sorted(max_now_diff_list, key=lambda x: max_row_col.index(x))
                # 遍历已经排序的差集单元格
                for x in sorted_max_now_diff_list:
                    # 求差的单元格所在的行数
                    diff_col_num = max_row_col.index(x)
                    # 在当前单元格的中相差的行数插入前一个单元格的内容
                    now_row.insert(diff_col_num, now_row[diff_col_num - 1])

        return  table

    def get_table_page_num(self,table):
        '''
        获取当前表格所在的页码
        :param table: ordered_table
        :return: pg_id
        '''
        #获取表格所在页面的页码
        return  table[0][0].find_parent('div',id=re.compile('pf')).attrs('id')








if __name__ == '__main__':
    obj = HtmlFile('t.html')
    table_soup = obj.create_file_table_soup()
    dfs = pd.read_html(str(table_soup))
    for df in dfs:
        print(df)
    # print(table_soup)
    print('------------------')
    # print(obj.page_contents_base_pgnum)