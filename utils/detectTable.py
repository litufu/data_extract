# _author : litufu
# date : 2018/5/25
import pandas as pd
import re
from utils.mytools import is_num
import numpy as np
import json

class NotDataFrameException(Exception):
    def __init__(self,err='非pd.DataFrame格式'):
        Exception.__init__(self,err)

class NoFoundIndexException(Exception):
    def __init__(self,err='未找到索引'):
        Exception.__init__(self,err)

CN_PATTERN = re.compile("([\u4e00-\u9fff]+)")
NUM_PATTERN = re.compile("^[\d,.]*?$")

def drop_na_except_first_line(df):
    '''
    扣除第一行后再删除nan值
    :param df:
    :return: df,删除nan值后的df
    '''
    columns_length = len(df.columns)
    df_drop_first_line = df.iloc[1:, :]
    drop_columns = []
    for i in range(columns_length):
        values = list(set(list(df_drop_first_line.iloc[:, i])))
        if len(values) == 1 and (values[0] == 'nan' or values[0]==np.nan):
            drop_columns.append(i)
    if len(drop_columns) > 0:
        df = df.drop(drop_columns, axis=1)

    return df

def detect_columns(df):
    '''
    检测索引的索引
    :param df:
    :return:
    '''
    if not isinstance(df,pd.DataFrame):
        raise NotDataFrameException

    df = df.dropna(axis=1,how='all')

    columns_length = len(df.columns)
    df_length = len(df)
    if df_length>= 1:
        first_line = df.iloc[0,:]
        if len(set(first_line)) == columns_length:
            return list(first_line)
        else:
            df = drop_na_except_first_line(df)
            columns_length = len(df.columns)
            first_line = df.iloc[0, :]
            if len(set(first_line)) == columns_length:
                return list(first_line)
            else:
                if df_length >= 2:
                    second_line = df.iloc[1,:]
                    if True in [is_num(item) for item in second_line]:
                        return None
                    else:
                        first_second = list(zip(list(first_line),list(second_line)))
                        if len(set(first_second)) == columns_length:
                            return list(first_second)
                        else:
                            if df_length >= 3:
                                third_line = df.iloc[2, :]
                                if True in [is_num(item) for item in third_line]:
                                    return None
                                else:
                                    first_second_third = list(zip(list(first_line), list(second_line),list(third_line)))
                                    if len(set(first_second_third)) == columns_length:
                                        return list(first_second_third)
                                    else:
                                        return None
                            else:
                                return None
                else:
                    return None
    else:
        return None

def detect_indexes(df):
    if not isinstance(df,pd.DataFrame):
        raise NotDataFrameException
    indexes = list(df.iloc[:,0])
    result = None
    for key,value in enumerate(indexes):
        if value == 'nan' or value == np.nan:
            continue
        else:
            try:
                result =  indexes[key:]
            except Exception:
                result = indexes[key:]
            break

    return result
