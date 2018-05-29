# _author : litufu
# date : 2018/4/14
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import Levenshtein
import re
from functools import wraps
import time
import pandas as pd
from decimal import Decimal
import requests
from bs4 import BeautifulSoup
from django.db import transaction
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
import inspect
BASE_DIR =os.path.dirname(os.path.abspath(__file__))

def func_timer(function):
    '''
    用装饰器实现函数计时
    :param function: 需要计时的函数
    :return: None
    '''
    @wraps(function)
    def function_timer(*args, **kwargs):
        print('[Function: {name} start...]'.format(name = function.__name__))
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print('[Function: {name} finished, spent time: {time:.2f}s]'.format(name = function.__name__,time = t1 - t0))
        return result
    return function_timer

class NotFoundHandleClassException(Exception):
    def __init__(self,err='没有发现索引处理函数'):
        Exception.__init__(self,err)

def similar(seq1, seq2,per=0.8):
    if len(seq1)>len(seq2):
        return Levenshtein.ratio(seq1[:len(seq2)], seq2) > per
    else:
        return Levenshtein.ratio(seq1, seq2[:len(seq1)]) > per
    #是否seq2被截断了，导致seq1和seq2不一致，因此对seq1进行截断操作

def similar_list(list1,list2,per):
    '''寻找两个列表中所有的相似元素
    list1中有多少个元素和list2中的相似
    '''
    similar_lst = []
    for item1 in list1:
        for item2 in list2:
            if similar(item1,item2,per):
                similar_lst.append(item1)
                break
    return similar_lst

def similar_item_with_list(item,list,per=0.8):
    '''
    判断某个元素是否与列表中的某个元素相似
    :param item:
    :param list:
    :return:
    '''
    for i in list:
        if similar(item,i,per):
            list.remove(i)
            return i
    return None

def similar_item_with_list_without_remove(item,list,per=0.8):
    '''
    判断某个元素是否与列表中的某个元素相似
    :param item:
    :param list:
    :return:
    '''
    for i in list:
        if similar(item,i,per):
            return i
    return None

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
    去除数字后面的百分号
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

def cnToArab(x):
    '''
    将大写汉字转换为数字
    :param x: 汉字数字，只转换一到九十九
    :return: 阿拉伯数字
    '''
    comparison_sheet= {'一':'1','二':'2','三':'3','四':'4','五':'5','六':'6','七':'7','八':'8','九':'9','十':'10'}
    comparison_sheet1 = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9',
                        '十': '1'}
    comparison_sheet2 = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9',
                         '十': '0'}
    if re.match('\d+',x):
        return int(x)
    else:
        if len(x)==1:
            return int(comparison_sheet[x])
        elif len(x)==2:
            if x not in ['二十','三十','四十','五十','六十','七十','八十','九十',] :
                return int(comparison_sheet1[x[0]]+comparison_sheet1[x[1]])
            else:
                return int(comparison_sheet2[x[0]] + comparison_sheet2[x[1]])
        elif len(x)==3:
            return int(comparison_sheet1[x[0]]+comparison_sheet1[x[2]])
        else:
            raise Exception

def compute_num_list(celltexts,pattern):
    #获取汉字序号
    cn_num = list(map(lambda x: pattern.match(x).groups()[0],celltexts))
    # 将汉字序号转换为阿拉伯数字
    arab_num = list(map(cnToArab,cn_num))
    return arab_num

def compare_num_list(num_list):
    '''检查序列数字的完整性'''
    comp = len(set([(k - int(v)) for k, v in enumerate(num_list)]))
    return comp

def check_if_pure_digital(s):
    '''检查是否为纯数字'''
    pattern = re.compile('^\-?\(?(\d+,?)+\.?\d*%?\)?$')
    ret = pattern.match(s)
    if ret:
        return True
    else:
        return False

def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except:
        print("Get HTML Text Failed!")
        return 0


def enToCn(to_translate, from_language="en", to_language="ch-CN"):
    # 根据参数生产提交的网址
    base_url = "https://translate.google.cn/m?hl={}&sl={}&ie=UTF-8&q={}"
    url = base_url.format(to_language, from_language, to_translate)

    # 获取网页
    html = getHTMLText(url)
    if html:
        soup = BeautifulSoup(html, "html.parser")

    # 解析网页得到翻译结果
    try:
        result = soup.find_all("div", {"class": "t0"})[0].text
    except:
        print("Translation Failed!")
        result = ""

    return result


def cnToEn(to_translate, from_language="ch-CN", to_language="en"):
    # 根据参数生产提交的网址
    base_url = "https://translate.google.cn/m?hl={}&sl={}&ie=UTF-8&q={}"
    url = base_url.format(to_language, from_language, to_translate)

    # 获取网页
    html = getHTMLText(url)
    if html:
        soup = BeautifulSoup(html, "html.parser")

    # 解析网页得到翻译结果
    try:
        result = soup.find_all("div", {"class": "t0"})[0].text
    except:
        print("Translation Failed!")
        result = ""


    return result


def toFiledname(name):
    porter = PorterStemmer()
    # lancaster = LancasterStemmer()
    # ret = '_'.join([lancaster.stem(w) for w in re.split('\s+',result.lower())])
    ret = '_'.join([porter.stem(w) for w in re.split('\s+', name.lower())])
    if len(ret)>30:
        ret = ret[:30]
    return ret

def toClassname(name):
    porter = PorterStemmer()
    # lancaster = LancasterStemmer()
    # ret = '_'.join([lancaster.stem(w) for w in re.split('\s+',result.lower())])
    ret = ''.join([str.capitalize(porter.stem(w)) for w in re.split('\s+', name.lower())])
    if len(ret)>30:
        ret = ret[:30]
    return ret


def get_current_function_name():
    return inspect.stack()[1][3]

def is_num(s):
    s = str(s)
    s = re.sub('\s+','',s)
    pattern = re.compile('^[\d,\.]+?$')
    if pattern.match(s):
        return True
    else:
        return False

def num_to_decimal(num,unit=None):
    unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
    if unit == None or (unit not in unit_change):
        return Decimal(re.sub(',', '', str(num))) if is_num(num) else 0.00
    else:
        return Decimal(re.sub(',', '', str(num))) * unit_change[unit] if is_num(num) else 0.00

def get_item_in_df_pos(item,df,similar=True):
    if similar == True:
        for i in range(len(df)):
            for j,value in enumerate(list(df.iloc[i,:])):
                if type(value) is not str:
                    value = ''
                if item in value:
                    return i,j
    else:
        for i in range(len(df)):
            for j, value in enumerate(list(df.iloc[i, :])):
                if type(value) is not str:
                    value = ''
                if item == value:
                    return i, j
    return None


def comput_no(numbers,level,names,fatherno='',num_len=10):
    '''
    自行计算十六进制编码
    :param numbers: 数据库中已经存储的该级别的编码
    :param level: 层次
    :param names: 拟新增的名称列表
    :param fatherno: 父级索引
    :param num_len: 编码长度
    :return:
    '''
    if not isinstance(numbers,list) or not isinstance(names,list) or not isinstance(level,int):
        raise Exception

    # 计算新增内容的编号
    # 1、读取数据库中该级别的最后一个编号
    temp_df = numbers[:]
    if len(temp_df) == 0:
        last_num = 0
    else:
        last_num = max(
            list(pd.Series(temp_df).map(lambda x: x[(level - 1) * 2:(2 * (level))]).map(lambda x: int(x, 16))))
    # 自己编号
    self_num = [str(hex(last_num + i))[2:] for i in range(1, len(names) + 1)]
    # 将自己编号变为固定的长度---2位
    self_num_fixed_length = []
    for num in self_num:
        if len(num) == 1:
            self_num_fixed_length.append('0' + num)
        else:
            self_num_fixed_length.append(num)
    # 2、父级别编号+自己的编号
    whole_num = [fatherno + num for num in self_num_fixed_length]
    # 将编号补成固定位数
    whole_num_fixed_length = [num + ''.join(['0' for i in range(num_len - len(num))]) for num in whole_num]
    selfnos = self_num_fixed_length
    return (selfnos,whole_num_fixed_length)

def compute_lines():
    '''计算处理文件的行数'''
    parts = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh',
             'twelve','commons','base']
    lines_length = 0
    for part in parts:
        part_name = part + '.py'
        path = os.path.join(os.path.join(BASE_DIR, 'handleindexcontent'),  part_name)
        f = open(path,'r',encoding='utf-8')
        temp_length = len(f.readlines())
        f.close()
        lines_length  = lines_length + temp_length
    print(lines_length)

def get_headers_line_num(table):
    line_num = 1
    for i in range(len(table)):
        if True in [is_num(cell) for cell in list(table.iloc[i, :])]:
            line_num = i
            break
        else:
            if i == (len(table)-1):
                line_num = len(table)
    return line_num


def combine_table_to_first(tables):
    '''
    将后面的表并到前面的表头
    :param tables:
    :return:
    '''
    if len(tables) > 1:
        result_tables = []
        headers = None
        for table in tables:
            if not isinstance(table, str):
                first_df = table[0]
                headers = first_df.iloc[:get_headers_line_num(first_df),:]
                break
        for key, table in enumerate(tables):
            if isinstance(table, str):
                result_tables.append(table)
            else:
                if key == 0:
                    result_tables.append(table)
                else:
                    df = pd.concat([headers,table[0]],ignore_index=True) if headers is not None else table[0]
                    result_tables.append([df])
        return result_tables
    else:
        return tables

if __name__ == '__main__':
    compute_lines()
    # print(similar('金流量表补充资料','现金流量表补充资料'))

    # registr('0205000000','pass')
    #新增索引及对应的处理类
    # registr('0b052500','pass')
    # print(toClassname(cnToEn('担保分析说明')))
    # print(toFiledname(cnToEn('违规担保')))
    # 新增表记录，每当新增一个标准表时使用
    # registr_table('MajorOverseaAsset','公司主要境外资产')


