#!/usr/bin/python
# -*- coding: utf-8 -*-

# _author : litufu
# date : 2018/5/23

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
from collections import Counter
import re
from report_data_extract import models
from utils.mytools import similar_item_with_list_without_remove

def get_std_index(market,fatherno,level):
    objs = models.StdContentIndex.objects.filter(market=market,fatherno=fatherno,level=level).all()
    return objs

def get_index_format(rp_t_df_cells,market,fatherno,level):
    print(rp_t_df_cells)
    indexes = [obj.name for obj in get_std_index(market, fatherno, level)]
    len_indexes = len(indexes)
    pattern = re.compile('[第\(（一二三四五六七八九十\d）\)节\.、]*')
    # pattern = re.compile('[第\(（一二三四五六七八九十\d\)）节\.、]*')
    pattern_upper = re.compile('[一二三四五六七八九十]+')
    pattern_lower = re.compile('\d+')

    #计算可能的索引
    ret = []
    for cell_text in rp_t_df_cells.cellText:
        span = pattern.match(cell_text).span()
        if span[0] == 0 and span[1] >0:
            sub_cell_text = re.sub(pattern, '', cell_text)
            if similar_item_with_list_without_remove(sub_cell_text,indexes) is not None:
                ret.append(cell_text)

    #计算可能索引的格式
    results = []
    for item in ret:
        span = pattern.match(item).span()
        num = item[span[0]:span[1]]
        sub_num = re.sub(pattern_upper, '([一二三四五六七八九十]+)', num)
        sub_num = re.sub(pattern_lower, '(\d+)', sub_num)
        results.append(sub_num)

    if len(results) == 0:
        return None
    #计算最有可能的索引格式，即最接近标准索引长度的格式
    ret_pattern = None
    count_ret = Counter(results)
    index_length_compare = [abs(value - len_indexes) for value in count_ret.values()]
    min_index_length_compare = min(index_length_compare)
    for key, compare in enumerate(index_length_compare):
        if compare == min_index_length_compare:
            ret_pattern = re.compile('^' + list(count_ret.keys())[key] + '(.*?)$')

    return ret_pattern

