# _author : litufu
# date : 2018/4/5

import pandas as pd
from bs4 import BeautifulSoup
from collections import OrderedDict
from itertools import groupby
import re
from collections import OrderedDict
from utils.pandas_text_process import *

def handle_more_talbe_in_one_page(pf_id):



    #第三步：找到所有表格的行信息
    # 将所有表格的行信息统计出来
    table_line_names = []  #[[table1.line1,table1.lin2],[table2.line1,table2.line2]
    #分别遍历所有表格的单元格信息
    for table_cells in all_table_cells:
        #用于存放行信息
        lines_names_list = []
        #用于去除重复的行信息
        lines_names_set = set()
        for table_cell in table_cells:
            if table_cell.attrs['class'][2] in lines_names_set:
                pass
            else:
                lines_names_set.add(table_cell.attrs['class'][2])
                lines_names_list.append(table_cell.attrs['class'][2])
        table_line_names.append(lines_names_list)

    #第四步：重新改写html元素，增加table、tr和td元素
    #新建html标签
    html_tables = soup.new_tag('html')
    #遍历行数
    for k,lines_names in enumerate(table_line_names):
        #新建一个表格
        table = soup.new_tag('table')
        for lines_name in lines_names:
            #新建一行
            tr = soup.new_tag('tr')
            #遍历该表格对应的所有单元格，添加到对应的行
            for table_cell in all_table_cells[k]:
                if table_cell.attrs['class'][2] == lines_name:
                    new_td = table_cell.wrap(soup.new_tag('td'))
                    #将单元格添加到行中
                    tr.append(new_td)
            #将行添加到表格中
            table.append(tr)
        #将表格添加到html中
        html_tables.append(table)

    #使用pandas读取表格解析表格
    try:
        dfs  = pd.read_html(str(html_tables))
        return dfs
    except Exception as e:
        return None

def is_continue(lst):
    '''
    判断列表中的数字是否连续:采用数值减去下标的方式判断
    :param a_list: 列表数据
    :return: 是否连续
    '''

    if len([k for k, g in groupby(enumerate(sorted(lst)), key=lambda x: x[1] - x[0])])==1:
        return True
    else:
        return False

def break_cell_to_text(soup,texts=None,previous_sibling=False ):
    '''

    :param soup: BeautifulSoup(html,'lxml')
    :param texts: 要变成text的文本，应该具有唯一性
    :return:
    '''
    if texts != None:
        for text in texts:
            if len(soup.find_all(text=text))==1:
                if previous_sibling == False:
                    special_text_tag = soup.find(text=text)
                    tag_special = special_text_tag.find_parent('div',class_='c')
                    tag_special.attrs['class'][0] = 't'
                elif previous_sibling == True:
                    special_text_tag = soup.find(text=text)
                    tag_special = special_text_tag.find_parent('div',class_='c')
                    tag_special.attrs['class'][0] = 't'
                    tag_special_previous = tag_special.previous_sibling
                    tag_special_previous.attrs['class'][0] = 't'




def get_all_pc_children(filepath):
    '''
    获取html中所有div(class_='pc')下的children
    :param pf_id: 页码信息:'pf1','pf2'
    :return: 一个包含所有表格的列表，表格是一个包含所有单元格的列表
    '''

    soup = BeautifulSoup(open(filepath, 'r',encoding='utf-8'), 'lxml')
    # texts1 = ['前十名无限售条件股东持股情况',]
    # break_cell_to_text(soup, texts=texts1)
    # texts = ['与中国铁路总公司及其下属单位之间的交易 ',\
    #          '通过中国铁路总公司统一清算的与其下属单位之间的运输服务收入及支出',\
    #                             '与中国铁路总公司及其下属单位之间的其他交易',\
    #                                '与中国铁路总公司及其下属单位之间的应收、应付款项余额',\
    #                                '中国铁路总公司及其下属单位代本公司结算款项']
    #
    # break_cell_to_text(soup,texts=texts,previous_sibling=True)
    pfs = soup.find_all(id=re.compile('pf'))
    # 第一步：找到所有子元素
    # 1、找到第几页
    all_pc_children = []
    pf_dict = OrderedDict()
    pf_dict2 = OrderedDict()
    for k,pf in enumerate(pfs):
        # 找到内容主题
        pc_children = get_pc_children(pf)
        #将pc_childen添加到pf_table_dict 中，索引为pf_id
        pf_dict[pf.attrs['id']] = pc_children
        #将pc_children添加到pf_table_dict2中,索引为连续整数
        pf_dict2[k] = pc_children

    for k in pf_dict2:

        '''
        如果当前页pc_childern最后一行的class_='c'并且下一页pc_children的第一行
        '''
        if list(pf_dict2[k])[-1].has_attr('class') and list(pf_dict2[k])[-1].attrs['class'][0] == 'c':
            if k + 1 in pf_dict2 and list(pf_dict2[k+1])[0].has_attr('class') and list(pf_dict2[k+1])[0].attrs['class'][0] == 'c':
                # 求当前页最后一个表格信息
                # 最后一个表格所有的单元格
                cells = get_table_cells(list(pf_dict2[k]))[-1]
                # 最后一个表格的cells_dict
                cells_dict = create_cells_dict(cells)
                # 最后一个表格的坐标
                table_coordinate = create_table_coordinate(cells_dict)
                last_line_x = [cell[0] for cell in table_coordinate[-1]]

                # 获取下一页第一个表的信息
                # 第一个表格所有的单元格
                cells = get_table_cells(list(pf_dict2[k+1]))[0]
                # 第一个一个表格的cells_dict
                cells_dict = create_cells_dict(cells)
                # 第一个表格的坐标
                table_coordinate = create_table_coordinate(cells_dict)
                first_line_x = [cell[0] for cell in table_coordinate[0]]
                #如果两个坐标不一致，则在两个跨页表格中间添加一个div,class_='t'的元素，以便把两页表格分隔开
                if last_line_x != first_line_x:
                    all_pc_children.extend(list(pf_dict2[k]))
                    all_pc_children.append(soup.new_tag('div',class_='t'))
                else:
                    all_pc_children.extend(list(pf_dict2[k]))
            else:
                all_pc_children.extend(list(pf_dict2[k]))
        else:
            all_pc_children.extend(list(pf_dict2[k]))

    return all_pc_children

def get_pc_children(pf):
    '''
    获取当前网页的pc_children
    :param pf: pf = soup.find(id=re.compile('pf'))
    :return: 列表格式pc = pf.find(class_='pc').childern
    '''
    pc = pf.find(class_='pc')
    # 删除前3个div(包括页眉、页脚和空行）,如果是竖向的话为y1,y2,y3如果是横向的话变为h2,h3,h4
    tag_img = pc.find('img')
    tag_img.decompose()
    tag_y1 = pc.find(class_='y1')
    if tag_y1 == None:
        tag_y1 = pc.find(class_='h2')
    tag_y1.decompose()
    tag_y2 = pc.find(class_='y2')
    if tag_y2 == None:
        tag_y2 = pc.find(class_='h3')
    tag_y2.decompose()
    tag_y3 = pc.find(class_='y3')
    if tag_y3 == None:
        tag_y3 = pc.find(class_='h4')
    tag_y3.decompose()

    # 查找pc所有的子元素
    # 获取当前页的pc_children,并删除换行符
    pc_children = del_same_item_from_list(list(pc.children),'\n')
    return pc_children

def del_same_item_from_list(alist,item):
    '''
    删除列表中相同的元素
    :param alist: 列表
    :param item: 元素
    :return: alist
    '''
    for i in range(len(alist)-1,-1,-1):
        # 倒序循环，从最后一个元素循环到第一个元素。不能用正序循环，因为正序循环删除元素后后续的列表的长度和元素下标同时也跟着变了，len(alist)是动态的。
        if alist[i] == item:
            alist.pop(i)  # 将index=i处的元素删除并return该元素。如果不想保存这个被删除的值只要不把alist.pop(i)赋值给变量就好，不影响程序运行。

    return alist

def get_table_cells(pc_children):
    '''
    根据传入的所有div(class_='pc')下的children,生成tablecells:
    # [[table1.cell1,table1.cell2],[table2.cell1,table2.cell2]...]
    :param pc_children: div(class_='pc')下的children
    :return: 传入数据可以生成的表格
    '''
    table_cells = []  # [[table1.cell1,table1.cell2],[table2.cell1,table2.cell2]...]
    # 定义的临时表格，用于存放一个表格的所有单元格
    temp = []
    # 遍历所有的子元素
    for child in pc_children:
        # 判断元素是否为div

        if child.name == 'div':
            # 判断是否有class属性，判断第一个属性是否为'c'
            if child.has_attr('class') and child.attrs['class'][0] == 'c':
                temp.append(child)
            # 如果已经不是单元格了，说明表格已经中断，将temp储存到结果中，并清空temp
            else:
                if len(temp) > 0:
                    table_cells.append(temp[:])
                    temp = []
                else:
                    pass
        else:
            pass
    if len(temp) >0:
        table_cells.append(temp[:])
    return table_cells

def create_cells_dict(cells):
    '''

    :param cells: 所有的单元格列表，按照顺序排列
    :return: cells_dict:格式如下：
    {('x16', 'y85', 'w17', 'h1d')：cell1，('x28', 'y88', 'w18', 'h14')：cell2,\
    ('x29', 'y88', 'w19', 'h14'):cell3,('x28', 'y89', 'w18', 'h14'):cell4...}
    '''
    cells_dict = OrderedDict()
    for cell in cells:
        cells_dict[tuple(cell.attrs['class'][1:])] = cell
    return cells_dict

def create_table_coordinate(cells_dict):
    '''
    返回所有表格坐标信息，对于合并单元格采用先向下填充，再向左填充的方法，确保所有的行拥有相同的列数
    :param cells_dict: 单元格字典，见create_cells_dict
    :return: table 将同一行的单元格放在一个列表，将行按照顺序添加到table中：格式如下
    [[('x16', 'y85', 'w17', 'h1d'), ('x28', 'y88', 'w18', 'h14'), ('x29', 'y88', 'w19', 'h14')], \
    [ ('x28', 'y89', 'w18', 'h14'), ('x29', 'y89', 'w19', 'h14')], \
    [('x28', 'y85', 'w18', 'h1e'), ('x29', 'y85', 'w19', 'h1e')]]
    '''

    #求出原始表格信息：
    #思路：找到表格中最大的行，然后各个单元格按照该行的列信息排列。如果单元格在最大行的索引比前面单元格小，那么就换行。
    #信息最全的行
    longest_row = find_longest_row(cells_dict)

    #零散的单元格信息
    cell_items = [td for td in cells_dict]
    cell_items_x = [td[0] for td in cells_dict]
    #按照信息最全的行排列零散的单元格信息，做成初始表格
    table = []
    #代表一行数据
    tr = []
    tr_set = set()
    if longest_row != None:
        for i in range(len(cell_items)-1):
            if i == 0 :
                tr.append(cell_items[0])
            else:
                if longest_row.index(cell_items[i][0]) >longest_row.index(cell_items[i-1][0]):
                    tr.append(cell_items[i])
                else:
                    table.append(tr[:])
                    tr = []
                    tr.append(cell_items[i])
        table.append(tr)
    else:
        for cell in cell_items:
            if cell[0] not in tr_set:
                tr.append(cell)
                tr_set.add(cell[0])
            elif cell[0] in tr_set:
                table.append(tr[:])
                tr = []
                tr_set = set()
                tr.append(cell)
                tr_set.add(cell[0])
            else:
                pass
        table.append(tr)




    # 计算所有行的单元格数量
    line_lengths = [len(line) for line in table]
    # 找出最大行所有的单元格
    maxlength = max(line_lengths)
    # 找出拥有最多单元格所在的行数
    max_len_row_in_line = line_lengths.index(maxlength)
    # 找到最大的单元格所在的行
    max_tr = table[max_len_row_in_line]

    #单元格向下填充
    for i,tr in enumerate(table):
        #如果已经拥有与最长行相同的单元格数量则跳过
        if len(tr) == maxlength:
            pass
        else:
            if i == 0:
                pass
            else:
                #根据上一行向下填充
                pre_row = table[i-1]
                now_row = tr
                pre_row_col = [td[0] for td in pre_row]
                now_row_col = [td[0] for td in now_row]
                pre_row_set_col = set(pre_row_col)
                now_row_set_col = set(now_row_col)
                pre_now_diff = pre_row_set_col.difference(now_row_set_col)
                for x in pre_now_diff:
                    diff_col_num = pre_row_col.index(x)
                    now_row.insert(diff_col_num,pre_row[diff_col_num])

    #单元格想左填充
    for i, tr in enumerate(table):
        # 如果已经是最大行跳过
        if len(tr) == maxlength:
            pass
        else:
            #最大行
            max_row = max_tr
            #现在循环行
            now_row = tr
            #最大行所有的单元格
            max_row_col = [td[0] for td in max_row]
            #现在行所有的单元格
            now_row_col = [td[0] for td in now_row]
            # 最大航所有的单元格转换为set便于求差集
            max_row_set_col = set(max_row_col)
            # 现在行所有的单元格转换为set便于求差集
            now_row_set_col = set(now_row_col)
            #求最大行与现在行的单元格差集
            max_now_diff_set = max_row_set_col.difference(now_row_set_col)
            #将差集按照max_row原来的顺序排列
            max_now_diff_list = list(max_now_diff_set)
            sorted_max_now_diff_list = sorted(max_now_diff_list,key=lambda x:max_row_col.index(x))
            #遍历已经排序的差集单元格
            for x in sorted_max_now_diff_list:
                #求差的单元格所在的行数
                diff_col_num = max_row_col.index(x)
                #在当前单元格的中相差的行数插入前一个单元格的内容
                now_row.insert(diff_col_num, now_row[diff_col_num - 1])
    return table

def create_html_table(cells_dict,table_coordinate):
    '''

    :param cells_dict: {表格单元格坐标信息:单元格}
    :param table_coordinate: 表格单元格坐标信息列表
    :return:Beautifulsoup(table节点对象）
    '''
    soup = BeautifulSoup('<html></html>','lxml')
    table  = soup.new_tag('table')
    for line_coordinate in table_coordinate:
        tr = soup.new_tag('tr')
        for cell_coordinate in line_coordinate:
            cell = cells_dict[cell_coordinate]
            new_td = cell.wrap(soup.new_tag('td'))
            tr.append(BeautifulSoup(str(new_td),'lxml').find('td'))#不能直接append td，否则会出现浅拷贝情况
        table.append(BeautifulSoup(str(tr),'lxml').find('tr'))#不能直接append tr，否则会出现浅拷贝情况

    return table

def handle_page_table(filepath):

    soup = BeautifulSoup('<html></html>', 'lxml')
    all_pc_children = get_all_pc_children(filepath)
    table_cells = get_table_cells(all_pc_children)
    for cells in table_cells:
        cells_dict = create_cells_dict(cells)
        table_coordinate = create_table_coordinate(cells_dict)
        html_table = create_html_table(cells_dict,table_coordinate)
        soup.append(html_table)
    return soup


def find_longest_row(cells_dict):
    '''

    :param cells_dict: 单个表，有序的cells字典{cell位置信息，cell的BeautifulSoup对象信息
    :return: 列表，安序排列的最长行 ['x68', 'x6f', 'x62', 'x6e', 'x30']
    '''
    print(cells_dict)
    print('-----------------------------')
    cell_items = [td[0] for td in cells_dict]
    columns = set(cell_items)
    col_len = len(columns)
    test_cell_items = cell_items[:]
    # 求各列数的位置
    first_item = cell_items[0]
    while True:
        try:
            num = test_cell_items.index(first_item)
            if len(set(test_cell_items[num:col_len])) == col_len:
                return test_cell_items[num:col_len]
            else:
                test_cell_items.remove(first_item)
                start_num = test_cell_items.index(first_item)
                test_cell_items = test_cell_items[start_num:]
        except Exception as e:
            print('101:没有找到最长的行')
            return None

if __name__ == '__main__':

    # lst = [2]
    # print(is_continue(lst))
    # handle_merge_cells('pf5')
    # import xlrd
    #
    # xls = xlrd.open_workbook(r'C:\Users\28521\Desktop\123.xlsx')
    # sh = xls.sheet_by_index(0)
    #
    # # 读取excel并读取第一页的内容。
    #
    # for crange in sh.merged_cells:
    #     rs, re, cs, ce = crange
    #     print(rs,re,cs,ce)
    #     print((rs, cs),(re - rs, ce - cs))

    # dfs = pd.read_html()
    # soup = BeautifulSoup()
    # 求总共的列数



    html = handle_page_table('t.html')
    # all_pc_children = get_all_pc_children('nw.html')
    # for pc_childern in all_pc_children:
    #     table_cells = get_table_cells(pc_childern)
    #     for cells in table_cells:
    #         print('------------------')
    #         print(cells)
    # table_cells = get_table_cells('t.html')
    # for cells in table_cells:
    #     cells_dict = create_cells_dict(cells)
    #     # print(cells_dict)
    #     result = func(cells_dict)
    #     print(result)
    dfs = pd.read_html(str(html))
    for df in dfs:
        print(remove_per_from_df(remove_space_from_df(df)))

        # print(df)
    # print(html)
    # soup = BeautifulSoup(open('t.html',encoding='utf-8').read(),'lxml')
    # cells = soup.find_all(class_='c')



    # print(tag_special.attrs['class'])
    # print(tag_special)
    # cells_dict = create_cells_dict(cells)
    # table_coordinate = create_table_coordinate(cells_dict)
    # table = create_html_table(cells_dict,table_coordinate)
    # dfs = pd.read_html(table)
    # print(dfs[0])






    # dfs = handle_more_talbe_in_one_page('pf5')
    # if dfs is not None:
    #     for df in dfs:
    #         print(df)
    # else:
    #     print('该页面不存在表格')









