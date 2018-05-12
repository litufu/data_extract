# _author : litufu
# date : 2018/5/10


import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import re
import numpy as np
from utils.mytools import HandleIndexContent,remove_space_from_df,remove_per_from_df,similar,is_num
from report_data_extract import models
from decimal import Decimal
from config.fs import manage_config
import jieba
import decimal
from collections import OrderedDict
from itertools import chain
import pandas as pd

class CompositOfEnterprisGroup(HandleIndexContent):
    '''
                  企业集团的构成
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CompositOfEnterprisGroup, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b09010100','0b09030100']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_per_from_df(remove_space_from_df(table))
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
        natures = {'0b09010100':'s','0b09030100':'j'}
        df, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('名称'))[0])
            main_place_of_busi_pos = list(np.where(df.iloc[0, :].str.contains('主要经营地'))[0])
            registr_place_pos = list(np.where(df.iloc[0, :].str.contains('注册地'))[0])
            busi_natur_pos = list(np.where(df.iloc[0, :].str.contains('业务性质'))[0])
            direct_sharehold_pos = list(np.where(df.iloc[1, :].str.contains('直接'))[0])
            indirect_sharehold_pos = list(np.where(df.iloc[1, :].str.contains('间接'))[0])
            get_method_pos = list(np.where(df.iloc[0, :].str.contains('取得方式'))[0])

            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(
                np.where(df.iloc[:, direct_sharehold_pos[0]].str.match(pattern) | df.iloc[:, direct_sharehold_pos[0]].str.match('nan'))[0])
            names = list(df.iloc[start_pos[0]:, name_pos[0]])
            main_place_of_busis = list(df.iloc[start_pos[0]:, main_place_of_busi_pos[0]])
            registr_places = list(df.iloc[start_pos[0]:, registr_place_pos[0]])
            busi_naturs = list(df.iloc[start_pos[0]:, busi_natur_pos[0]])
            direct_shareholds = list(df.iloc[start_pos[0]:, direct_sharehold_pos[0]])
            indirect_shareholds = list(df.iloc[start_pos[0]:, indirect_sharehold_pos[0]])
            get_methods = list(df.iloc[start_pos[0]:, get_method_pos[0]]) if len(get_method_pos) > 0 else ['' for i in
                                                                                            range(len(names))]

            for (name, main_place_of_busi, registr_place, busi_natur, \
                        direct_sharehold,indirect_sharehold,get_method) in \
                    zip(names, main_place_of_busis, registr_places, busi_naturs, \
                        direct_shareholds,indirect_shareholds,get_methods):
                if models.CompositOfEnterprisGroup.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          typ_rep_id='A',natur_of_the_unit=natures[self.indexno],name=name ):
                    obj = models.CompositOfEnterprisGroup.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              typ_rep_id='A',natur_of_the_unit=natures[self.indexno], name=name)

                    obj.main_place_of_busi = main_place_of_busi
                    obj.registr_place = registr_place
                    obj.busi_natur = busi_natur
                    obj.direct_sharehold = direct_sharehold
                    obj.indirect_sharehold = indirect_sharehold
                    obj.get_method = get_method
                    obj.save()
                else:
                    models.CompositOfEnterprisGroup.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        natur_of_the_unit=natures[self.indexno],
                        name=name,
                        main_place_of_busi=main_place_of_busi,
                        registr_place=registr_place,
                        busi_natur=busi_natur,
                        direct_sharehold=direct_sharehold,
                        indirect_sharehold=indirect_sharehold,
                        get_method=get_method,
                    )
        else:
            pass

        if len(instructi) > 0 and self.indexno=='0b09010100':
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.composit_of_enterpris_group = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    composit_of_enterpris_group=instructi
                )

        if len(instructi) > 0 and self.indexno=='0b09030100':
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.joint_ventur = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    joint_ventur=instructi
                )

class ImportNonwhollyownSubsidia(HandleIndexContent):
    '''
                  重要的非全资子公司
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ImportNonwhollyownSubsidia, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b09010200']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_per_from_df(remove_space_from_df(table))
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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            subcompani_name_pos = list(np.where(df.iloc[0, :].str.contains('子公司名称'))[0])
            minor_sharehold_pos = list(np.where(df.iloc[0, :].str.contains('少数股东持股比例'))[0])
            profit_attrib_to_minor_pos = list(np.where(df.iloc[0, :].str.contains('归属于少数股东的损益'))[0])
            dividend_to_minor_pos = list(np.where(df.iloc[0, :].str.contains('本期向少数股东宣告分派的股利'))[0])
            minor_equiti_pos = list(np.where(df.iloc[1, :].str.contains('期末少数股东权益余额'))[0])

            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(
                np.where(df.iloc[:, minor_sharehold_pos[0]].str.match(pattern) | df.iloc[:, minor_sharehold_pos[0]].str.match('nan'))[0])
            subcompani_names = list(df.iloc[start_pos[0]:, subcompani_name_pos[0]])
            minor_shareholds = list(df.iloc[start_pos[0]:, minor_sharehold_pos[0]])
            profit_attrib_to_minors = list(df.iloc[start_pos[0]:, profit_attrib_to_minor_pos[0]])
            dividend_to_minors = list(df.iloc[start_pos[0]:, dividend_to_minor_pos[0]])
            minor_equitis = list(df.iloc[start_pos[0]:, minor_equiti_pos[0]]) if len(minor_equiti_pos) > 0 else [0.00 for i in
                                                                                            range(len(subcompani_names))]

            for (subcompani_name, minor_sharehold, profit_attrib_to_minor, dividend_to_minor,minor_equiti) in \
                    zip(subcompani_names, minor_shareholds, profit_attrib_to_minors, dividend_to_minors,minor_equitis):
                if models.ImportNonwhollyownSubsidia.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          typ_rep_id='A',subcompani_name=subcompani_name ):
                    obj = models.ImportNonwhollyownSubsidia.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              typ_rep_id='A', subcompani_name=subcompani_name)

                    obj.minor_sharehold = Decimal(re.sub(',', '', str(minor_sharehold))) * unit_change[unit] if is_num(minor_sharehold) else 0.00
                    obj.profit_attrib_to_minor = Decimal(re.sub(',', '', str(profit_attrib_to_minor))) * unit_change[unit] if is_num(profit_attrib_to_minor) else 0.00
                    obj.dividend_to_minor = Decimal(re.sub(',', '', str(dividend_to_minor))) * unit_change[unit] if is_num(dividend_to_minor) else 0.00
                    obj.minor_equiti = Decimal(re.sub(',', '', str(minor_equiti))) * unit_change[unit] if is_num(minor_equiti) else 0.00

                    obj.save()
                else:
                    models.ImportNonwhollyownSubsidia.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        subcompani_name=subcompani_name,
                        minor_sharehold=Decimal(re.sub(',', '', str(minor_sharehold))) * unit_change[unit] if is_num(
                            minor_sharehold) else 0.00,
                        profit_attrib_to_minor=Decimal(re.sub(',', '', str(profit_attrib_to_minor))) * unit_change[
                            unit] if is_num(profit_attrib_to_minor) else 0.00,
                        dividend_to_minor=Decimal(re.sub(',', '', str(dividend_to_minor))) * unit_change[
                            unit] if is_num(dividend_to_minor) else 0.00,
                        minor_equiti=Decimal(re.sub(',', '', str(minor_equiti))) * unit_change[unit] if is_num(
                            minor_equiti) else 0.00,
                    )
        else:
            pass

class MajorNonwhollyownSubsidiaryFinanciInform(HandleIndexContent):
    '''
                      重要的非全资子公司财务信息
                   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MajorNonwhollyownSubsidiaryFinanciInform, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b09010300']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[1,:].str.contains('流动资产').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['asset'] = df
                                elif table.iloc[1,:].str.contains('营业收入').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['income'] = df
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
        before_end_dict = {'期初余额':'b','期末余额':'e','本期发生额':'e','上期发生额':'b'}
        subject_dict = {'流动资产':'la','非流动资产':'na','资产合计':'ta',\
                        '流动负债':'cl','非流动负债':'nl','负债合计':'tl',\
                        '营业收入':'oi','净利润':'np','综合收益总额':'tci','经营活动现金流量':'cfo'}
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if dfs.get('asset') is not None :
            df = dfs['asset']
            df = df.set_index([0])
            df = df.T
            df = df.set_index(['子公司名称'])
            all_dict = df.to_dict()
            for subcompani_name in all_dict:
                for item in all_dict[subcompani_name]:
                    before_end_item,subject_item = item
                    before_end = before_end_dict[before_end_item]
                    subject = subject_dict[subject_item]
                    value = all_dict[subcompani_name][item]
                    value = Decimal(re.sub(',', '', str(value))) * unit_change[unit] if is_num(value) else 0.00
                    if models.MajorNonwhollyownSubsidiaryFinanciInform.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                                typ_rep_id='A', before_end=before_end,company_type='s',
                                                                        subcompani_name=subcompani_name,subject=subject):
                        obj = models.MajorNonwhollyownSubsidiaryFinanciInform.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                            typ_rep_id='A', before_end=before_end,company_type='s',
                                                                        subcompani_name=subcompani_name,subject=subject)

                        obj.amount = value

                        obj.save()
                    else:
                        models.MajorNonwhollyownSubsidiaryFinanciInform.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            typ_rep_id='A',
                            company_type='s',
                            before_end=before_end,
                            subcompani_name=subcompani_name,
                            subject=subject,
                            amount=value
                        )

class JointPoolFinanciInform(HandleIndexContent):
    '''
                      联营企业和合营企业财务信息
                   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(JointPoolFinanciInform, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b09030200','0b09030300']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_per_from_df(remove_space_from_df(table))

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
        company_type_dict = {'0b09030200':'j','0b09030300':'p'}
        df, unit, instructi = self.recognize()
        subject_dict = {'流动资产':'1','非流动资产':'2','资产合计':'3',\
                        '流动负债':'4','非流动负债':'5','负债合计':'6', \
                        '营业收入': '7', '净利润': '8', '综合收益总额': '9', '经营活动现金流量': '10',
                        '现金及现金等价物':'11','少数股东权益':'12','净资产':'13','净资产份额':'14',\
                        '调整事项':'15','商誉':'16','内部交易未实现利润':'17','其他调整':'18',\
                        '权益投资的账面价值':'19','权益投资的公允价值':'20','财务费用':'21','所得税费用':'22',\
                        '终止经营的净利润':'23','其他综合收益':'24','股利':'25'
                        }
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None  and len(df)>1:
            end_poses = list(np.where(df.iloc[0, :].str.contains('期末'))[0])
            before_poses = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            subjects = list(df.iloc[:,0])
            before_end_poses = {'e':end_poses,'b':before_poses}
            for before_end in before_end_poses:
                for pos in before_end_poses[before_end]:
                    subcompani_name = df.iloc[1,pos]
                    for subject_name in subject_dict:
                        subject_pos = ''
                        for k,subject in enumerate(subjects):
                            if subject_name == subject:
                                subject_pos = k
                                break
                            else:
                                if subject_name in subject:
                                    subject_pos = k
                                    break
                                else:
                                    pass
                        if subject_pos != '':
                            subject = subject_dict[subject_name]
                            value = df.iloc[subject_pos,pos]
                            value = Decimal(re.sub(',', '', str(value))) * unit_change[unit] if is_num(value) else 0.00
                            if models.MajorNonwhollyownSubsidiaryFinanciInform.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                                        typ_rep_id='A', before_end='e',company_type='s',
                                                                                subcompani_name=subcompani_name,subject=subject):
                                obj = models.MajorNonwhollyownSubsidiaryFinanciInform.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                                    typ_rep_id='A', before_end=before_end,company_type=company_type_dict[self.indexno],
                                                                                subcompani_name=subcompani_name,subject=subject)
                                obj.amount = value
                                obj.save()
                            else:
                                models.MajorNonwhollyownSubsidiaryFinanciInform.objects.create(
                                    stk_cd_id=self.stk_cd_id,
                                    acc_per=self.acc_per,
                                    typ_rep_id='A',
                                    company_type=company_type_dict[self.indexno],
                                    before_end=before_end,
                                    subcompani_name=subcompani_name,
                                    subject=subject,
                                    amount=value
                                )
                        else:
                            pass

class RiskRelatToFinanciInstrument(HandleIndexContent):
    '''
                      与金融工具相关的风险
                   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RiskRelatToFinanciInstrument, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0a000000']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_per_from_df(remove_space_from_df(table))
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
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.risk_relat_to_financi_instrument = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    risk_relat_to_financi_instrument=instructi
                )

class ParentCompaniAndActualControl(HandleIndexContent):
    '''
                          本企业的母公司情况
                       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ParentCompaniAndActualControl, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0c010000']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_per_from_df(remove_space_from_df(table))
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
        pattern = re.compile('^.*?最终控制方是(.*?)。其他说明：(.*?)$')
        parent_compani_name = ''
        registr = ''
        busi_natur = ''
        regist_capit = 0.00
        parent_company_share = 0.00
        parent_company_vote_right = 0.00
        if df is not None and len(df)>1:
            parent_compani_name_pos = list(np.where(df.iloc[0, :].str.contains('母公司名称'))[0])
            registr_pos = list(np.where(df.iloc[0, :].str.contains('注册地'))[0])
            busi_natur_pos = list(np.where(df.iloc[0, :].str.contains('业务性质'))[0])
            regist_capit_pos = list(np.where(df.iloc[0, :].str.contains('注册资本'))[0])
            parent_company_share_pos = list(np.where(df.iloc[0, :].str.contains('持股比例'))[0])
            parent_company_vote_right_pos = list(np.where(df.iloc[0, :].str.contains('表决权比例'))[0])
            if len(df) == 2:
                parent_compani_name = df.iloc[1, parent_compani_name_pos[0]]
                registr = df.iloc[1, registr_pos[0]]
                busi_natur = df.iloc[1, busi_natur_pos[0]]
                regist_capit = df.iloc[1, regist_capit_pos[0]]
                parent_company_share = df.iloc[1, parent_company_share_pos[0]]
                parent_company_vote_right = df.iloc[1, parent_company_vote_right_pos[0]]

        if len(instructi) > 0 and pattern.match(instructi):
            actual_control = pattern.match(instructi).groups()[0]
            desc = pattern.match(instructi).groups()[1]
        else:
            actual_control = ''
            desc = ''

        if parent_compani_name != '':
            if models.ParentCompaniAndActualControl.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              typ_rep_id='A',
                                                                   parent_compani_name=parent_compani_name):
                obj = models.ParentCompaniAndActualControl.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                  typ_rep_id='A',
                                                                       parent_compani_name=parent_compani_name)

                obj.registr = registr
                obj.busi_natur = busi_natur
                obj.regist_capit = regist_capit
                obj.parent_company_share = parent_company_share
                obj.parent_company_vote_right = parent_company_vote_right
                obj.actual_control = actual_control
                obj.desc = desc
                obj.save()
            else:
                models.ParentCompaniAndActualControl.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    parent_compani_name=parent_compani_name,
                    registr=registr,
                    busi_natur=busi_natur,
                    regist_capit=regist_capit,
                    parent_company_share=parent_company_share,
                    parent_company_vote_right=parent_company_vote_right,
                    actual_control=actual_control,
                    desc=desc,
                )

class OtherRelat(HandleIndexContent):
    '''
                             其他关联方
                          '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OtherRelat, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0c040000']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_per_from_df(remove_space_from_df(table))
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
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('名称'))[0])
            relationship_pos = list(np.where(df.iloc[0, :].str.contains('关系'))[0])

            names = list(df.iloc[1:,name_pos[0]])
            relationships = list(df.iloc[1:,relationship_pos[0]])
            for (name,relationship) in zip(names,relationships):
                if models.OtherRelat.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                       typ_rep_id='A',
                                                                       name=name):
                    obj = models.OtherRelat.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                           typ_rep_id='A',
                                                        name=name)

                    obj.relationship = relationship
                    obj.save()
                else:
                    models.OtherRelat.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        relationship=relationship,
                    )

class PurchasAndSale(HandleIndexContent):
    '''
         采购或销售关联交易
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(PurchasAndSale, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0c050100']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for key,table in enumerate(tables):
                                if table.iloc[0,:].str.contains('获批的交易额度').any() or \
                                    table.iloc[:, 1].str.contains('采购').any() or \
                                    table.iloc[:, 1].str.contains('接受劳务').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['p'] = df
                                elif table.iloc[:, 1].str.contains('销售').any() or \
                                    table.iloc[:, 1].str.contains('提供劳务').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['s'] = df
                                else:
                                    if key == 0:
                                        df = remove_per_from_df(remove_space_from_df(table))
                                        dfs['p'] = df
                                    else:
                                        df = remove_per_from_df(remove_space_from_df(table))
                                        dfs['s'] = df

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
        transact_types = ['s','p']
        dfs, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        for transact_type in transact_types:
            if dfs.get(transact_type) is not None and len(dfs[transact_type])>1:
                df = dfs[transact_type]
                df = df[df.iloc[:, 0] != '合计']
                name_pos = list(np.where(df.iloc[0, :].str.contains('关联方'))[0])
                content_pos = list(np.where(df.iloc[0, :].str.contains('内容'))[0])
                before_pos = list(np.where(df.iloc[0, :].str.contains('上期'))[0])
                end_pos = list(np.where(df.iloc[0, :].str.contains('本期'))[0])
                approv_transact_amou_pos = list(np.where(df.iloc[0, :].str.contains('获批的交易额度'))[0])
                is_exceed_amount_pos = list(np.where(df.iloc[0, :].str.contains('是否超过交易额度'))[0])

                names = list(df.iloc[1:, name_pos[0]])
                contents = list(df.iloc[1:, content_pos[0]])
                befores = list(df.iloc[1:, before_pos[0]])
                ends = list(df.iloc[1:, end_pos[0]])
                approv_transact_amous = list(df.iloc[1:, approv_transact_amou_pos[0]]) if len(approv_transact_amou_pos)>0 else\
                    ['' for i in range(len(names))]
                is_exceed_amounts = list(df.iloc[1:, is_exceed_amount_pos[0]]) if len(
                    is_exceed_amount_pos) > 0 else ['' for i in range(len(names))]

                for (name, content,before,end,approv_transact_amou,is_exceed_amount) in \
                        zip(names, contents,befores,ends,approv_transact_amous,is_exceed_amounts):
                    if models.PurchasAndSale.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                        typ_rep_id='A',transact_type=transact_type,
                                                        name=name):
                        obj = models.PurchasAndSale.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            typ_rep_id='A',transact_type=transact_type,
                                                            name=name)

                        obj.content = content
                        obj.before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00
                        obj.end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00
                        obj.approv_transact_amou = approv_transact_amou
                        obj.is_exceed_amount = is_exceed_amount
                        obj.save()
                    else:
                        models.PurchasAndSale.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            typ_rep_id='A',
                            transact_type=transact_type,
                            name=name,
                            content=content,
                            before=Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00,
                            end=Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00,
                            approv_transact_amou=approv_transact_amou,
                            is_exceed_amount=is_exceed_amount,
                        )

class RelatPartiLeas(HandleIndexContent):
    '''
         关联方租赁
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RelatPartiLeas, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0c050300']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for key,table in enumerate(tables):
                                if table.iloc[0,:].str.contains('收入').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['to'] = df
                                elif table.iloc[:, 1].str.contains('租赁费').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['from'] = df
                                else:
                                    if key == 0:
                                        df = remove_per_from_df(remove_space_from_df(table))
                                        dfs['to'] = df
                                    else:
                                        df = remove_per_from_df(remove_space_from_df(table))
                                        dfs['from'] = df

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
        transact_types = ['to','from']
        dfs, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        for transact_type in transact_types:
            if dfs.get(transact_type) is not None:
                df = dfs[transact_type]
                df = df[df.iloc[:, 0] != '合计']
                name_pos = list(np.where(df.iloc[0, :].str.contains('名称'))[0])
                content_pos = list(np.where(df.iloc[0, :].str.contains('资产种类'))[0])
                before_pos = list(np.where(df.iloc[0, :].str.contains('上期'))[0])
                end_pos = list(np.where(df.iloc[0, :].str.contains('本期'))[0])

                names = list(df.iloc[1:, name_pos[0]])
                contents = list(df.iloc[1:, content_pos[0]])
                befores = list(df.iloc[1:, before_pos[0]])
                ends = list(df.iloc[1:, end_pos[0]])

                for (name, content,before,end) in \
                        zip(names, contents,befores,ends):
                    if models.RelatPartiLeas.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                        typ_rep_id='A',transact_type=transact_type,
                                                        name=name):
                        obj = models.RelatPartiLeas.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            typ_rep_id='A',transact_type=transact_type,
                                                            name=name)

                        obj.content = content
                        obj.before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00
                        obj.end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00

                        obj.save()
                    else:
                        models.RelatPartiLeas.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            typ_rep_id='A',
                            transact_type=transact_type,
                            name=name,
                            content=content,
                            before=Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00,
                            end=Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00,

                        )

class MoneyLend(HandleIndexContent):
    '''
            资金拆借
         '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MoneyLend, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0c050500']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        if len(item) == 3:
                            df_from = remove_per_from_df(remove_space_from_df(item[1][0]))
                            df_to = remove_per_from_df(remove_space_from_df(item[2][0]))
                            dfs['from'] = df_from
                            dfs['to'] = df_to
                        elif len(item) == 2:
                            if item[1][0].iloc[:,0].str.contains('拆出').any():
                                df = remove_per_from_df(remove_space_from_df(item[1][0]))
                                dfs['from'] = df
                            else:
                                df = remove_per_from_df(remove_space_from_df(item[1][0]))
                                dfs['to'] = df
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
        transact_types = ['to', 'from']
        dfs, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        for transact_type in transact_types:
            if dfs.get(transact_type) is not None:
                df = dfs[transact_type]
                df = df[df.iloc[:, 0] != '合计']
                df = df[df.iloc[:,0]!='拆出']
                df = df[df.iloc[:,0]!='拆入']
                names = list(df.iloc[:, 0])
                amounts = list(df.iloc[:, 1])
                start_dates = list(df.iloc[:, 2])
                expiri_dates = list(df.iloc[:, 3])
                descs = list(df.iloc[:, 4])

                for (name, amount, start_date, expiri_date,desc) in \
                        zip(names, amounts, start_dates, expiri_dates,descs):
                    if models.MoneyLend.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            typ_rep_id='A', transact_type=transact_type,
                                                            name=name,amount=amount,start_date=start_date,
                                                       expiri_date=expiri_date):
                        pass
                    else:
                        models.MoneyLend.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            typ_rep_id='A',
                            transact_type=transact_type,
                            name=name,
                            amount=Decimal(re.sub(',', '', str(amount))) * unit_change[unit] if is_num(
                                amount) else 0.00,
                            start_date=start_date,
                            expiri_date=expiri_date,
                            desc=desc,

                        )

class RelatAssetTransferDebtRestructur(HandleIndexContent):
    '''
             关联方资产转让、债务重组情况
          '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RelatAssetTransferDebtRestructur, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0c050600']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for key, table in enumerate(tables):
                                df = remove_per_from_df(remove_space_from_df(table))
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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            df = df[df.iloc[:,0]!='合计']
            name_pos = list(np.where(df.iloc[0, :].str.contains('关联方'))[0])
            content_pos = list(np.where(df.iloc[0, :].str.contains('内容'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('上期'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('本期'))[0])

            names = list(df.iloc[1:, name_pos[0]])
            contents = list(df.iloc[1:, content_pos[0]])
            befores = list(df.iloc[1:, before_pos[0]])
            ends = list(df.iloc[1:, end_pos[0]])

            for (name, content, before, end, ) in \
                    zip(names, contents, befores, ends):
                if models.PurchasAndSale.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                        typ_rep_id='A', transact_type='atdr',
                                                        name=name):
                    obj = models.PurchasAndSale.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            typ_rep_id='A', transact_type='atdr',
                                                            name=name)

                    obj.content = content
                    obj.before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(
                        before) else 0.00
                    obj.end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00
                    obj.save()
                else:
                    models.PurchasAndSale.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        transact_type='atdr',
                        name=name,
                        content=content,
                        before=Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(
                            before) else 0.00,
                        end=Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00,
                    )

class KeyManagStaffRemuner(HandleIndexContent):
    '''
                 关键管理人员薪酬
              '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(KeyManagStaffRemuner, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0c050700']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for key, table in enumerate(tables):
                                df = remove_per_from_df(remove_space_from_df(table))
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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            df = df[df.iloc[:, 0] != '合计']
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('上期'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('本期'))[0])

            names = list(df.iloc[1:, name_pos[0]])
            befores = list(df.iloc[1:, before_pos[0]])
            ends = list(df.iloc[1:, end_pos[0]])

            for (name,  before, end,) in \
                    zip(names,  befores, ends):
                if models.KeyManagStaffRemuner.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                        typ_rep_id='A',
                                                        name=name):
                    obj = models.KeyManagStaffRemuner.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            typ_rep_id='A',
                                                            name=name)

                    obj.before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(
                        before) else 0.00
                    obj.end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00
                    obj.save()
                else:
                    models.KeyManagStaffRemuner.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        before=Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(
                            before) else 0.00,
                        end=Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00,
                    )

class OtherRelatTransact(HandleIndexContent):
    '''
                  其他关联交易
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OtherRelatTransact, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0c050800']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_per_from_df(remove_space_from_df(table))
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
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if len(instructi) > 0 :
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.other_relat_transact = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    other_relat_transact=instructi
                )

class RelatReceivPayabl(HandleIndexContent):
    '''
                 关联方应收应付款
              '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RelatReceivPayabl, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0c060100','0b0c060200']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for key, table in enumerate(tables):
                                df = remove_per_from_df(remove_space_from_df(table))
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
        natur_of_payment_dict = {'0b0c060100':'r','0b0c060200':'p'}
        df, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            df = df[df.iloc[:, 0] != '合计']
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            relat_parti_name_pos = list(np.where(df.iloc[0, :].str.contains('关联方'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])
            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(
                np.where(df.iloc[:, before_pos[0]].str.match(pattern) | df.iloc[:,before_pos[0]].str.match( 'nan'))[0])

            names = list(df.iloc[start_pos[0]:, name_pos[0]])
            relat_parti_names = list(df.iloc[start_pos[0]:, relat_parti_name_pos[0]])
            before_values = list(df.iloc[start_pos[0]:, before_pos[0]])
            before_bad_debt_prepars = list(df.iloc[start_pos[0]:, before_pos[1]]) if len(before_pos)==2 else [0.00 for i in range(len(names))]
            end_values = list(df.iloc[start_pos[0]:, end_pos[0]])
            end_bad_debt_prepars = list(df.iloc[start_pos[0]:, end_pos[1]]) if len(end_pos) == 2 else [0.00 for i in range(len(names))]

            all_dict = {'b':list(zip(before_values,before_bad_debt_prepars)),
                        'e':list(zip(end_values,end_bad_debt_prepars))}

            for before_end in all_dict:
                for name,relat_parti_name,value in zip(names,relat_parti_names,all_dict[before_end]):
                    book_value,bad_debt_prepar = value

                    if models.RelatReceivPayabl.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            typ_rep_id='A',before_end=before_end,
                                                               natur_of_payment=natur_of_payment_dict[self.indexno],name=name,
                                                                 relat_parti_name=relat_parti_name):
                        obj = models.RelatReceivPayabl.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                typ_rep_id='A',before_end=before_end,
                                                                   natur_of_payment=natur_of_payment_dict[self.indexno],  name=name,
                                                                   relat_parti_name=relat_parti_name)

                        obj.book_value = Decimal(re.sub(',', '', str(book_value))) * unit_change[unit] if is_num(
                            book_value) else 0.00
                        obj.bad_debt_prepar = Decimal(re.sub(',', '', str(bad_debt_prepar))) * unit_change[unit] if is_num(bad_debt_prepar) else 0.00
                        obj.save()
                    else:
                        models.RelatReceivPayabl.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            typ_rep_id='A',
                            before_end=before_end,
                            natur_of_payment=natur_of_payment_dict[self.indexno],
                            name=name,
                            relat_parti_name=relat_parti_name,
                            book_value=Decimal(re.sub(',', '', str(book_value))) * unit_change[unit] if is_num(
                            book_value) else 0.00,
                            bad_debt_prepar=Decimal(re.sub(',', '', str(bad_debt_prepar))) * unit_change[unit] if is_num(bad_debt_prepar) else 0.00,
                        )

class RelatPartiCommit(HandleIndexContent):
    '''
                  关联方承诺
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RelatPartiCommit, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0c070000']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_per_from_df(remove_space_from_df(table))
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
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if len(instructi) > 0 :
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.relat_parti_commit = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    relat_parti_commit=instructi
                )

class ImportCommit(HandleIndexContent):
    '''
                  重要承诺事项
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ImportCommit, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0e010000']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_per_from_df(remove_space_from_df(table))
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
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if len(instructi) > 0 :
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.import_commit = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    import_commit=instructi
                )

class Conting(HandleIndexContent):
    '''
                  或有事项
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(Conting, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b0e020100']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_per_from_df(remove_space_from_df(table))
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
        else:
            pass

        return df, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = self.recognize()
        if len(instructi) > 0 :
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.conting = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    conting=instructi
                )

# class