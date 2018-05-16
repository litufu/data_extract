# _author : litufu
# date : 2018/4/18
import pandas as pd
from collections import OrderedDict
import re
from sqlalchemy import create_engine
engine = create_engine(r'sqlite:///H:\data_extract\db.sqlite3')
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
from utils.mytools import remove_space_from_df
from report_data_extract import models
from utils.handleIndex import HtmlFile
from utils.handleTable import HtmlTable
from  utils.handleindexcontent.first import *
from  utils.handleindexcontent.second import *
from  utils.handleindexcontent.third import *
from  utils.handleindexcontent.fourth import *
from  utils.handleindexcontent.fifth import *
from  utils.handleindexcontent.sixth import *
from  utils.handleindexcontent.eighth import *
from  utils.handleindexcontent.tenth import *
from  utils.handleindexcontent.eleventh import *
from  utils.handleindexcontent.twelve import *

def extract(filepath):
    #第一步，解析页面元素，并按照索引对元素进行分离
    file = HtmlFile(filepath)
    file_all_cells = file.file_cells
    # file.clearTempIndexCellCount()
    # file.parse_all_dir()
    cells_length = len(file_all_cells)
    objs = models.TempIndexCellCount.objects.all().order_by('start_id')
    file_all_cells_classify = []
    for i in range(len(objs)):
        start_id = objs[i].start_id
        if i+1 < len(objs):
            end_id = objs[i+1].start_id
        else:
            end_id = cells_length
        if end_id - start_id >1:
            cells = file_all_cells[start_id+1:end_id]
            classify_cells = get_classify_cells(cells)
            file_all_cells_classify.append({objs[i].no:classify_cells})
        else:
            file_all_cells_classify.append({objs[i].no:''})

    return file.code,file.accper,file_all_cells_classify

def get_classify_cells(cells):
    '''
    将元素分为表格元素和文本元素。
    原理：表格与表格中间存在非表格元素：
                表格单元格html元素的属性class为以’c'开头的div
                非表格html元素的属性class为以’t'开头的div
                把文件元素中所有相连的c组成列表放在一起即为一个表格所有的单元格，如果出现非表格html元素，
                说明表格结束。
    :param cells: 一个索引下的所有元素
    :return: 传入数据可以生成的表格
    '''
    cells_classify = []  # [[text1.cell1,text2.cell2],[table1.cell1,table1.cell2],[table2.cell1,table2.cell2]...]
    # 定义的临时表格，用于存放一个表格的所有单元格
    table_temp = []
    text_temp = []
    # 遍历所有的子元素
    for cell in cells:
        # 判断元素是否为div
        if cell.name == 'div':
            # 判断是否有class属性，判断第一个属性是否为'c'
            if cell.has_attr('class') and cell.attrs['class'][0] == 'c':
                if len(text_temp) > 0:
                    text = produce_text(text_temp)
                    cells_classify.append({'t':text})
                    text_temp = []
                else:
                    pass
                table_temp.append(cell)
            # 如果已经不是单元格了，说明表格已经中断，将temp储存到结果中，并清空temp
            elif cell.has_attr('class') and cell.attrs['class'][0] == 't':
                if len(table_temp) > 0:
                    html_table = produce_table(table_temp)
                    cells_classify.append({'c':html_table})
                    table_temp = []
                else:
                    pass
                text_temp.append(cell)
            else:
                pass
        else:
            pass

    if len(table_temp) > 0:
        cells_classify.append({'c':produce_table(table_temp)})
    if len(text_temp) > 0:
        cells_classify.append({'t':produce_text(text_temp)})

    return cells_classify

def produce_text(cells_list):
    cell_text = []
    for cell in cells_list:
        cell_text.append(re.sub('\s+','',cell.get_text()))
    return ''.join(cell_text)

def produce_table(cells_list):
    table = HtmlTable(cells_list)
    dfs = []
    for table1 in table.fill_merge_cells_table:
        html_table = table.create_html_table(table1)
        try:
            df = html_table_to_df(str(html_table))
            dfs.append(df)
        except Exception as e:
            return pd.DataFrame()
    return dfs

def html_table_to_df(html_table):
    table = pd.read_html(html_table)
    return table

def print_contents(indexno,indexcontents):
    for content in indexcontents:
        for classify,item in content.items():
            if classify =='t':
                print(classify,item)
            elif classify == 'c' and len(item)>0:
                # print('item',item)
                for tables in item:
                    # print('tables',tables)
                    for table in tables:
                        print(classify, remove_space_from_df(table))
            else:
                print('未统计')
            print('-------------------')
    print('--------{}结束----------'.format(indexno))

def handle_content(indexno,indexcontents,stk_cd_id,acc_per):
    indexno_id = models.StdContentIndex.objects.get(no=indexno).id
    handle_classname = models.IndexHandleMethod.objects.filter(indexno_id=indexno_id)
    if len(handle_classname) > 0 and handle_classname[0].handle_classname != 'pass':
        Handleclass = eval(handle_classname[0].handle_classname)
        obj = Handleclass(stk_cd_id, acc_per, indexno, indexcontents)
        obj.save()
    elif len(handle_classname) > 0 and handle_classname[0].handle_classname == 'pass':
        print('无需处理', indexno)
        pass
    else:
        print('尚未进行处理', indexno)
        exit()

def handle_all_contents(filepath):
    stk_cd,acc_per,indexcontents = extract(filepath)
    stk_cd_id = models.CompanyList.objects.get(code=stk_cd).code
    for contents in indexcontents:
        for indexno,indexcontents in contents.items():
            print('--------{}开始----------'.format(indexno))
            if indexno != '08050200':
                continue
            handle_content(indexno,indexcontents,stk_cd_id,acc_per)

def print_all_contents(filepath):
    stk_cd,acc_per,indexcontents = extract(filepath)
    # stk_cd_id = models.CompanyList.objects.get(code=stk_cd).code
    for contents in indexcontents:
        for indexno,indexcontents in contents.items():
            print('--------{}开始----------'.format(indexno))
            print_contents(indexno,indexcontents)

if __name__ == '__main__':
    # filepath = r'H:\data_extract\report\shanghai\sh_600312_20171231.html'
    filepath = r'H:\data_extract\report\shenzhen\sz_000701_20171231.html'
    handle_all_contents(filepath)
    # print_all_contents(filepath)


    # stk_cd,acc_per,indexcontents = extract(filepath)
    # stk_cd_id = models.CompanyList.objects.get(code=stk_cd).code
    # for contents in indexcontents:
    #     for indexno,indexcontents in contents.items():
    #         print('--------{}开始----------'.format(indexno))
    #         # if indexno != '0b11030000':
    #         #     continue
    #         indexno_id = models.StdContentIndex.objects.get(no=indexno).id
    #         handle_classname = models.IndexHandleMethod.objects.filter(indexno_id=indexno_id)
    #         if len(handle_classname)>0 and handle_classname[0].handle_classname != 'pass':
    #             Handleclass = eval(handle_classname[0].handle_classname)
    #             obj = Handleclass(stk_cd_id,acc_per,indexno,indexcontents)
    #             obj.save()
    #         elif len(handle_classname)>0 and handle_classname[0].handle_classname == 'pass':
    #             print('无需处理',indexno)
    #             pass
    #         else:
    #             print('尚未进行处理',indexno)
    #             exit()
    #
    #
    #         # for content in indexcontents:
    #         #     for classify,item in content.items():
    #         #         if classify =='t':
    #         #             print(classify,item)
    #         #         elif classify == 'c' and len(item)>0:
    #         #             # print('item',item)
    #         #             for tables in item:
    #         #                 # print('tables',tables)
    #         #                 for table in tables:
    #         #                     print(classify, remove_space_from_df(table))
    #         #         else:
    #         #             print('未统计')
    #         #         print('-------------------')
    #         # print('--------{}结束----------'.format(indexno))