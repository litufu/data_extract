# _author : litufu
# date : 2018/5/27
import pandas as pd
from sqlalchemy import create_engine
import json
engine = create_engine(r'sqlite:///H:\data_extract\newsdata.sqlite3')
# from report_data_extract import models
from utils.mytools import remove_space_from_df,similar_item_with_list,similar_list
import numpy as np
import re


def compare_list_equal(list1, list2):
    ret = []
    for i1 in list1:
        if i1 in list2:
            ret.append(True)
        else:
            ret.append(False)
    if len(set(ret)) == 1 and list(set(ret))[0] == True:
        return True
    else:
        return False


def compare_list_similar(list1, list2, per=0.8):
    sl = similar_list(list1, list2, per)
    if len(sl) == len(list1):
        return True
    else:
        return False


df1 = pd.read_sql('select * from report_data_extract_tableattr',engine)
df1 = remove_space_from_df(df1)
df2 = pd.read_sql('report_data_extract_stdcontentindex',engine)
df2 = remove_space_from_df(df2)
df3 = pd.merge(df1,df2,how='outer',left_on='indexno_id',right_on='id')
df4 = pd.pivot_table(df3,index=['no','name','columns'],values=['no_name'],aggfunc='count')
df5 = pd.pivot_table(df3,index=['no','name','indexes'],values=['no_name'],aggfunc='count')
df4 = df4.reset_index()
df5 = df5.reset_index()
df6 = df4.groupby('no').apply(lambda t: t[t.no_name==t.no_name.max()])
df7 = df5.groupby('no').apply(lambda t: t[t.no_name==t.no_name.max()])
df6 = df6[df6.no_name!=1]
df7 = df7[df7.no_name!=1]
df8 = pd.merge(df6,df7,how='outer',left_on='no',right_on='no')
index_std = []
count = []
for key,(x1,x2) in enumerate(list(zip(df8.no_name_x,df8.no_name_y))):
    if np.isnan(x1):
        index_std.append(df8.iloc[key, 5])
        count.append(x2)
    if np.isnan(x2):
        index_std.append(df8.iloc[key, 2])
        count.append(x1)
    if not np.isnan(x1) and not np.isnan(x2):
        if x1>x2:
            index_std.append(df8.iloc[key,2])
            count.append(x1)
        else:
            index_std.append(df8.iloc[key, 5])
            count.append(x2)
df8['index_std'] = index_std
df8['count'] = count
df8 = df8[['no','name_x','index_std','count']]
df9 = df8.drop_duplicates()

df_std = pd.read_sql('report_data_extract_fielddesc',engine)
table_ids = df_std.table_id.unique()
std_table_attr = {}
for id in table_ids:
    verbose_names = list(df_std[df_std.table_id==id].f_verbose_name)
    std_table_attr[str(id)] = verbose_names

for index_std, no in zip(df9.index_std, df9.no):
    if index_std == '':
        continue
    index_std = re.sub('nan', '"标准名称"', index_std)
    try:
        test_index_std = eval(index_std)
        print(test_index_std)
        for table_id in std_table_attr:
            if compare_list_equal(test_index_std,std_table_attr[table_id]):
                print('找到相同的表：',table_id,std_table_attr[table_id])
                break
            else:
                if compare_list_similar(test_index_std,std_table_attr[table_id]):
                    print('找到相似的表',table_id,std_table_attr[table_id])
                    break
                else:
                    pass
    except Exception:
        print('没有转换成功{}'.format(index_std))
        continue
