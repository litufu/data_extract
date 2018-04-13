# _author : litufu
# date : 2018/4/6

import re

def remove_space_from_df(df):
    '''

    :param df: DataFrame
    :return: 去除单元格中数据的空格
    '''
    pattern = re.compile(r'\s+')
    df = df.applymap(lambda x: pattern.sub('', str(x)))
    return df

def remove_per_after_num(cell):
    '''
    去重数字后面的百分号
    :param df:
    :return: 去除百分号的数字
    '''
    pattern = re.compile(r'-{0,1}\d+\.{0,1}\d*%')
    ret = pattern.match(str(cell))
    if ret:
        cell = re.sub(r'%','',ret[0])
    return cell

def remove_per_from_df(df):
    '''

    :param df: DataFrame
    :return: 去除数字后的百分号的df
    '''
    df = df.applymap(lambda x: remove_per_after_num(x))
    return df

