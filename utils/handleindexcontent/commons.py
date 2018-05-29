# _author : litufu
# date : 2018/5/16
import re
import numpy as np
import pandas as pd
from utils.mytools import remove_per_from_df,remove_space_from_df,combine_table_to_first
from utils.detectTable import detect_columns,detect_indexes

class NoTupleException(Exception):
    def __init__(self,err='不是元祖'):
        Exception.__init__(self,err)

def recognize_instucti(indexcontent):
    df = None
    instructi = []
    unit = '元'
    pattern0 = re.compile('^.*?单位[：:](.*?)$')
    for content in indexcontent:
        for classify, item in content.items():
            if classify == 'c' and len(item) > 0:
                for tables in item:
                    for table in tables:
                        if isinstance(table,str):
                            continue
                        df = remove_per_from_df(remove_space_from_df(table))
                        print(df)
                        print('提取的列索引是{}'.format(detect_columns(df)))
                        print('提取的行索引是{}'.format(detect_indexes(df)))
                        instructi.append(df.to_string())
            elif classify == 't' and len(item) > 0:
                if pattern0.match(item):
                    unit = pattern0.match(item).groups()[0]
                else:
                    ret = re.sub('.*?.适用.不适用', '', item)
                    if ret != '':
                        instructi.append(ret)
            else:
                pass

    return df, unit, ''.join(instructi)

def recognize_df_and_instucti(indexcontent):
    dfs = []
    instructi = []
    unit = '元'
    pattern0 = re.compile('^.*?单位[：:](.{0,3}元).*?$')
    for k, content in enumerate(indexcontent):
        for classify, item in content.items():
            if classify == 'c' and len(item) > 0:
                if len(item)>1:
                    item = combine_table_to_first(item)
                for tables in item:
                    for table in tables:
                        df = remove_per_from_df(remove_space_from_df(table))
                        print(df)
                        print('提取的列索引是{}'.format(detect_columns(df)))
                        print('提取的行索引是{}'.format(detect_indexes(df)))
                        dfs.append(df)
            elif classify == 't' and len(item) > 0:
                if pattern0.match(item):
                    unit = pattern0.match(item).groups()[0]
                else:
                    ret = re.sub('.*?.适用.不适用', '', item)
                    if ret != '':
                        instructi.append(ret)
            else:
                pass

    if len(dfs) == 1:
        df = dfs[0]
    elif len(dfs) == 0:
        df = None
    elif len(dfs)>1:
        raise Exception
        # df = dfs
    else:
        raise Exception

    return df, unit, ''.join(instructi)

def save_instructi(instructi,modelname,stk_cd_id,acc_per,filedname):
    '''保存普通说明'''
    if len(instructi) > 0:
        if modelname.objects.filter(stk_cd_id=stk_cd_id, acc_per=acc_per):
            obj = modelname.objects.get(stk_cd_id=stk_cd_id, acc_per=acc_per)
            setattr(obj,filedname,instructi)
            obj.save()
        else:
            obj = modelname.objects.create(
                stk_cd_id=stk_cd_id,
                acc_per=acc_per,
            )
            setattr(obj, filedname, instructi)
            obj.save()
    else:
        pass

def save_combine_instructi(instructi,modelname,stk_cd_id,acc_per,typ_rep_id,filedname):
    '''保存附注说明'''
    if len(instructi) > 0:
        if modelname.objects.filter(stk_cd_id=stk_cd_id, acc_per=acc_per,typ_rep_id=typ_rep_id):
            obj = modelname.objects.get(stk_cd_id=stk_cd_id, acc_per=acc_per,typ_rep_id=typ_rep_id)
            setattr(obj,filedname,instructi)
            obj.save()
        else:
            obj = modelname.objects.create(
                stk_cd_id=stk_cd_id,
                acc_per=acc_per,
                typ_rep_id=typ_rep_id,
            )
            setattr(obj, filedname, instructi)
            obj.save()
    else:
        pass

def compute_start_pos(df):
    start_pos = []
    pattern = re.compile('^[-\d\.,%]*?$')
    for i in range(len(df.columns)):
        if df.iloc[:,i].str.match(pattern).any():
            start_pos = list(np.where(df.iloc[:, i].str.match(pattern) | df.iloc[:, i].str.match('nan'))[0])
    return start_pos

def get_values(df,start_pos,value_pos,value_type='d'):
    data_length = len(df.iloc[start_pos[0]:, :])
    if type(value_pos) is list:
        if value_type == 't':
            values = list(df.iloc[start_pos[0]:, value_pos[0]]) if len(value_pos) > 0 \
                else ['' for i in range(data_length)]
        elif value_type == 'd':
            values = list(df.iloc[start_pos[0]:, value_pos[0]]) if len(value_pos) > 0 \
                else [0.00 for i in range(data_length)]
        elif value_type == 'i':
            values = list(df.iloc[start_pos[0]:, value_pos[0]]) if len(value_pos) > 0 \
                else [0 for i in range(data_length)]
        else:
            raise Exception
    elif (type(value_pos)) is int or (type(value_pos) is np.int64):
        if value_type == 't':
            values = list(df.iloc[start_pos[0]:, value_pos]) if value_pos < len(df.columns) \
                else ['' for i in range(data_length)]
        elif value_type == 'd':
            values = list(df.iloc[start_pos[0]:, value_pos]) if value_pos < len(df.columns)  \
                else [0.00 for i in range(data_length)]
        elif value_type == 'i':
            values = list(df.iloc[start_pos[0]:, value_pos]) if value_pos < len(df.columns)  \
                else [0 for i in range(data_length)]
        else:
            raise Exception
    else:
        raise Exception

    return values


def get_dfs(classify,item):
    '''
    从内容中提取多个表格
    :param classify:
    :param item:
    :return:
    '''

    if not isinstance(classify,tuple):
        raise NoTupleException


    dfs = {}
    tables = []
    for table in item:
        if not isinstance(table, str):
            first_df = table[0]
            dfs['first'] = remove_per_from_df(remove_space_from_df(first_df))
            break

    for i in item:
        if isinstance(i, str):
            tables.append(i)
        elif isinstance(i, list):
            tables.append(i)
        else:
            raise Exception

    tables_length = len(tables)
    texts = [i for i in tables if isinstance(i,str)]
    for c in classify:
        for t in texts:
            if c in t:
                c = t
                break

        if (c in tables) and ((tables.index(c) + 1) < tables_length) and isinstance(tables[tables.index(c) + 1][0],pd.DataFrame):
            dfs[c] = remove_per_from_df(remove_space_from_df(tables[tables.index(c) + 1][0]))

    return dfs







