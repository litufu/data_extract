# _author : litufu
# date : 2018/4/8

from nose.tools import *
from utils.parsehtml import *
from bs4.element import Tag

# def test_htmlfile():
#     #测试是否能够获取文件内容
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     assert_equal(file.pageCount,168)
#     assert_equal(file.file_content,[])
#     assert_equal(file.all_table_cells,[])
#     assert_equal(len(file.page_contents_base_pgCount),168)
#     assert_equal(len(file.pageId),168)
#     assert_equal(file.pfs[0]['id'],'pf1')
#     assert_equal(len(file.page_contents_base_pgid),168)
#
# def test_htmlpage_pgContent():
#     #测试是否能够获取单页的内容
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     page = HtmlPage(file,1)
#     page_1_content = page.pgContent
#     assert_equal(type(page_1_content),list)
#     assert_equal(type(page_1_content[0]),Tag)
#     assert_regexp_matches(page_1_content[0].get_text(),r'公司代码：.*')
#     assert_regexp_matches(page_1_content[-1].get_text(),r'否')
#
# def test_htmlpage_get_tables_cells():
#     '''
#     测试是否能够获取页面中所有的表格内容
#     :return:
#     '''
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     page = HtmlPage(file,1)
#     page_table_cells = page.get_tables_cells()
#     assert_equal(type(page_table_cells),list)
#     assert_equal(type(page_table_cells[0]), list)
#     assert_equal(page_table_cells[0][0].get_text().strip(), r'未出席董事职务')
#     assert_equal(page_table_cells[0][0]['class'][0], 'c')
#     assert_equal(page_table_cells[-1][-1]['class'][0], 'c')
#     assert_equal(page_table_cells[-1][-1].get_text().strip(), r'俞蒙')
#
#
# def test_htmlpage_cells_dict():
#     #测试是否可以正确对单个表格建立单元格位置信息与单元格匹配的字典
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     page = HtmlPage(file,1)
#     table_1_cells_dict = page.pg_tables_cells_dict[1]
#     assert_equal(type(list(table_1_cells_dict.keys())[0]),tuple)
#     assert_equal(type(list(table_1_cells_dict.values())[0]),Tag)
#     assert_equal(list(table_1_cells_dict.values())[0].get_text().strip(),r'未出席董事职务')
#     assert_equal(list(table_1_cells_dict.keys())[0][0],'x0')
#     assert_equal(list(table_1_cells_dict.keys())[-1][0],'xc')
#     assert_equal(list(table_1_cells_dict.values())[-1].get_text().strip(),r'俞蒙')
#
# #
# def test_table_get_longest_row_x():
#     # 测试是否可以根据表格位置信息，按照表格正确的行和列排列表格中的单元格
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     page = HtmlPage(file,31)
#     table_cells_dict = page.pg_tables_cells_dict[3]
#     table = HtmlTable(table_cells_dict)
#     long_row_x = table.longest_row_x
#     assert_equal(type(long_row_x),list)
#     assert_equal(len(long_row_x),8)
#
#     page = HtmlPage(file, 32)
#     table_cells_dict = page.pg_tables_cells_dict[1]
#     table = HtmlTable(table_cells_dict)
#     long_row_x = table.longest_row_x
#     assert_equal(long_row_x,None)

# def test_order_table_cell():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     page = HtmlPage(file,31)
#     table_cells_dict = page.pg_tables_cells_dict[3]
#     table = HtmlTable(table_cells_dict)
#     ordered_table = table.ordered_table
#     assert_is_not_none(table.longest_row_x)
#     assert_equal(len(ordered_table),9)
#     assert_equal(type(ordered_table),list)
#     assert_equal(len(ordered_table[0]),1)
#     assert_equal(len(ordered_table[1]),7)
#     assert_equal(len(ordered_table[2]),2)
#     assert_equal(len(ordered_table[3]),8)
#     assert_equal(type(ordered_table[3][0]),tuple)
#     assert_equal(ordered_table[3][0],('x16','y35f','wa2','h22'))
#
#     page = HtmlPage(file,32)
#     table_cells_dict = page.pg_tables_cells_dict[1]
#     table = HtmlTable(table_cells_dict)
#     assert_is_none(table.longest_row_x)
#     ordered_table = table.ordered_table
#     assert_equal(len(ordered_table),18)
#     assert_equal(len(ordered_table[0]),8)
#     assert_equal(len(ordered_table[4]),1)
#     assert_equal(len(ordered_table[5]),3)
#     assert_equal(len(ordered_table[6]),2)
#     assert_equal(len(ordered_table[7]),4)

# def test_pg_ordered_table_list():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#
#     #测试页面中包含多个表
#     page = HtmlPage(file, 31)
#     page_tables = page.pg_ordered_table_list
#     #页面中包含的表列表
#     assert_equal(type(page_tables),list)
#     assert_equal(len(page_tables),3)
#     #表中包含的行列表
#     assert_equal(type(page_tables[0]),list)
#     assert_equal(len(page_tables[0]),4)
#     assert_equal(len(page_tables[2]),9)
#     #行中包含的单元格列表
#     assert_equal(type(page_tables[0][0]),list)
#     assert_equal(len(page_tables[0][0]),3)
#     assert_equal(len(page_tables[2][8]),8)
#     #单元格要素是tag
#     assert_equal(type(page_tables[0][0][0]), Tag)
#     assert_equal(page_tables[0][0][0].get_text().strip(),'内部职工股的发行日期')
#
#     #测试页面中包含一个表
#     page = HtmlPage(file, 34)
#     page_tables = page.pg_ordered_table_list
#     # 页面中包含的表列表
#     assert_equal(type(page_tables), list)
#     assert_equal(len(page_tables), 1)
#     # 表中包含的行列表
#     assert_equal(type(page_tables[0]), list)
#     assert_equal(len(page_tables[0]), 4)
#     # 行中包含的单元格列表
#     assert_equal(type(page_tables[0][0]), list)
#     assert_equal(len(page_tables[0][0]), 6)
#     # 单元格要素是tag
#     assert_equal(type(page_tables[0][0][0]), Tag)
#     assert_equal(page_tables[0][0][0].get_text().strip(), '法人股东名称')
#
#     #测试页面中包含0个表
#     page = HtmlPage(file, 42)
#     page_tables = page.pg_ordered_table_list
#     # 页面中包含的表列表
#     assert_equal(type(page_tables), list)
#     assert_equal(len(page_tables), 0)

#
# def test_spreedsheet():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     current_page_tables, next_page_tables = file.spreedsheet(31)
#     assert_equal(len(current_page_tables),3)
#     assert_equal(len(next_page_tables),2)
#
# def test_is_spreedsheet():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     flag_31 = file.is_spreedsheet(31)
#     flag_32 = file.is_spreedsheet(32)
#     flag_33 = file.is_spreedsheet(33)
#     assert_equal(flag_31, True)
#     assert_equal(flag_32, True)
#     assert_equal(flag_33, False)


# def test_splittable():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     page = HtmlPage(file,41)
#     table_cells_dict = page.pg_tables_cells_dict[1]
#     table = HtmlTable(table_cells_dict)
#     order_table_cells = table.ordered_table_cells
#     after_splite_table = table.splittable()
#     assert_equal(len(order_table_cells),20)
#     assert_equal(len(after_splite_table),3)
#     assert_equal(len(after_splite_table[0]),4)
#     assert_equal(len(after_splite_table[1]),9)
#     assert_equal(len(after_splite_table[2]),5)
#
#     page = HtmlPage(file,40)
#     table_cells_dict = page.pg_tables_cells_dict[1]
#     table = HtmlTable(table_cells_dict)
#     order_table_cells = table.ordered_table_cells
#     after_splite_table = table.splittable()
#     assert_equal(len(order_table_cells),7)
#     assert_equal(len(after_splite_table),1)
#     assert_equal(len(after_splite_table[0]),7)

# def test_check_if_pure_digital():
#     assert_equal(check_if_pure_digital('0.56%'),True)
#     assert_equal(check_if_pure_digital('1,000.56'),True)
#     assert_equal(check_if_pure_digital('-155550'),True)
#     assert_equal(check_if_pure_digital('5548'),True)
#     assert_equal(check_if_pure_digital('(5548)'),True)
#     assert_equal(check_if_pure_digital('2014年度'),False)
#     assert_equal(check_if_pure_digital('akfj'),False)

# def test_fill_merge_cells():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     page = HtmlPage(file,48)
#     table_cells_dict = page.pg_tables_cells_dict[1]
#     table = HtmlTable(table_cells_dict)
#     fill_merge_cells_tables = table.fill_merge_cells_table
#     assert_equal(len(fill_merge_cells_tables),1)
#     assert_equal(len(fill_merge_cells_tables[0][1]),5)
#
#     page = HtmlPage(file, 15)
#     table_cells_dict = page.pg_tables_cells_dict[2]
#     table = HtmlTable(table_cells_dict)
#     fill_merge_cells_tables = table.fill_merge_cells_table
#     assert_equal(len(fill_merge_cells_tables),2)
#     assert_equal(len(fill_merge_cells_tables[1][0]),7)

# def test_get_all_pg_tables():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     file_all_page_tables = file.file_page_tables
#     assert_equal(len(file_all_page_tables),168)

# def test_spreed_file_tables():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     spreed_file_tables = file.spreed_file_tables
#     assert_equal(len(spreed_file_tables),168)

# def test_spreed_table():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     spreed_file_tables = file.spreed_file_tables
#     page_48 = spreed_file_tables[47]
#     page_49 = spreed_file_tables[48]
#     page_50 = spreed_file_tables[49]
#     assert_equal(len(page_48),1)
#     assert_equal(len(page_49),0)
#     assert_equal(len(page_50),1)
#
#
#     print(page_48)
#     print(page_49)
#     print(page_50)
#
# def test_get_table_previous_text():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     table = file.spreed_file_tables[84][0]
#     print(file.get_table_previous_text(table))

# def test_get_all_table_previous_text():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     file_previous_text = file.get_all_table_previous_text()
#     print(file_previous_text)
#     assert_equal(len(file_previous_text),168)

# def test_get_file_cells_text():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     cells_text = file.get_file_cells_text()
#     assert_equal(cells_text['1tm0x3h5y4ff2fs1fc0sc0ls1ws0'],'公司代码：601006公司简称：大秦铁路')


# def test_get_all_table_previous_text2():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     table = file.spreed_file_tables[84][0]
#     file_previous_text = file.get_table_previous_text_2(table)
#     print(file_previous_text)

# def test_get_all_table_previous_text():
#     filepath = r'H:\data_extract\utils\nw.html'
#     file = HtmlFile(filepath)
#     file_previous_text = file.get_all_table_previous_text_2()
#     assert_equal(len(file_previous_text),168)


# def test_create_ordered_table():
#     #测试是否可以根据表格位置信息，按照表格正确的行和列排列表格中的单元格
#     filepath = r'H:\data_extract\utils\test.html'
#     file = HtmlReport(filepath)


# def test_get_origin_page_num():
#     filepath = r'H:\data_extract\report\shenzhen\1204618902.html'
#     file = HtmlFile(filepath)
#     page = HtmlPage(file,3)
#
#     title,origin_page_num = page.get_origin_page_num()
#     assert_equal(title,'浙江万丰奥威汽轮股份有限公司2017年年度报告全文')
#     assert_equal(origin_page_num,'3')


# def test_get_dir():
#     filepath = r'H:\data_extract\report\shenzhen\1204618902.html'
#     file = HtmlFile(filepath)
#
#     root = file.soup.find('div', id='outline')
#     file.dirlist(root)










