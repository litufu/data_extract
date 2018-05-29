# _author : litufu
# date : 2018/4/18

import re
from bs4 import BeautifulSoup
from collections import OrderedDict
from utils.mytools import check_if_pure_digital,is_num
import re

class HtmlTable(object):

    def __init__(self,table_cells):
        self.table_cells = table_cells
        self.table_cells_dict = self.create_cells_dict(table_cells)
        self.table_cells_dict_keys = [item[0] for item in self.table_cells_dict]
        self.longest_row_x = self.get_longest_row_x()
        self.longest_row_w = self.get_longest_row_w()
        self.ordered_table = self.order_table_cell_by_longest_row() if self.longest_row_x != None \
            else self.order_table_cell_by_experience()
        # self.ordered_table = self.order_table_cell_by_experience()
        self.ordered_table_cells = self.get_ordered_table_cells()
        self.split_or_not = self.need_splittable_or_not()
        self.split_tables = self.splitAndCombine()
        # self.split_tables = self.splittable()
        self.fill_merge_cells_table = self.get_fill_merge_cells_table()

    def get_fill_merge_cells_table(self):
        ret = []
        for table in self.split_tables:
            if isinstance(table,tuple):
                ret.append(table)
            else:
                if True in [is_num(re.sub('\s+','',cell.get_text())) for tr in table for cell in tr]:
                    ret.append(self.fill_merge_cells(table))
                else:
                    ret.append(table)
        return ret

    def get_cell_by_pos(self,pos):
        for item,value in self.table_cells_dict:
            if item == pos:
                return value

    def create_cells_dict(self, table_cells):
        '''
        获取单个表格的单元格所对应的坐标位置
        :param table: cells list
        :return: cells_dict:格式如下：
        {('x16', 'y85', 'w17', 'h1d')：cell1，('x28', 'y88', 'w18', 'h14')：cell2,\
        ('x29', 'y88', 'w19', 'h14'):cell3,('x28', 'y89', 'w18', 'h14'):cell4...}
        '''
        # cells_dict = OrderedDict()
        # for cell in table_cells:
        #     cells_dict[tuple(cell.attrs['class'][1:])] = cell
        # return cells_dict

        cells_dict = []
        for cell in table_cells:
            pg = cell.parent.parent['id']
            pos = cell.attrs['class'][1:]
            pos.append(pg)
            cells_dict.append((tuple(pos),cell))
        return cells_dict


    def get_longest_row_x(self):
        '''
        获取表格中最长的行对应的x索引
        根据各单元格的x坐标确认表格有多少列，然后从表格起始位置x向后数表格对应的列数，
        如果没有重复值，则该序列为表格所有列所对应的位置
        :param table: cells list
        :return: 表格各列对应的x坐标[x1,x2,x3]
        '''
        table_cells_pos_x = [cell_pos[0] for cell_pos in self.table_cells_dict_keys]
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

    def get_longest_row_w(self):
        '''
        根据表格中最长的行对应的x索引，获取w索引
        :param table: cells list
        :return: 表格各列对应的x坐标[w1,w2,w3]
        '''
        table_cells_pos_x = [cell_pos[0] for cell_pos in self.table_cells_dict_keys]
        table_cells_pos_w = [cell_pos[2] for cell_pos in self.table_cells_dict_keys]
        columns = set(table_cells_pos_x)
        col_len = len(columns)
        test_cell_items = table_cells_pos_x[:]
        # 求各列数的位置
        first_item = table_cells_pos_x[0]
        while True:
            try:
                num = test_cell_items.index(first_item)
                if len(set(test_cell_items[num:col_len])) == col_len:
                    return table_cells_pos_w[num:col_len]
                else:
                    test_cell_items.remove(first_item)
                    table_cells_pos_w.pop(num)
                    if first_item in test_cell_items:
                        start_num = test_cell_items.index(first_item)
                        test_cell_items = test_cell_items[start_num:]
                        table_cells_pos_w = table_cells_pos_w[start_num:]
                    else:
                        # print('没有找到最长的行')
                        # print(self.table_cells)
                        return None
                        # print('101:没有找到最长的行,该表格所在的页码是{}'.format(self.get_table_page_num(table)))
                        # raise NotFoundLongestRowException
            except Exception as e:
                # print('101:没有找到最长的行,该表格所在的页码是{}'.format(self.get_table_page_num(table)))
                raise Exception

    def order_table_cell_by_longest_row(self):
        '''

        :return: 按照最长行排序后的所有单元格坐标信息
        '''
        # 零散的单元格信息
        cell_items = [td for td in self.table_cells_dict_keys]
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
        cell_items = [td for td in self.table_cells_dict_keys]
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
                td = self.get_cell_by_pos(td_pos)
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
                        after_splite_table[i] = 1
                    else:
                        after_splite_table[i] = 1
                else:
                    after_splite_table[i] = 1
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

    def splitAndCombine(self,combine_header=False):
        '''
        将表格进行拆分或合并：
        如果一行有一个单元格，且该单元格的w不在最长的单元格列表中，则分表
        如果一行只有一个单元格，但该单元格w在最长的单元格列表中，则该单元格合并到上一行相同位置的单元格中。
        如果一行中的单元格不连续，则该行大概率要合并
        如果一行中的单元格没有第一个也没有最后一个，则该行大概率要合并

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
        #检查单元格中存在空单元格的情况：
        row_have_space = []
        if self.longest_row_x is not None:
            for i in range(1,len(row_length)):
                if row_length[i]<row_length[i-1]:
                    # last_row = self.ordered_table_cells[i - 1]
                    curr_row = self.ordered_table_cells[i]
                    curr_row_index = [self.longest_row_x.index(td.attrs['class'][1]) for td in curr_row]
                    for j in range(1,len(curr_row_index)):
                        if curr_row_index[j]- curr_row_index[j-1]>1:
                            row_have_space.append(i)
        #检查单元格是否没有第一个和最后一个
        row_have_no_start_end = []
        if self.longest_row_x is not None:
            for i in range(1,len(row_length)):
                if row_length[i]<row_length[i-1]:
                    curr_row = self.ordered_table_cells[i]
                    curr_row_index = [self.longest_row_x.index(td.attrs['class'][1]) for td in curr_row]
                    if (0 not in curr_row_index) or ((len(self.longest_row_x)-1) not in curr_row_index):
                        row_have_no_start_end.append(i)
        else:
            for i in range(1,len(row_length)):
                if row_length[i]<row_length[i-1]:
                    last_row = self.ordered_table_cells[i-1]
                    last_row_td = [td.attrs['class'][1] for td in last_row]
                    curr_row = self.ordered_table_cells[i]
                    # curr_row_index = [last_row_td.index(td.attrs['class'][1]) for td in curr_row]
                    if (((curr_row[0].attrs['class'][1] in last_row_td) and (last_row_td.index(curr_row[0].attrs['class'][1])!=0))  or
                         ((curr_row[len(curr_row)-1].attrs['class'][1] in last_row_td) and (last_row_td.index(curr_row[len(curr_row)-1].attrs['class'][1])!=(len(last_row_td)-1)))):
                        row_have_no_start_end.append(i)
        #检查是否存在一行只有一个单元格的情况,求出该行的索引
        row_have_1_cell = [i for i,length in enumerate(row_length) if length==1]
        columns_max_length = max(row_length)
        temp_tables = []
        temp = []
        row_have_no_start_end.extend(row_have_space)

        #检查单元格是否在不同的页面
        diff_page = []
        if columns_max_length > 1 and len(row_have_no_start_end)>=1:
            for i in row_have_no_start_end:
                if i+1 <=len(self.ordered_table_cells) and i-1>=0:
                    last_row = self.ordered_table_cells[i-1]
                    curr_row = self.ordered_table_cells[i]
                    if last_row[0].parent['class'] != curr_row[0].parent['class']:
                        diff_page.append(i)

        row_have_1_cell.extend(diff_page)
        row_have_1_cell = sorted(list(set(row_have_1_cell)),reverse=True)

        if columns_max_length > 1 and len(row_have_1_cell)>=1:
            for i in row_have_1_cell:
                if i+1 <=len(self.ordered_table_cells) and i-1>=0:
                    last_row = self.ordered_table_cells[i-1]
                    if i+1<len(self.ordered_table_cells):
                        next_row = self.ordered_table_cells[i+1]
                    else:
                        next_row = None
                    curr_row = self.ordered_table_cells[i]

                    is_combin = []
                    for curr_td in curr_row:
                        if type(last_row) is not tuple:
                            flag = curr_td.attrs['class'][3] in [td.attrs['class'][3] for td in last_row]
                            is_combin.append(flag)

                    if len(set(is_combin))==1 and list(set(is_combin))[0] == True:
                        for curr_td in curr_row:
                            for td in last_row:
                                if td.attrs['class'][3] == curr_td.attrs['class'][3] and td.attrs['class'][1] == \
                                        curr_td.attrs['class'][1] :
                                    td.string = td.get_text() + curr_td.get_text()
                                    # combine_list.append(i)
                        self.ordered_table_cells.pop(i)
                    elif True in is_combin:
                        for curr_td in curr_row:
                            for td in last_row:
                                if td.attrs['class'][3] == curr_td.attrs['class'][3] and td.attrs['class'][1] == \
                                        curr_td.attrs['class'][1] :
                                    td.string = td.get_text() + curr_td.get_text()
                                    # curr_row.remove(curr_td)
                        # self.ordered_table_cells.pop(i)
                    else:
                        if next_row is None or type(next_row) is int:
                            pass
                        else:
                            if len(curr_row) == 1 :
                                if self.check_row_have_pure_digital(next_row):
                                    self.ordered_table_cells[i] = (1,re.sub('\s+','',self.ordered_table_cells[i][0].get_text()))
                                else:
                                    self.ordered_table_cells[i] = (1,re.sub('\s+','',self.ordered_table_cells[i][0].get_text()))
                else:
                    if i == 0:
                        self.ordered_table_cells[i] = (1,re.sub('\s+','',self.ordered_table_cells[i][0].get_text()))
                    elif i == len(self.ordered_table_cells):
                        self.ordered_table_cells[i] = (1,re.sub('\s+','',self.ordered_table_cells[i][0].get_text()))
                    else:
                        pass

            for tr in self.ordered_table_cells:
                if isinstance(tr,tuple):
                    if len(temp)>0:
                        temp_tables.append(temp[:])
                        temp = []
                        temp_tables.append(tr)
                elif tr==0:
                    pass
                else:
                    temp.append(tr[:])
            if len(temp)>0:
                temp_tables.append(temp[:])

            if len(temp_tables)>1:

                first_df_id = 0
                for key, table in enumerate(temp_tables):
                    if not isinstance(table,str):
                        first_df_id = key
                        break

                first_df = temp_tables[first_df_id]

                result_talbes = []
                for key, table in enumerate(temp_tables):

                    if isinstance(table,tuple):
                        result_talbes.append(table)
                    else:
                        if key == first_df_id:
                            result_talbes.append(table)
                        else:
                            if True not in [is_num(re.sub('\s+','',cell.get_text())) for cell in table[0]]:
                                pass
                            else:
                                first_lines = []
                                if first_df is not None:
                                    for tr in first_df:
                                        if True not in [is_num(re.sub('\s+', '', cell.get_text())) for cell in tr]:
                                            first_lines.append(tr)
                                        else:
                                            break
                                if len(first_lines)>0:
                                    first_lines.extend(table)
                                    result_talbes.append(first_lines)
                                else:
                                    pass
                return result_talbes
            else:
                return temp_tables
        else:
            return [self.ordered_table_cells]

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
        max_row_col = [td.attrs['class'][1] for td in max_tr]

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
                    pre_now_diff = list(pre_row_set_col.difference(now_row_set_col))
                    pre_now_diff.sort(key=lambda x:pre_row_col.index(x))
                    for x in pre_now_diff:
                        diff_col_num = pre_row_col.index(x)
                        max_col_num = max_row_col.index(x) if x in max_row_col else diff_col_num
                        now_row.insert(max_col_num, pre_row[diff_col_num])

        # 单元格向左填充
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

    def create_html_table(self,table):
        '''
        #为表格添加table,td,tr等html形式元素
        :param table: orderedtablecells
        :return:Beautifulsoup(table节点对象）
        '''
        soup = BeautifulSoup('<html></html>','lxml')
        html_table = soup.new_tag('table')
        for line in table:
            tr = soup.new_tag('tr')
            for cell in line:
                new_td = cell.wrap(soup.new_tag('td'))
                tr.append(BeautifulSoup(str(new_td), 'lxml').find('td'))  # 不能直接append td，否则会出现浅拷贝情况
            html_table.append(BeautifulSoup(str(tr), 'lxml').find('tr'))  # 不能直接append tr，否则会出现浅拷贝情况
        return html_table

if __name__ == '__main__':
    filepath = r'H:\data_extract\report\shenzhen\sz_000701_20171231.html'
    from utils.parsehtml import HtmlFile
    file = HtmlFile(filepath)

