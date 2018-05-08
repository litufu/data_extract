# _author : litufu
# date : 2018/4/27

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import re
import numpy as np
from utils.mytools import HandleIndexContent,remove_space_from_df,remove_per_from_df,similar
from report_data_extract import models
from decimal import Decimal
import decimal
from collections import OrderedDict
from itertools import chain
import pandas as pd


class ChangInShareholdAndRemuner(HandleIndexContent):
    '''
    现任及报告期内离任董事、监事和高级管理人员持股变动及报酬情况
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInShareholdAndRemuner, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0801010000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('职务').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                else:
                                    pass

                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.*?.适用.不适用', '', item)
                            if ret != '':
                                instructi.append(ret)
                    else:
                        pass
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if df is not None and len(df)>0:
            pattern = re.compile('^.*?报告期内从公司获得的税前报酬总额（(.*?元)）.*?$')
            unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
            name_pos = list(np.where(df.iloc[0, :].str.contains('姓名'))[0])
            job_titl_pos = list(np.where(df.iloc[0, :].str.contains('职务'))[0])
            sex_pos = list(np.where(df.iloc[0, :].str.contains('性别'))[0])
            age_pos = list(np.where(df.iloc[0, :].str.contains('年龄'))[0])
            term_start_date_pos = list(np.where(df.iloc[0, :].str.contains('任期起始日期'))[0])
            term_end_date_pos = list(np.where(df.iloc[0, :].str.contains('任期终止日期'))[0])
            share_held_num_begin_pos = list(np.where(df.iloc[0, :].str.contains('初持股数'))[0])
            share_held_num_end_pos = list(np.where(df.iloc[0, :].str.contains('末持股数'))[0])
            increas_or_decreas_num_pos = list(np.where(df.iloc[0, :].str.contains('增减变动量'))[0])
            change_reason_pos = list(np.where(df.iloc[0, :].str.contains('增减变动原因'))[0])
            pre_tax_compens_pos = list(np.where(df.iloc[0, :].str.contains('报告期内从公司获得的税前报酬总额'))[0])
            is_get_compens_from_relat_pos = list(np.where(df.iloc[0, :].str.contains('是否在公司关联方获取报酬'))[0])
            total_pos = list(np.where(df.iloc[:,0].str.contains('合计'))[0])
            unit = pattern.match(df.iloc[0,pre_tax_compens_pos[0]]).groups()[0]
            work_experi_dict = {}
            if len(df)>total_pos[0]+1:
                name_a_pos = list(np.where(df.iloc[(total_pos[0]+1), :].str.contains('姓名'))[0])
                work_experi_pos = list(np.where(df.iloc[(total_pos[0]+1), :].str.contains('主要工作经历'))[0])
                name_as = list(df.iloc[(total_pos[0]+2):,name_a_pos[0]])
                work_experis = list(df.iloc[(total_pos[0]+2):,work_experi_pos[0]])
                work_experi_dict = dict(zip(name_as,work_experis))

            names = list(df.iloc[1:total_pos[0], name_pos[0]])
            job_titls = list(df.iloc[1:total_pos[0], job_titl_pos[0]])
            sexs = list(df.iloc[1:total_pos[0], sex_pos[0]])
            ages = list(df.iloc[1:total_pos[0], age_pos[0]])
            term_start_dates = list(df.iloc[1:total_pos[0], term_start_date_pos[0]])
            term_end_dates = list(df.iloc[1:total_pos[0], term_end_date_pos[0]])
            share_held_num_begins = list(df.iloc[1:total_pos[0], share_held_num_begin_pos[0]])
            share_held_num_ends = list(df.iloc[1:total_pos[0], share_held_num_end_pos[0]])
            increas_or_decreas_nums = list(df.iloc[1:total_pos[0], increas_or_decreas_num_pos[0]])
            change_reasons = list(df.iloc[1:total_pos[0], change_reason_pos[0]])
            pre_tax_compenses = list(df.iloc[1:total_pos[0], pre_tax_compens_pos[0]])
            is_get_compens_from_relats = list(df.iloc[1:total_pos[0], is_get_compens_from_relat_pos[0]])

            for (name,job_titl,sex,age,term_start_date,term_end_date,share_held_num_begin, \
                           share_held_num_end,increas_or_decreas_num,change_reason,pre_tax_compens, \
                           is_get_compens_from_relat) \
                    in zip(names,job_titls,sexs,ages,term_start_dates,term_end_dates,share_held_num_begins, \
                           share_held_num_ends,increas_or_decreas_nums,change_reasons,pre_tax_compenses, \
                           is_get_compens_from_relats):
                if models.ChangInShareholdAndRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                         name=name):
                    obj = models.ChangInShareholdAndRemuner.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                             name=name)
                    obj.name = name
                    obj.job_titl = job_titl
                    obj.sex = sex
                    obj.age = age
                    obj.term_start_date = term_start_date
                    obj.term_end_date = term_end_date
                    obj.share_held_num_begin = share_held_num_begin if share_held_num_begin != 'nan' else 0
                    obj.share_held_num_end = share_held_num_end if share_held_num_end != 'nan' else 0
                    obj.increas_or_decreas_num = increas_or_decreas_num if increas_or_decreas_num != 'nan' else 0
                    obj.change_reason = change_reason
                    obj.pre_tax_compens = Decimal(re.sub(',','',str(pre_tax_compens)))*unit_change[unit]
                    obj.is_get_compens_from_relat = is_get_compens_from_relat
                    if work_experi_dict.get(name) is not None:
                        obj.work_experi = work_experi_dict.get(name)
                    else:
                        obj.work_experi = ''
                    obj.save()
                else:
                    models.ChangInShareholdAndRemuner.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        name=name,
                        job_titl=job_titl,
                        sex=sex,
                        age=age,
                        term_start_date=term_start_date,
                        term_end_date=term_end_date,
                        share_held_num_begin=share_held_num_begin if share_held_num_begin != 'nan' else 0,
                        share_held_num_end=share_held_num_end if share_held_num_end != 'nan' else 0,
                        increas_or_decreas_num=increas_or_decreas_num if increas_or_decreas_num != 'nan' else 0,
                        change_reason=change_reason,
                        pre_tax_compens= Decimal(re.sub(',','',str(pre_tax_compens)))*unit_change[unit],
                        is_get_compens_from_relat=is_get_compens_from_relat,
                        work_experi = work_experi_dict.get(name) if work_experi_dict.get(name) is not None else ''
                    )

class ChangInShareholdSZ(HandleIndexContent):
    '''
    董事、监事和高级管理人员持股变动
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInShareholdSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['08010000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('职务').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                else:
                                    pass

                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.*?.适用.不适用', '', item)
                            if ret != '':
                                instructi.append(ret)
                    else:
                        pass
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if df is not None and len(df)>0:
            name_pos = list(np.where(df.iloc[0, :].str.contains('姓名'))[0])
            job_titl_pos = list(np.where(df.iloc[0, :].str.contains('职务'))[0])
            sex_pos = list(np.where(df.iloc[0, :].str.contains('性别'))[0])
            age_pos = list(np.where(df.iloc[0, :].str.contains('年龄'))[0])
            term_start_date_pos = list(np.where(df.iloc[0, :].str.contains('任期起始日期'))[0])
            term_end_date_pos = list(np.where(df.iloc[0, :].str.contains('任期终止日期'))[0])
            share_held_num_begin_pos = list(np.where(df.iloc[0, :].str.contains('初持股数'))[0])
            share_held_num_end_pos = list(np.where(df.iloc[0, :].str.contains('末持股数'))[0])
            increas_share = list(np.where(df.iloc[0, :].str.contains('增持股份'))[0])
            decreas_share = list(np.where(df.iloc[0, :].str.contains('减持股份'))[0])
            other_change_share = list(np.where(df.iloc[0, :].str.contains('其他增减变动'))[0])

            df = df.drop([0,len(df)-1])

            names = list(df.iloc[:, name_pos[0]])
            job_titls = list(df.iloc[:, job_titl_pos[0]])
            sexs = list(df.iloc[:, sex_pos[0]])
            ages = list(df.iloc[:, age_pos[0]])
            term_start_dates = list(df.iloc[:, term_start_date_pos[0]])
            term_end_dates = list(df.iloc[:, term_end_date_pos[0]])
            share_held_num_begins = list(df.iloc[:, share_held_num_begin_pos[0]])
            share_held_num_ends = list(df.iloc[:, share_held_num_end_pos[0]])
            increas_shares = list(df.iloc[:, increas_share[0]])
            decreas_shares = list(df.iloc[:, decreas_share[0]])
            other_change_shares = list(df.iloc[:, other_change_share[0]])

            for (name,job_titl,sex,age,term_start_date,term_end_date,share_held_num_begin, \
                           share_held_num_end,increas_share,decreas_share,other_change_share) \
                    in zip(names,job_titls,sexs,ages,term_start_dates,term_end_dates,share_held_num_begins, \
                           share_held_num_ends,increas_shares,decreas_shares,other_change_shares):
                if name == 'nan':
                    continue
                increas_share = increas_share if increas_share != 'nan' else 0
                decreas_share = decreas_share if decreas_share != 'nan' else 0
                other_change_share = other_change_share if other_change_share != 'nan' else 0
                # print('increas_share',increas_share,type(increas_share),int(increas_share))
                # print('decreas_share',decreas_share,type(decreas_share),int(decreas_share))
                # print('other_change_share',other_change_share,type(other_change_share))
                if models.ChangInShareholdAndRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                         name=name,job_titl=job_titl,age=age):
                    obj = models.ChangInShareholdAndRemuner.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                             name=name,job_titl=job_titl,age=age)
                    obj.name = name
                    obj.job_titl = job_titl
                    obj.sex = sex
                    obj.age = age
                    obj.term_start_date = term_start_date
                    obj.term_end_date = term_end_date
                    obj.share_held_num_begin = share_held_num_begin if share_held_num_begin != 'nan' else 0
                    obj.share_held_num_end = share_held_num_end if share_held_num_end != 'nan' else 0
                    obj.increas_or_decreas_num = int(increas_share)- int(decreas_share)+int(other_change_share)
                    obj.save()
                else:
                    models.ChangInShareholdAndRemuner.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        name=name,
                        job_titl=job_titl,
                        sex=sex,
                        age=age,
                        term_start_date=term_start_date,
                        term_end_date=term_end_date,
                        share_held_num_begin=share_held_num_begin if share_held_num_begin != 'nan' else 0,
                        share_held_num_end=share_held_num_end if share_held_num_end != 'nan' else 0,
                        increas_or_decreas_num=int(increas_share)- int(decreas_share)+int(other_change_share)
                    )

class ExecutIntroduct(HandleIndexContent):
    '''
       现任及报告期内离任董事、监事和高级管理人员持股变动及报酬情况
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ExecutIntroduct, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructis = {}
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['08030000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('股东单位').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['shareheld_com'] = df
                                if table.iloc[0, :].str.contains('其他单位').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['other_com'] = df
                                else:
                                    pass

                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.适用.不适用', '', item)
                            if ret != '' and '公司现任董事、监事、高级管理人员专业背景、主要工作经历以及目前在公司的主要职责' in ret:
                                instructis['execut_introduct'] = ret
                            elif ret != '' and '公司现任及报告期内离任董事、监事和高级管理人员近三年证券监管机构处罚的情况' in ret:
                                instructis['execut_punish'] = ret
                            else:
                                pass
                    else:
                        pass
        else:
            pass

        return dfs, unit, instructis

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs, unit, instructis = self.recognize()
        if dfs.get('shareheld_com') is not None:
            df = dfs.get('shareheld_com')
            name_pos = list(np.where(df.iloc[0, :].str.contains('任职人员姓名'))[0])
            name_of_sharehold_pos = list(np.where(df.iloc[0, :].str.contains('股东单位名称'))[0])
            job_titl_in_sharehold_com_pos = list(np.where(df.iloc[0, :].str.contains('在股东单位担任的职务'))[0])
            start_date_in_sharehold_com_pos = list(np.where(df.iloc[0, :].str.contains('任期起始日期'))[0])
            end_date_in_sharehold_com_pos = list(np.where(df.iloc[0, :].str.contains('任期终止日期'))[0])

            df = df.drop([0, len(df) - 1])
            names = list(df.iloc[:, name_pos[0]])
            name_of_shareholds = list(df.iloc[:, name_of_sharehold_pos[0]])
            job_titl_in_sharehold_coms = list(df.iloc[:, job_titl_in_sharehold_com_pos[0]])
            start_date_in_sharehold_coms = list(df.iloc[:, start_date_in_sharehold_com_pos[0]])
            end_date_in_sharehold_coms = list(df.iloc[:, end_date_in_sharehold_com_pos[0]])
            values = list(zip(name_of_shareholds, job_titl_in_sharehold_coms, start_date_in_sharehold_coms,
                              end_date_in_sharehold_coms))
            work_in_sharehold_unit_dict = dict(zip(names, values))

            for (name, name_of_sharehold, job_titl_in_sharehold_com, \
                 start_date_in_sharehold_com, end_date_in_sharehold_com) \
                    in zip(names, name_of_shareholds, job_titl_in_sharehold_coms, \
                           start_date_in_sharehold_coms, end_date_in_sharehold_coms):
                if models.ChangInShareholdAndRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                    name=name):
                    obj = models.ChangInShareholdAndRemuner.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                        name=name)
                    obj.name = name
                    obj.name_of_sharehold = work_in_sharehold_unit_dict[name][0]
                    obj.job_titl_in_sharehold_com = work_in_sharehold_unit_dict[name][1]
                    obj.start_date_in_sharehold_com = work_in_sharehold_unit_dict[name][2]
                    obj.end_date_in_sharehold_com = work_in_sharehold_unit_dict[name][3]
                    obj.save()
                else:
                    models.ChangInShareholdAndRemuner.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        name=name,
                        name_of_sharehold=work_in_sharehold_unit_dict[name][0],
                        job_titl_in_sharehold_com=work_in_sharehold_unit_dict[name][1],
                        start_date_in_sharehold_com=work_in_sharehold_unit_dict[name][2],
                        end_date_in_sharehold_com=work_in_sharehold_unit_dict[name][3]

                    )
        else:
            pass

        if dfs.get('other_com') is not None:
            df = dfs.get('other_com')
            name_pos = list(np.where(df.iloc[0, :].str.contains('任职人员姓名'))[0])
            name_of_sharehold_pos = list(np.where(df.iloc[0, :].str.contains('其他单位名称'))[0])
            job_titl_in_sharehold_com_pos = list(np.where(df.iloc[0, :].str.contains('在其他单位担任的职务'))[0])
            start_date_in_sharehold_com_pos = list(np.where(df.iloc[0, :].str.contains('任期起始日期'))[0])
            end_date_in_sharehold_com_pos = list(np.where(df.iloc[0, :].str.contains('任期终止日期'))[0])

            df = df.drop([0])
            names = list(df.iloc[:, name_pos[0]])
            companys = list(df.iloc[:, name_of_sharehold_pos[0]])
            job_titls = list(df.iloc[:, job_titl_in_sharehold_com_pos[0]])
            start_dates = list(df.iloc[:, start_date_in_sharehold_com_pos[0]])
            end_dates = list(df.iloc[:, end_date_in_sharehold_com_pos[0]])

            for (name, company, job_titl, start_date, end_date) \
                    in zip(names, companys, job_titls, start_dates, end_dates):
                if len(models.ChangInShareholdAndRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                     name=name))==0:
                    pass
                else:
                    obj_name_id = \
                        models.ChangInShareholdAndRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                         name=name)[0].id
                if models.WorkInOtherUnit.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                         name_id=obj_name_id, company=company):
                    obj = models.WorkInOtherUnit.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                             name_id=obj_name_id, company=company)

                    obj.job_titl = job_titl
                    obj.start_date = start_date
                    obj.end_date = end_date
                    obj.save()
                else:
                    models.WorkInOtherUnit.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        name_id=obj_name_id,
                        company=company,
                        job_titl=job_titl,
                        start_date=start_date,
                        end_date=end_date
                    )
        else:
            pass

        if instructis.get('execut_introduct'):
            introduct = instructis.get('execut_introduct')
            introduct_text = re.sub('公司现任董事、监事、高级管理人员专业背景、主要工作经历以及目前在公司的主要职责','',introduct)
            objs = models.ChangInShareholdAndRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
            names = [obj.name for obj in objs]
            split_name = '('+'|'.join(names)+')'
            split_ret = re.split(split_name,introduct_text)
            introduct_dict = {}
            name = ''
            temp_text = []
            for text in split_ret:
                if text in names:
                    if name == '':
                        pass
                    else:
                        introduct_dict[name] = ''.join(temp_text)
                    name = text
                    temp_text = []
                else:
                    if name == '':
                        pass
                    else:
                        temp_text.append(text)
            introduct_dict[name] = temp_text
            for name in introduct_dict:
                if models.ChangInShareholdAndRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                    name=name):
                    obj = models.ChangInShareholdAndRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                        name=name)[0]

                    obj.work_experi = introduct_dict[name]
                    obj.save()
                else:
                    models.ChangInShareholdAndRemuner.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        name=name,
                        work_experi=introduct_dict[name]
                    )
        else:
            pass

        if instructis.get('execut_punish'):
            punish = instructis.get('execut_punish')
            punish_text = re.sub('公司现任及报告期内离任董事、监事和高级管理人员近三年证券监管机构处罚的情况','',punish)
            pass

class ExecutCompens(HandleIndexContent):
    '''
        董事、监事、高级管理人员报酬情况
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ExecutCompens, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['08040000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('报酬').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                else:
                                    pass

                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.*?.适用.不适用', '', item)
                            if ret != '':
                                instructi.append(ret)
                    else:
                        pass
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if df is not None and len(df) > 0:
            unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
            name_pos = list(np.where(df.iloc[0, :].str.contains('姓名'))[0])
            job_titl_pos = list(np.where(df.iloc[0, :].str.contains('职务'))[0])
            sex_pos = list(np.where(df.iloc[0, :].str.contains('性别'))[0])
            age_pos = list(np.where(df.iloc[0, :].str.contains('年龄'))[0])
            pre_tax_compens_pos = list(np.where(df.iloc[0, :].str.contains('从公司获得的税前报酬总额'))[0])
            is_get_compens_from_relat_pos = list(np.where(df.iloc[0, :].str.contains('是否在公司关联方获取报酬'))[0])

            df = df.drop([0,len(df)-1])

            names = list(df.iloc[:, name_pos[0]])
            job_titls = list(df.iloc[:, job_titl_pos[0]])
            sexs = list(df.iloc[:, sex_pos[0]])
            ages = list(df.iloc[:, age_pos[0]])
            pre_tax_compenses = list(df.iloc[:, pre_tax_compens_pos[0]])
            is_get_compens_from_relats = list(df.iloc[:, is_get_compens_from_relat_pos[0]])

            for (name, job_titl, sex, age,  pre_tax_compens, is_get_compens_from_relat) \
                    in zip(names, job_titls, sexs, ages, pre_tax_compenses,is_get_compens_from_relats):
                if models.ChangInShareholdAndRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                    job_titl=job_titl,name=name,age=age):
                    obj = models.ChangInShareholdAndRemuner.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                        job_titl=job_titl,name=name,age=age)
                    obj.name = name
                    obj.job_titl = job_titl
                    obj.sex = sex
                    obj.age = age
                    obj.pre_tax_compens = Decimal(re.sub(',', '', str(pre_tax_compens))) * unit_change[unit]
                    obj.is_get_compens_from_relat = is_get_compens_from_relat
                    obj.save()
                else:
                    models.ChangInShareholdAndRemuner.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        name=name,
                        job_titl=job_titl,
                        sex=sex,
                        age=age,
                        pre_tax_compens=Decimal(re.sub(',', '', str(pre_tax_compens))) * unit_change[unit],
                        is_get_compens_from_relat=is_get_compens_from_relat,
                    )

class WorkInShareholdUnit(HandleIndexContent):
    '''
        在股东单位任职情况
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(WorkInShareholdUnit, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0802010000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('股东单位').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                else:
                                    pass

                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.*?.适用.不适用', '', item)
                            if ret != '':
                                instructi.append(ret)
                    else:
                        pass
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if df is not None and len(df) > 0:

            name_pos = list(np.where(df.iloc[0, :].str.contains('任职人员姓名'))[0])
            name_of_sharehold_pos = list(np.where(df.iloc[0, :].str.contains('股东单位名称'))[0])
            job_titl_in_sharehold_com_pos = list(np.where(df.iloc[0, :].str.contains('在股东单位担任的职务'))[0])
            start_date_in_sharehold_com_pos = list(np.where(df.iloc[0, :].str.contains('任期起始日期'))[0])
            end_date_in_sharehold_com_pos = list(np.where(df.iloc[0, :].str.contains('任期终止日期'))[0])

            df = df.drop([0,len(df)-1])
            names = list(df.iloc[:, name_pos[0]])
            name_of_shareholds = list(df.iloc[:, name_of_sharehold_pos[0]])
            job_titl_in_sharehold_coms = list(df.iloc[:, job_titl_in_sharehold_com_pos[0]])
            start_date_in_sharehold_coms = list(df.iloc[:, start_date_in_sharehold_com_pos[0]])
            end_date_in_sharehold_coms = list(df.iloc[:, end_date_in_sharehold_com_pos[0]])
            values = list(zip(name_of_shareholds,job_titl_in_sharehold_coms,start_date_in_sharehold_coms,end_date_in_sharehold_coms))
            work_in_sharehold_unit_dict = dict(zip(names,values))

            for (name,name_of_sharehold,job_titl_in_sharehold_com, \
                           start_date_in_sharehold_com, end_date_in_sharehold_com) \
                    in zip(names,name_of_shareholds,job_titl_in_sharehold_coms, \
                           start_date_in_sharehold_coms, end_date_in_sharehold_coms):
                if models.ChangInShareholdAndRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                    name=name):
                    obj = models.ChangInShareholdAndRemuner.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                        name=name)
                    obj.name = name
                    obj.name_of_sharehold = work_in_sharehold_unit_dict[name][0]
                    obj.job_titl_in_sharehold_com = work_in_sharehold_unit_dict[name][1]
                    obj.start_date_in_sharehold_com = work_in_sharehold_unit_dict[name][2]
                    obj.end_date_in_sharehold_com = work_in_sharehold_unit_dict[name][3]
                    obj.save()
                else:
                    models.ChangInShareholdAndRemuner.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        name=name,
                        name_of_sharehold=work_in_sharehold_unit_dict[name][0],
                        job_titl_in_sharehold_com=work_in_sharehold_unit_dict[name][1],
                        start_date_in_sharehold_com= work_in_sharehold_unit_dict[name][2],
                        end_date_in_sharehold_com=work_in_sharehold_unit_dict[name][3]

                    )

class WorkInOtherUnit(HandleIndexContent):
    '''
            在其他单位任职情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(WorkInOtherUnit, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0802020000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('其他单位').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                else:
                                    pass

                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.*?.适用.不适用', '', item)
                            if ret != '':
                                instructi.append(ret)
                    else:
                        pass
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if df is not None and len(df) > 0:
            name_pos = list(np.where(df.iloc[0, :].str.contains('任职人员姓名'))[0])
            name_of_sharehold_pos = list(np.where(df.iloc[0, :].str.contains('其他单位名称'))[0])
            job_titl_in_sharehold_com_pos = list(np.where(df.iloc[0, :].str.contains('在其他单位担任的职务'))[0])
            start_date_in_sharehold_com_pos = list(np.where(df.iloc[0, :].str.contains('任期起始日期'))[0])
            end_date_in_sharehold_com_pos = list(np.where(df.iloc[0, :].str.contains('任期终止日期'))[0])

            df = df.drop([0, len(df) - 1])
            names = list(df.iloc[:, name_pos[0]])
            companys = list(df.iloc[:, name_of_sharehold_pos[0]])
            job_titls = list(df.iloc[:, job_titl_in_sharehold_com_pos[0]])
            start_dates = list(df.iloc[:, start_date_in_sharehold_com_pos[0]])
            end_dates = list(df.iloc[:, end_date_in_sharehold_com_pos[0]])


            for (name, company, job_titl,start_date,end_date)  \
                    in zip(names, companys, job_titls,start_dates,end_dates):
                obj_name_id = \
                models.ChangInShareholdAndRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                 name=name)[0].id
                if models.WorkInOtherUnit.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                    name_id=obj_name_id,company=company):
                    obj = models.WorkInOtherUnit.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                             name_id=obj_name_id,company=company)

                    obj.job_titl = job_titl
                    obj.start_date = start_date
                    obj.end_date = end_date
                    obj.save()
                else:
                    models.WorkInOtherUnit.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        name_id=obj_name_id,
                        company=company,
                        job_titl=job_titl,
                        start_date=start_date,
                        end_date=end_date
                    )

class ChangInDirectorsAndSupervisor(HandleIndexContent):
    '''
    四、公司董事、监事、高级管理人员变动情况
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInDirectorsAndSupervisor, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0804000000','08020000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('变动').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                else:
                                    pass

                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.*?.适用.不适用', '', item)
                            if ret != '':
                                instructi.append(ret)
                    else:
                        pass
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if df is not None and len(df) > 0:
            name_pos = list(np.where(df.iloc[0, :].str.contains('姓名'))[0])
            job_titl_chang_reason_pos = list(np.where(df.iloc[0, :].str.contains('原因'))[0])

            df = df.drop([0])
            names = list(df.iloc[:, name_pos[0]])
            job_titl_chang_reasons = list(df.iloc[:, job_titl_chang_reason_pos[0]])

            for (name,job_titl_chang_reason ) \
                    in zip(names, job_titl_chang_reasons):
                if models.ChangInShareholdAndRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                         name=name):
                    obj = models.ChangInShareholdAndRemuner.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                             name=name)

                    obj.job_titl_chang_reason = job_titl_chang_reason
                    obj.save()
                else:
                    models.ChangInShareholdAndRemuner.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        name=name,
                        job_titl_chang_reason=job_titl_chang_reason,
                    )

class EmployeeDesc(HandleIndexContent):
    '''
        员工数量、专业构成及教育程度
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(EmployeeDesc, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0806010000','08050100']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:,0].str.contains('母公司在职员工的数量').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['num'] = df
                                elif table.iloc[:,0].str.contains('专业构成类别').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['prof'] = df
                                elif table.iloc[:,0].str.contains('教育程度类别').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['edu'] = df
                                else:
                                    pass

                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.*?.适用.不适用', '', item)
                            if ret != '':
                                instructi.append(ret)
                    else:
                        pass
        else:
            pass

        return dfs, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs, unit, instructi = self.recognize()
        if dfs.get('num') is not None:
            df = dfs.get('num')
            parent_compani_pos = list(np.where(df.iloc[:, 0].str.contains('母公司在职员工的数量'))[0])
            subsidiari_pos = list(np.where(df.iloc[:, 0].str.contains('主要子公司在职员工的数量'))[0])
            total_pos = list(np.where(df.iloc[:, 0].str.contains('在职员工的数量合计'))[0])
            retir_num_pos = list(np.where(df.iloc[:, 0].str.contains('母公司及主要子公司需承担费用的离退休职工人数'))[0])

            parent_compani = df.iloc[parent_compani_pos[0],1]
            subsidiari = df.iloc[subsidiari_pos[0],1]
            total = df.iloc[total_pos[0],1]
            retir_num = df.iloc[retir_num_pos[0],1]

            if models.NumberOfEmploye.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.NumberOfEmploye.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.parent_compani = parent_compani
                obj.subsidiari = subsidiari
                obj.total = total
                obj.retir_num = retir_num
                obj.save()
            else:
                models.NumberOfEmploye.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    parent_compani=parent_compani,
                    subsidiari=subsidiari,
                    total=total,
                    retir_num=retir_num,
                )
        else:
            pass

        if dfs.get('prof') is not None:
            df = dfs.get('prof')
            df = df.drop([0])
            employe_types = {
                '生产人员':'product',
                '销售人员':'sale',
                '技术人员':'technic',
                '财务人员':'financi',
                '行政人员':'administr',
                '合计':'total',
            }
            types = list(df.iloc[:,0])
            nums = list(df.iloc[:,1])

            for type,num in dict(zip(types,nums)).items():
                if type in employe_types:
                    employe_type = employe_types[type]
                else:
                    employe_type = 'other'

                if models.ProfessionOfEmploye.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,employe_type=employe_type):
                    obj = models.ProfessionOfEmploye.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,employe_type=employe_type)
                    obj.employe_type = employe_type
                    obj.num = num
                    obj.save()
                else:
                    models.ProfessionOfEmploye.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        employe_type=employe_type,
                        num=num,
                    )
        else:
            pass

        if dfs.get('edu') is not None:
            df = dfs.get('edu')
            df = df.drop([0])

            levels = list(df.iloc[:, 0])
            nums = list(df.iloc[:, 1])

            for level, num in dict(zip(levels, nums)).items():
                if models.EduOfEmploye.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,level=level):
                    obj = models.EduOfEmploye.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,level=level)
                    obj.level = level
                    obj.num = num
                    obj.save()
                else:
                    models.EduOfEmploye.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        level=level,
                        num=num,
                    )
        else:
            pass

class RemunerPolicy(HandleIndexContent):
    '''
    薪酬政策
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RemunerPolicy, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0806020000','08050200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(item[0][0])
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.*?.适用.不适用', '', item)
                            if ret != '':
                                instructi.append(ret)
                    else:
                        pass
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if len(instructi) > 0:
            if models.NumberOfEmploye.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.NumberOfEmploye.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.remuner_polici = instructi
                obj.save()
            else:
                models.NumberOfEmploye.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    remuner_polici=instructi
                )
        else:
            pass

class TrainPlan(HandleIndexContent):
    '''
    培训计划
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(TrainPlan, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0806030000','08050300']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(item[0][0])
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.*?.适用.不适用', '', item)
                            if ret != '':
                                instructi.append(ret)
                    else:
                        pass
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if len(instructi) > 0:
            if models.NumberOfEmploye.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.NumberOfEmploye.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.train_program = instructi
                obj.save()
            else:
                models.NumberOfEmploye.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    train_program=instructi
                )
        else:
            pass

class LaborOutsourcing(HandleIndexContent):
    '''
    劳务外包
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(LaborOutsourcing, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0806040000','08050400']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(item[0][0])
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.*?.适用.不适用', '', item)
                            if ret != '':
                                instructi.append(ret)
                    else:
                        pass
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if len(instructi) > 0:
            if models.NumberOfEmploye.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.NumberOfEmploye.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.outsourc = instructi
                obj.save()
            else:
                models.NumberOfEmploye.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    outsourc=instructi
                )
        else:
            pass





