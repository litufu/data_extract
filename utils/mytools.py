# _author : litufu
# date : 2018/4/14
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import Levenshtein
import re
import requests
from bs4 import BeautifulSoup
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
import inspect
from report_data_extract import models

class NotFoundHandleClassException(Exception):
    def __init__(self,err='没有发现索引处理函数'):
        Exception.__init__(self,err)

def similar(seq1, seq2):
    if len(seq1)>len(seq2):
        return Levenshtein.ratio(seq1[:len(seq2)], seq2) > 0.55
    else:
        return Levenshtein.ratio(seq1, seq2[:len(seq1)]) > 0.55
    #是否seq2被截断了，导致seq1和seq2不一致，因此对seq1进行截断操作

def similar_list(list1,list2):
    '''寻找两个列表中所有的相似元素
    list1中有多少个元素和list2中的相似
    '''
    similar_lst = []
    for item1 in list1:
        for item2 in list2:
            if similar(item1,item2):
                similar_lst.append(item1)
                break
    return similar_lst

def similar_item_with_list(item,list):
    '''
    判断某个元素是否与列表中的某个元素相似
    :param item:
    :param list:
    :return:
    '''
    for i in list:
        if similar(item,i):
            list.remove(i)
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

class HandleIndexContent(object):

    def __init__(self,stk_cd_id,acc_per,indexno, indexcontent):
        self.indexno = indexno
        self.indexcontent = indexcontent
        self.stk_cd_id = stk_cd_id
        self.acc_per = acc_per

    def check(self):
        '''
        检查表是否正确
        :return:
        '''
        try:
            self.recognize()
            self.converse()
            self.logic()
            self.save()
        except Exception as e:
            self.error_info()
            raise Exception

    def recognize(self):
        '''
        识别表
        :return:
        '''
        pass


    def converse(self):
        '''
        转化表
        :return:
        '''
        pass

    def logic(self):
        '''
        表逻辑检验
        :return:
        '''
        pass


    def save(self):
        '''
        存储表
        :return:
        '''
        pass


    def error_info(self):
        print("%s.%s ******"%(self.__class__.__name__[1:], self.indexno))


def registr(no,name):
    '''
    登记索引及对应的处理函数名称
    :param no: 索引编号
    :param name: 处理函数
    :return:
    '''

    index_id = models.StdContentIndex.objects.get(no=no).id
    if models.IndexHandleMethod.objects.filter(indexno_id=index_id):
        obj = models.IndexHandleMethod.objects.get(indexno_id=index_id)
        obj.handle_classname = name
        obj.save()
    else:
        models.IndexHandleMethod.objects.create(indexno_id=index_id,handle_classname=name)

def registr_table(tablename,table_cn_name):
    if models.StandardTables.objects.filter(tablename=tablename):
        pass
    else:
        models.StandardTables.objects.create(tablename=tablename,table_cn_name=table_cn_name)

def is_num(s):
    s = str(s)
    pattern = re.compile('^.*?\d+.*?$')
    if pattern.match(s):
        return True
    else:
        return False

def get_item_in_df_pos(item,df,similar=True):
    if similar == True:
        for i in range(len(df)):
            for j,value in enumerate(list(df.iloc[i,:])):
                if item in value:
                    return i,j
    else:
        for i in range(len(df)):
            for j, value in enumerate(list(df.iloc[i, :])):
                if item == value:
                    return i, j
    return None





if __name__ == '__main__':
    # registr('0205000000','pass')
    #新增索引及对应的处理类
    registr('0b090100','pass')
    # print(toClassname(cnToEn('其他对投资者决策有影响的重要交易和事项')))
    # print(toFiledname(cnToEn('报告分部的财务信息')))
    # 新增表记录，每当新增一个标准表时使用
    # registr_table('MajorOverseaAsset','公司主要境外资产')


