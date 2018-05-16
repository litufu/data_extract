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
        if self.indexno in ['0b09010100','0b09030100','0b090101','0b090301']:
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
        natures = {'0b09010100':'s','0b09030100':'j','0b090101':'s','0b090301':"j"}
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
                if models.CompanyName.objects.filter(natur_of_the_unit=natures[self.indexno], name=name):
                    obj_name = models.CompanyName.objects.get(natur_of_the_unit=natures[self.indexno], name=name)
                else:
                    obj_name = models.CompanyName.objects.create(natur_of_the_unit=natures[self.indexno], name=name)

                if models.CompositOfEnterprisGroup.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          typ_rep_id='A',name_id=obj_name.id):
                    obj = models.CompositOfEnterprisGroup.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              typ_rep_id='A', name_id=obj_name.id)

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
                        name_id=obj_name.id,
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
        if self.indexno in ['0b09010200','0b090102']:
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
        if self.indexno in ['0b09010300','0b090103']:
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
        subject_dict = {'流动资产':'1','非流动资产':'2','资产合计':'3',\
                        '流动负债':'4','非流动负债':'5','负债合计':'6',\
                        '营业收入':'7','净利润':'8','综合收益总额':'9','经营活动现金流量':'10'}
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
        if self.indexno in ['0b09030200','0b09030300','0b090302','0b090303']:
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
        company_type_dict = {'0b09030200':'j','0b09030300':'p','0b090302':'j','0b090303':'p'}
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
                                                                                        typ_rep_id='A', before_end=before_end,company_type=company_type_dict[self.indexno],
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
        if self.indexno in ['0b0a000000','0b0a0000']:
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
        if self.indexno in ['0b0c010000','0b0c0100']:
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
        if self.indexno in ['0b0c040000','0b0c0400']:
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
        if self.indexno in ['0b0c050100','0b0c0501']:
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
        if self.indexno in ['0b0c050300','0b0c0503']:
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
        if self.indexno in ['0b0c050500','0b0c0505']:
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
        if self.indexno in ['0b0c050600','0b0c0506']:
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
        if self.indexno in ['0b0c050700','0b0c0507']:
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
        if self.indexno in ['0b0c050800','0b0c0508']:
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
        if self.indexno in ['0b0c060100','0b0c060200','0b0c0601','0b0c0602']:
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
        natur_of_payment_dict = {'0b0c060100':'r','0b0c060200':'p','0b0c0601':'r','0b0c0602':'p'}
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
        if self.indexno in ['0b0c070000','0b0c0700']:
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
        if self.indexno in ['0b0e010000','0b0e0100']:
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
        if self.indexno in ['0b0e020100','0b0e0201']:
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

class InvestInSubsidiari(HandleIndexContent):
    '''
                      对子公司的投资
                   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(InvestInSubsidiari, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b11030100','0b110301']:
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
            # df = df[df.iloc[:,0]!="合计"]
            name_pos = list(np.where(df.iloc[0, :].str.contains('被投资单位'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初余额'))[0])
            increase_pos = list(np.where(df.iloc[0, :].str.contains('本期增加'))[0])
            cut_back_pos = list(np.where(df.iloc[0, :].str.contains('本期减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末余额'))[0])
            impair_pos = list(np.where(df.iloc[0, :].str.contains('本期计提减值准备'))[0])
            impair_balanc_pos = list(np.where(df.iloc[0, :].str.contains('减值准备期末余额'))[0])

            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(
                np.where(df.iloc[:, end_pos[0]].str.match(pattern) | df.iloc[:,end_pos[0]].str.match( 'nan'))[0])

            names = list(df.iloc[start_pos[0]:, name_pos[0]])
            befores = list(df.iloc[start_pos[0]:, before_pos[0]])
            increases = list(df.iloc[start_pos[0]:, increase_pos[0]])
            cut_backs = list(df.iloc[start_pos[0]:, cut_back_pos[0]])
            ends = list(df.iloc[start_pos[0]:, end_pos[0]])
            impairs = list(df.iloc[start_pos[0]:, impair_pos[0]])
            impair_balancs = list(df.iloc[start_pos[0]:, impair_balanc_pos[0]])
            for (name, before, increase, cut_back, end,impair,impair_balanc) in \
                    zip(names, befores, increases, cut_backs, ends,impairs,impair_balancs):

                if models.CompanyName.objects.filter(natur_of_the_unit='s', name=name):
                    obj_name = models.CompanyName.objects.get(natur_of_the_unit='s', name=name)
                else:
                    obj_name = models.CompanyName.objects.create(natur_of_the_unit='s', name=name)

                if models.InvestInSubsidiari.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                    typ_rep_id='A', name_id=obj_name.id):
                    obj = models.InvestInSubsidiari.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                        typ_rep_id='A', name_id=obj_name.id)

                    obj.before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(
                        before) else 0.00
                    obj.increase = Decimal(re.sub(',', '', str(increase))) * unit_change[
                        unit] if is_num(increase) else 0.00
                    obj.cut_back = Decimal(re.sub(',', '', str(cut_back))) * unit_change[
                        unit] if is_num(cut_back) else 0.00
                    obj.end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(
                        end) else 0.00
                    obj.impair = Decimal(re.sub(',', '', str(impair))) * unit_change[unit] if is_num(
                        impair) else 0.00
                    obj.impair_balanc = Decimal(re.sub(',', '', str(impair_balanc))) * unit_change[unit] if is_num(
                        impair_balanc) else 0.00
                    obj.save()
                else:
                    models.InvestInSubsidiari.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        before=Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(
                            before) else 0.00,
                        increase=Decimal(re.sub(',', '', str(increase))) * unit_change[
                            unit] if is_num(increase) else 0.00,
                        cut_back=Decimal(re.sub(',', '', str(cut_back))) * unit_change[
                            unit] if is_num(cut_back) else 0.00,
                        end=Decimal(re.sub(',', '', str(end))) * unit_change[
                            unit] if is_num(end) else 0.00,
                        impair=Decimal(re.sub(',', '', str(impair))) * unit_change[
                            unit] if is_num(impair) else 0.00,
                        impair_balanc=Decimal(re.sub(',', '', str(impair_balanc))) * unit_change[
                            unit] if is_num(impair_balanc) else 0.00,
                    )
        else:
            pass


class ReturnOnEquitiAndEarnPerShare(HandleIndexContent):
    '''
                          净资产收益率及每股收益
                       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ReturnOnEquitiAndEarnPerShare, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b12020000','0b120200']:
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
            return_on_equiti_pos = list(np.where(df.iloc[1, :].str.contains('加权平均净资产收益率'))[0])
            basic_earn_per_share_pos = list(np.where(df.iloc[1, :].str.contains('基本每股收益'))[0])
            dilut_earn_per_share_pos = list(np.where(df.iloc[1, :].str.contains('稀释每股收益'))[0])
            before_pos = list(np.where(df.iloc[:, 0] == '归属于公司普通股股东的净利润')[0])
            after_pos = list(np.where(df.iloc[:, 0].str.contains('扣除非经常性损益后'))[0])

            poses = {'b':before_pos,'a':after_pos}
            for gain_or_loss_type in poses:
                return_on_equiti = df.iloc[poses[gain_or_loss_type][0],return_on_equiti_pos[0]]
                basic_earn_per_share = df.iloc[poses[gain_or_loss_type][0],basic_earn_per_share_pos[0]]
                dilut_earn_per_share = df.iloc[poses[gain_or_loss_type][0],dilut_earn_per_share_pos[0]]
                if models.ReturnOnEquitiAndEarnPerShare.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            typ_rep_id='A', gain_or_loss_type=gain_or_loss_type):
                    obj = models.ReturnOnEquitiAndEarnPerShare.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                typ_rep_id='A', gain_or_loss_type=gain_or_loss_type)

                    obj.return_on_equiti = Decimal(re.sub(',', '', str(return_on_equiti)))  if is_num(
                        return_on_equiti) else 0.00
                    obj.basic_earn_per_share = Decimal(re.sub(',', '', str(basic_earn_per_share)))  if is_num(basic_earn_per_share) else 0.00
                    obj.dilut_earn_per_share = Decimal(re.sub(',', '', str(dilut_earn_per_share))) if is_num(dilut_earn_per_share) else 0.00
                    obj.save()
                else:
                    models.ReturnOnEquitiAndEarnPerShare.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        gain_or_loss_type=gain_or_loss_type,
                        return_on_equiti=Decimal(re.sub(',', '', str(return_on_equiti)))  if is_num(
                            return_on_equiti) else 0.00,
                        basic_earn_per_share=Decimal(re.sub(',', '', str(basic_earn_per_share))) if is_num(basic_earn_per_share) else 0.00,
                        dilut_earn_per_share=Decimal(re.sub(',', '', str(dilut_earn_per_share))) if is_num(dilut_earn_per_share) else 0.00,
                    )
        else:
            pass

class BusiMergerNotUnderTheSameControl(HandleIndexContent):
    '''
                  本期发生的非同一控制下企业合并
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BusiMergerNotUnderTheSameControl, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b080101']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0,:].str.contains('被购买方名称').any():
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
            name_pos = list(np.where(df.iloc[0, :].str.contains('被购买方名称'))[0])
            acquisit_time_pos = list(np.where(df.iloc[0, :].str.contains('股权取得时点'))[0])
            acquisit_cost_pos = list(np.where(df.iloc[0, :].str.contains('股权取得成本'))[0])
            acquisit_rate_pos = list(np.where(df.iloc[0, :].str.contains('股权取得比例'))[0])
            acquisit_style_pos = list(np.where(df.iloc[0, :].str.contains('取得方式'))[0])
            purchas_day_pos = list(np.where(df.iloc[0, :].str.contains('购买日'))[0])
            purchas_day_determi_basi_pos = list(np.where(df.iloc[0, :].str.contains('购买日的确定依据'))[0])
            income_pos = list(np.where(df.iloc[0, :].str.contains('购买日至期末被购买方的收入'))[0])
            np_pos = list(np.where(df.iloc[0, :].str.contains('购买日至期末被购买方的净利润'))[0])

            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(
                np.where(df.iloc[:, income_pos[0]].str.match(pattern) | df.iloc[:, income_pos[0]].str.match('nan'))[0])
            names = list(df.iloc[start_pos[0]:, name_pos[0]])
            acquisit_times = list(df.iloc[start_pos[0]:, acquisit_time_pos[0]])
            acquisit_costs = list(df.iloc[start_pos[0]:, acquisit_cost_pos[0]])
            acquisit_rates = list(df.iloc[start_pos[0]:, acquisit_rate_pos[0]])
            acquisit_styles = list(df.iloc[start_pos[0]:, acquisit_style_pos[0]])
            purchas_days = list(df.iloc[start_pos[0]:, purchas_day_pos[0]])
            purchas_day_determi_basis = list(df.iloc[start_pos[0]:, purchas_day_determi_basi_pos[0]])
            incomes = list(df.iloc[start_pos[0]:, income_pos[0]])
            nps = list(df.iloc[start_pos[0]:, np_pos[0]]) if len(np_pos) > 0 else [0.00 for i in range(len(names))]

            for (name, acquisit_time, acquisit_cost, acquisit_rate,acquisit_style,purchas_day,
                        purchas_day_determi_basi,income,np) in\
                    zip(names, acquisit_times, acquisit_costs, acquisit_rates,acquisit_styles,purchas_days,
                        purchas_day_determi_basis,incomes,nps):
                if models.CompanyName.objects.filter(name=name):
                    obj_name = models.CompanyName.objects.get( name=name)
                else:
                    obj_name = models.CompanyName.objects.create(name=name)

                if models.BusiMergerNotUnderTheSameControl.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          typ_rep_id='A', name_id=obj_name.id):
                    obj = models.BusiMergerNotUnderTheSameControl.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              typ_rep_id='A', name_id=obj_name.id)

                    obj.acquisit_time = acquisit_time
                    obj.acquisit_cost = Decimal(re.sub(',', '', str(acquisit_cost))) * unit_change[unit] if is_num(acquisit_cost) else 0.00
                    obj.acquisit_rate = Decimal(re.sub(',', '', str(acquisit_rate)))  if is_num(acquisit_rate) else 0.00
                    obj.acquisit_style = acquisit_style
                    obj.purchas_day = purchas_day
                    obj.purchas_day_determi_basi = purchas_day_determi_basi
                    obj.income = Decimal(re.sub(',', '', str(income))) * unit_change[unit] if is_num(income) else 0.00
                    obj.np = Decimal(re.sub(',', '', str(np))) * unit_change[unit] if is_num(np) else 0.00

                    obj.save()
                else:
                    models.BusiMergerNotUnderTheSameControl.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        acquisit_time=acquisit_time,
                        acquisit_cost=Decimal(re.sub(',', '', str(acquisit_cost))) * unit_change[unit] if is_num(acquisit_cost) else 0.00,
                        acquisit_rate=Decimal(re.sub(',', '', str(acquisit_rate)))  if is_num(acquisit_rate) else 0.00,
                        acquisit_style=acquisit_style,
                        purchas_day=purchas_day,
                        purchas_day_determi_basi=purchas_day_determi_basi,
                        income=Decimal(re.sub(',', '', str(income))) * unit_change[unit] if is_num(income) else 0.00,
                        np = Decimal(re.sub(',', '', str(np))) * unit_change[unit] if is_num(np) else 0.00
                    )
        else:
            pass



class ConsolidCostAndGoodwil(HandleIndexContent):
    '''
      合并成本及商誉
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ConsolidCostAndGoodwil, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b080102']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:,0].str.contains('合并成本').any():
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
            df = df.T
            cash_pos = list(np.where(df.iloc[0, :].str.contains('现金'))[0])
            non_cash_asset_pos = list(np.where(df.iloc[0, :].str.contains('非现金资产'))[0])
            issu_or_assum_debt_pos = list(np.where(df.iloc[0, :].str.contains('发行或承担的债务'))[0])
            issuanc_of_equiti_secur_pos = list(np.where(df.iloc[0, :].str.contains('权益性证券'))[0])
            or_have_consider_pos = list(np.where(df.iloc[0, :].str.contains('或有对价'))[0])
            share_held_prior_to_the_acquis_pos = list(np.where(df.iloc[0, :].str.contains('购买日之前持有的股权'))[0])
            other_pos = list(np.where(df.iloc[0, :].str.contains('其他'))[0])
            total_combin_cost_pos = list(np.where(df.iloc[0, :].str.contains('合并成本合计'))[0])
            recogniz_net_asset_fair_valu_pos = list(np.where(df.iloc[0, :].str.contains('可辨认净资产公允价值'))[0])
            goodwil_pos = list(np.where(df.iloc[0, :].str.contains('商誉'))[0])


            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(
                np.where(df.iloc[:, cash_pos[0]].str.match(pattern) | df.iloc[:, cash_pos[0]].str.match('nan'))[0])
            names = list(df.iloc[start_pos[0]:,0])
            cashs = list(df.iloc[start_pos[0]:, cash_pos[0]])  if len(cash_pos) > 0 else [0.00 for i in range(len(names))]
            non_cash_assets = list(df.iloc[start_pos[0]:, non_cash_asset_pos[0]])  if len(non_cash_asset_pos) > 0 else [0.00 for i in range(len(names))]
            issu_or_assum_debts = list(df.iloc[start_pos[0]:, issu_or_assum_debt_pos[0]]) if len(issu_or_assum_debt_pos) > 0 else [0.00 for i in range(len(names))]
            issuanc_of_equiti_securs = list(df.iloc[start_pos[0]:, issuanc_of_equiti_secur_pos[0]]) if len(issuanc_of_equiti_secur_pos) > 0 else [0.00 for i in range(len(names))]
            or_have_considers = list(df.iloc[start_pos[0]:, or_have_consider_pos[0]]) if len(or_have_consider_pos) > 0 else [0.00 for i in range(len(names))]
            share_held_prior_to_the_acquiss = list(df.iloc[start_pos[0]:, share_held_prior_to_the_acquis_pos[0]]) if len(share_held_prior_to_the_acquis_pos) > 0 else [0.00 for i in range(len(names))]
            others = list(df.iloc[start_pos[0]:, other_pos[0]]) if len(other_pos) > 0 else [0.00 for i in range(len(names))]
            total_combin_costs = list(df.iloc[start_pos[0]:, total_combin_cost_pos[0]]) if len(total_combin_cost_pos) > 0 else [0.00 for i in range(len(names))]
            recogniz_net_asset_fair_valus = list(df.iloc[start_pos[0]:, recogniz_net_asset_fair_valu_pos[0]]) if len(recogniz_net_asset_fair_valu_pos) > 0 else [0.00 for i in range(len(names))]
            goodwils = list(df.iloc[start_pos[0]:, goodwil_pos[0]]) if len(goodwil_pos) > 0 else [0.00 for i in range(len(names))]

            for (name,cash, non_cash_asset, issu_or_assum_debt, issuanc_of_equiti_secur, or_have_consider, share_held_prior_to_the_acquis,
                        other, total_combin_cost, recogniz_net_asset_fair_valu,goodwil) in \
                    zip(names,cashs, non_cash_assets, issu_or_assum_debts, issuanc_of_equiti_securs, or_have_considers, share_held_prior_to_the_acquiss,
                        others, total_combin_costs, recogniz_net_asset_fair_valus,goodwils):
                if models.CompanyName.objects.filter(name=name):
                    obj_name = models.CompanyName.objects.get(name=name)
                else:
                    obj_name = models.CompanyName.objects.create(name=name)

                if models.ConsolidCostAndGoodwil.objects.filter(stk_cd_id=self.stk_cd_id,
                                                                          acc_per=self.acc_per,
                                                                          typ_rep_id='A', name_id=obj_name.id):
                    obj = models.ConsolidCostAndGoodwil.objects.get(stk_cd_id=self.stk_cd_id,
                                                                              acc_per=self.acc_per,
                                                                              typ_rep_id='A', name_id=obj_name.id)
                    obj.cash = Decimal(re.sub(',', '', str(cash))) * unit_change[unit] if is_num(
                        cash) else 0.00
                    obj.non_cash_asset = Decimal(re.sub(',', '', str(non_cash_asset))) * unit_change[unit] if is_num(
                        non_cash_asset) else 0.00
                    obj.issu_or_assum_debt = Decimal(re.sub(',', '', str(issu_or_assum_debt))) if is_num(issu_or_assum_debt) else 0.00
                    obj.issuanc_of_equiti_secur = Decimal(re.sub(',', '', str(issuanc_of_equiti_secur))) if is_num(issuanc_of_equiti_secur) else 0.00
                    obj.or_have_consider = Decimal(re.sub(',', '', str(or_have_consider))) if is_num(or_have_consider) else 0.00
                    obj.share_held_prior_to_the_acquis = Decimal(re.sub(',', '', str(share_held_prior_to_the_acquis))) if is_num(share_held_prior_to_the_acquis) else 0.00
                    obj.other = Decimal(re.sub(',', '', str(other))) if is_num(other) else 0.00
                    obj.total_combin_cost = Decimal(re.sub(',', '', str(total_combin_cost))) if is_num(total_combin_cost) else 0.00
                    obj.recogniz_net_asset_fair_valu = Decimal(re.sub(',', '', str(recogniz_net_asset_fair_valu))) if is_num(recogniz_net_asset_fair_valu) else 0.00
                    obj.goodwil = Decimal(re.sub(',', '', str(goodwil))) if is_num(goodwil) else 0.00
                    obj.save()
                else:
                    models.ConsolidCostAndGoodwil.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        cash=Decimal(re.sub(',', '', str(cash))) * unit_change[unit] if is_num(
                            cash) else 0.00,
                        non_cash_asset=Decimal(re.sub(',', '', str(non_cash_asset))) * unit_change[unit] if is_num(
                            non_cash_asset) else 0.00,
                        issu_or_assum_debt=Decimal(re.sub(',', '', str(issu_or_assum_debt))) if is_num(
                            issu_or_assum_debt) else 0.00,
                        issuanc_of_equiti_secur=Decimal(re.sub(',', '', str(issuanc_of_equiti_secur))) if is_num(
                            issuanc_of_equiti_secur) else 0.00,
                        or_have_consider=Decimal(re.sub(',', '', str(or_have_consider))) if is_num(
                            or_have_consider) else 0.00,
                        share_held_prior_to_the_acquis=Decimal(
                            re.sub(',', '', str(share_held_prior_to_the_acquis))) if is_num(share_held_prior_to_the_acquis) else 0.00,
                        other=Decimal(re.sub(',', '', str(other))) if is_num(other) else 0.00,
                        total_combin_cost=Decimal(re.sub(',', '', str(total_combin_cost))) if is_num(
                            total_combin_cost) else 0.00,
                        recogniz_net_asset_fair_valu=Decimal(
                            re.sub(',', '', str(recogniz_net_asset_fair_valu))) if is_num(
                            recogniz_net_asset_fair_valu) else 0.00,
                        goodwil=Decimal(re.sub(',', '', str(goodwil))) if is_num(goodwil) else 0.00,
                    )
        else:
            pass

        if len(instructi) > 1:
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.consolid_cost_and_goodwil = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    consolid_cost_and_goodwil=instructi
                )

class AcquireRecognisAssetAndLiab(HandleIndexContent):
    '''
          被购买方于购买日可辨认资产、负债
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AcquireRecognisAssetAndLiab, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b080103']:
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
        value_type_dict={'购买日公允价值':'f','购买日账面价值':'b'}
        df, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            df = df.set_index([0])
            df = df.dropna(how='all')
            df = df.reset_index()

            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(np.where(df.iloc[:,1].str.match(pattern) | df.iloc[:, 1].str.match('nan'))[0])
            subjects = list(df.iloc[start_pos[0]:,:])
            company_names = list(df.iloc[0,1:])
            value_types = list(df.iloc[1,1:])

            for key,company_name in enumerate(company_names):
                if models.CompanyName.objects.filter(name=company_name):
                    obj_name = models.CompanyName.objects.get(name=company_name)
                else:
                    obj_name = models.CompanyName.objects.create(name=company_name)

                value_type_name = value_types[key]
                if value_type_dict.get(value_type_name) is not None:
                    value_type = value_type_dict[value_type_name]
                    for i,subject in enumerate(subjects):

                        if models.SubjectName.objects.filter(name=subject):
                            subject_name = models.SubjectName.objects.get(name=subject)
                        else:
                            subject_name = models.SubjectName.objects.create(name=subject)


                        amount = df.iloc[(start_pos[0]+i),(key+1)]
                        amount = Decimal(re.sub(',', '', str(amount))) * unit_change[unit] if is_num(amount) else 0.00
                        if models.AcquireRecognisAssetAndLiab.objects.filter(stk_cd_id=self.stk_cd_id,
                                                                        acc_per=self.acc_per,value_type=value_type,subject_id=subject_name.id,
                                                                        typ_rep_id='A', company_name_id=obj_name.id):
                            obj = models.AcquireRecognisAssetAndLiab.objects.get(stk_cd_id=self.stk_cd_id,subject_id=subject_name.id,
                                                                            acc_per=self.acc_per,value_type=value_type,
                                                                            typ_rep_id='A', company_name_id=obj_name.id)
                            obj.amount = amount
                            obj.save()
                        else:
                            models.AcquireRecognisAssetAndLiab.objects.create(
                                stk_cd_id=self.stk_cd_id,
                                acc_per=self.acc_per,
                                typ_rep_id='A',
                                company_name_id=obj_name.id,
                                value_type=value_type,
                                subject_id=subject_name.id,
                                amount=amount
                            )
        else:
            pass

class BusiMergerUnderTheSameControl(HandleIndexContent):
    '''
                      本期发生的同一控制下企业合并
                   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BusiMergerUnderTheSameControl, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b080201']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('被合并方名称').any():
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
            name_pos = list(np.where(df.iloc[0, :].str.contains('被合并方名称'))[0])
            acquisit_rate_pos = list(np.where(df.iloc[0, :].str.contains('企业合并中取得的权益比例'))[0])
            same_control_basi_pos = list(np.where(df.iloc[0, :].str.contains('构成同一控制下企业合并的依据'))[0])
            merger_date_pos = list(np.where(df.iloc[0, :].str.contains('合并日'))[0])
            merger_date_determi_basi_pos = list(np.where(df.iloc[0, :].str.contains('合并日的确定依据'))[0])
            this_income_pos = list(np.where(df.iloc[0, :].str.contains('初至合并日被合并方的收入'))[0])
            this_np_pos = list(np.where(df.iloc[0, :].str.contains('初至合并日被合并方的净利润'))[0])
            before_income_pos = list(np.where(df.iloc[0, :].str.contains('比较期间被合并方的收入'))[0])
            before_np_pos = list(np.where(df.iloc[0, :].str.contains('比较期间被合并方的净利润'))[0])

            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(
                np.where(df.iloc[:, this_income_pos[0]].str.match(pattern) | df.iloc[:, this_income_pos[0]].str.match('nan'))[0])
            names = list(df.iloc[start_pos[0]:, name_pos[0]])
            acquisit_rates = list(df.iloc[start_pos[0]:, acquisit_rate_pos[0]])
            same_control_basis = list(df.iloc[start_pos[0]:, same_control_basi_pos[0]])
            merger_dates = list(df.iloc[start_pos[0]:, merger_date_pos[0]])
            merger_date_determi_basis = list(df.iloc[start_pos[0]:, merger_date_determi_basi_pos[0]])
            this_incomes = list(df.iloc[start_pos[0]:, this_income_pos[0]])
            this_nps = list(df.iloc[start_pos[0]:, this_np_pos[0]])
            before_incomes = list(df.iloc[start_pos[0]:, before_income_pos[0]])
            before_nps = list(df.iloc[start_pos[0]:, before_np_pos[0]]) if len(before_np_pos) > 0 else [0.00 for i in range(len(names))]

            for (name, acquisit_rate,same_control_basi,merger_date,merger_date_determi_basi,
                        this_income,this_np,before_income,before_np) in \
                    zip(names, acquisit_rates,same_control_basis,merger_dates,merger_date_determi_basis,
                        this_incomes,this_nps,before_incomes,before_nps):
                if models.CompanyName.objects.filter(name=name):
                    obj_name = models.CompanyName.objects.get(name=name)
                else:
                    obj_name = models.CompanyName.objects.create(name=name)

                if models.BusiMergerUnderTheSameControl.objects.filter(stk_cd_id=self.stk_cd_id,
                                                                          acc_per=self.acc_per,
                                                                          typ_rep_id='A', name_id=obj_name.id):
                    obj = models.BusiMergerUnderTheSameControl.objects.get(stk_cd_id=self.stk_cd_id,
                                                                              acc_per=self.acc_per,
                                                                              typ_rep_id='A', name_id=obj_name.id)

                    obj.acquisit_rate = Decimal(re.sub(',', '', str(acquisit_rate)))if is_num(
                        acquisit_rate) else 0.00
                    obj.same_control_basi = same_control_basi
                    obj.merger_date = merger_date
                    obj.merger_date_determi_basi = merger_date_determi_basi
                    obj.this_income = Decimal(re.sub(',', '', str(this_income))) * unit_change[unit] if is_num(this_income) else 0.00
                    obj.this_np = Decimal(re.sub(',', '', str(this_np))) * unit_change[unit] if is_num(this_np) else 0.00
                    obj.before_income = Decimal(re.sub(',', '', str(before_income))) * unit_change[unit] if is_num(before_income) else 0.00
                    obj.before_np = Decimal(re.sub(',', '', str(before_np))) * unit_change[unit] if is_num(before_np) else 0.00
                    obj.save()
                else:
                    models.BusiMergerUnderTheSameControl.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        acquisit_rate=Decimal(re.sub(',', '', str(acquisit_rate))) if is_num(
                            acquisit_rate) else 0.00,
                        same_control_basi=same_control_basi,
                        merger_date=merger_date,
                        merger_date_determi_basi=merger_date_determi_basi,
                        this_income=Decimal(re.sub(',', '', str(this_income))) * unit_change[unit] if is_num(
                            this_income) else 0.00,
                        this_np=Decimal(re.sub(',', '', str(this_np))) * unit_change[unit] if is_num(this_np) else 0.00,
                        before_income=Decimal(re.sub(',', '', str(before_income))) * unit_change[unit] if is_num(
                            before_income) else 0.00,
                        before_np = Decimal(re.sub(',', '', str(before_np))) * unit_change[unit] if is_num(
                            before_np) else 0.00
                    )
        else:
            pass

class ConsolidCost(HandleIndexContent):
    '''
          合并成本
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ConsolidCost, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b080202']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:, 0].str.contains('合并成本').any():
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
            df = df.T
            cash_pos = list(np.where(df.iloc[0, :].str.contains('现金'))[0])
            non_cash_asset_pos = list(np.where(df.iloc[0, :].str.contains('非现金资产'))[0])
            issu_or_assum_debt_pos = list(np.where(df.iloc[0, :].str.contains('发行或承担的债务'))[0])
            issuanc_of_equiti_secur_pos = list(np.where(df.iloc[0, :].str.contains('权益性证券'))[0])
            or_have_consider_pos = list(np.where(df.iloc[0, :].str.contains('或有对价'))[0])


            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(
                np.where(df.iloc[:, cash_pos[0]].str.match(pattern) | df.iloc[:, cash_pos[0]].str.match('nan'))[0])
            names = list(df.iloc[start_pos[0]:, 0])
            cashs = list(df.iloc[start_pos[0]:, cash_pos[0]]) if len(cash_pos) > 0 else [0.00 for i in
                                                                                         range(len(names))]
            non_cash_assets = list(df.iloc[start_pos[0]:, non_cash_asset_pos[0]]) if len(non_cash_asset_pos) > 0 else [
                0.00 for i in range(len(names))]
            issu_or_assum_debts = list(df.iloc[start_pos[0]:, issu_or_assum_debt_pos[0]]) if len(
                issu_or_assum_debt_pos) > 0 else [0.00 for i in range(len(names))]
            issuanc_of_equiti_securs = list(df.iloc[start_pos[0]:, issuanc_of_equiti_secur_pos[0]]) if len(
                issuanc_of_equiti_secur_pos) > 0 else [0.00 for i in range(len(names))]
            or_have_considers = list(df.iloc[start_pos[0]:, or_have_consider_pos[0]]) if len(
                or_have_consider_pos) > 0 else [0.00 for i in range(len(names))]

            for (name, cash, non_cash_asset, issu_or_assum_debt, issuanc_of_equiti_secur, or_have_consider,
                 ) in \
                    zip(names, cashs, non_cash_assets, issu_or_assum_debts, issuanc_of_equiti_securs, or_have_considers,
                        ):
                if models.CompanyName.objects.filter(name=name):
                    obj_name = models.CompanyName.objects.get(name=name)
                else:
                    obj_name = models.CompanyName.objects.create(name=name)

                if models.ConsolidCost.objects.filter(stk_cd_id=self.stk_cd_id,
                                                                acc_per=self.acc_per,
                                                                typ_rep_id='A', name_id=obj_name.id):
                    obj = models.ConsolidCost.objects.get(stk_cd_id=self.stk_cd_id,
                                                                    acc_per=self.acc_per,
                                                                    typ_rep_id='A', name_id=obj_name.id)
                    obj.cash = Decimal(re.sub(',', '', str(cash))) * unit_change[unit] if is_num(
                        cash) else 0.00
                    obj.non_cash_asset = Decimal(re.sub(',', '', str(non_cash_asset))) * unit_change[unit] if is_num(
                        non_cash_asset) else 0.00
                    obj.issu_or_assum_debt = Decimal(re.sub(',', '', str(issu_or_assum_debt))) if is_num(
                        issu_or_assum_debt) else 0.00
                    obj.issuanc_of_equiti_secur = Decimal(re.sub(',', '', str(issuanc_of_equiti_secur))) if is_num(
                        issuanc_of_equiti_secur) else 0.00
                    obj.or_have_consider = Decimal(re.sub(',', '', str(or_have_consider))) if is_num(
                        or_have_consider) else 0.00

                    obj.save()
                else:
                    models.ConsolidCost.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        cash=Decimal(re.sub(',', '', str(cash))) * unit_change[unit] if is_num(
                            cash) else 0.00,
                        non_cash_asset=Decimal(re.sub(',', '', str(non_cash_asset))) * unit_change[unit] if is_num(
                            non_cash_asset) else 0.00,
                        issu_or_assum_debt=Decimal(re.sub(',', '', str(issu_or_assum_debt))) if is_num(
                            issu_or_assum_debt) else 0.00,
                        issuanc_of_equiti_secur=Decimal(re.sub(',', '', str(issuanc_of_equiti_secur))) if is_num(
                            issuanc_of_equiti_secur) else 0.00,
                        or_have_consider=Decimal(re.sub(',', '', str(or_have_consider))) if is_num(
                            or_have_consider) else 0.00,
                    )
        else:
            pass

        if len(instructi) > 1:
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.consolid_cost = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    consolid_cost=instructi
                )

class BookValuOfAssetAndLiabil(HandleIndexContent):
    '''
              合并日被合并方资产、负债的账面价值
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BookValuOfAssetAndLiabil, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b080203']:
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
        deadlin_dict = {'合并日': 'm', '上年年末': 'b'}
        df, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            df = df.set_index([0])
            df = df.dropna(how='all')
            df = df.reset_index()

            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(np.where(df.iloc[:, 1].str.match(pattern) | df.iloc[:, 1].str.match('nan'))[0])
            subjects = list(df.iloc[start_pos[0]:, :])
            company_names = list(df.iloc[0, 1:])
            deadlins = list(df.iloc[1, 1:])

            for key, company_name in enumerate(company_names):
                if models.CompanyName.objects.filter(name=company_name):
                    obj_name = models.CompanyName.objects.get(name=company_name)
                else:
                    obj_name = models.CompanyName.objects.create(name=company_name)

                deadlin_name = deadlins[key]
                if deadlin_dict.get(deadlin_name) is not None:
                    deadlin = deadlin_dict[deadlin_name]
                    for i, subject in enumerate(subjects):

                        if models.SubjectName.objects.filter(name=subject):
                            subject_name = models.SubjectName.objects.get(name=subject)
                        else:
                            subject_name = models.SubjectName.objects.create(name=subject)

                        amount = df.iloc[(start_pos[0] + i), (key + 1)]
                        amount = Decimal(re.sub(',', '', str(amount))) * unit_change[unit] if is_num(amount) else 0.00
                        if models.AcquireRecognisAssetAndLiab.objects.filter(stk_cd_id=self.stk_cd_id,
                                                                             acc_per=self.acc_per,
                                                                             deadlin=deadlin,
                                                                             subject_id=subject_name.id,
                                                                             typ_rep_id='A',
                                                                             company_name_id=obj_name.id):
                            obj = models.AcquireRecognisAssetAndLiab.objects.get(stk_cd_id=self.stk_cd_id,
                                                                                 subject_id=subject_name.id,
                                                                                 acc_per=self.acc_per,
                                                                                 deadlin=deadlin,
                                                                                 typ_rep_id='A',
                                                                                 company_name_id=obj_name.id)
                            obj.amount = amount
                            obj.save()
                        else:
                            models.AcquireRecognisAssetAndLiab.objects.create(
                                stk_cd_id=self.stk_cd_id,
                                acc_per=self.acc_per,
                                typ_rep_id='A',
                                company_name_id=obj_name.id,
                                deadlin=deadlin,
                                subject_id=subject_name.id,
                                amount=amount
                            )
        else:
            pass

class ReversPurchas(HandleIndexContent):
    '''
          反向购买
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ReversPurchas, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b080300']:
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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}

        if len(instructi) > 1:
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.revers_purchas = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    revers_purchas=instructi
                )

class ChangInConsolidScopeWithOtherReason(HandleIndexContent):
    '''
              其他原因的合并范围变动
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInConsolidScopeWithOtherReason, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b080500']:
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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}

        if len(instructi) > 1:
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.chang_in_consolid_scope_with_other_reason = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    chang_in_consolid_scope_with_other_reason=instructi
                )

class ChangInShareOfOwnerEquitiInSu(HandleIndexContent):
    '''
          在子公司所有者权益份额发生变化的情况说明
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInShareOfOwnerEquitiInSu, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b090201']:
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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}

        if len(instructi) > 1:
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.chang_share_of_owner_equiti_in_subsidiari = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    chang_share_of_owner_equiti_in_subsidiari=instructi
                )

class TransactImpactInChangeShareOfSubsidiari(HandleIndexContent):
    '''
              交易对于少数股东权益及归属于母公司所有者权益的影响
           '''
    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(TransactImpactInChangeShareOfSubsidiari, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b090202']:
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
            company_names = list(df.iloc[0,1:])
            project_names = list(df.iloc[1:,0])

            for key, company_name in enumerate(company_names):
                if models.CompanyName.objects.filter(name=company_name):
                    obj_name = models.CompanyName.objects.get(name=company_name)
                else:
                    obj_name = models.CompanyName.objects.create(name=company_name)

                for i, project_name in enumerate(project_names):

                    amount = df.iloc[(i + 1), (key + 1)]
                    amount = Decimal(re.sub(',', '', str(amount))) * unit_change[unit] if is_num(amount) else 0.00
                    if models.TransactImpactInChangeShareOfSubsidiari.objects.filter(stk_cd_id=self.stk_cd_id,
                                                                         acc_per=self.acc_per,
                                                                         project_name=project_name,
                                                                         typ_rep_id='A',
                                                                         name_id=obj_name.id):
                        obj = models.TransactImpactInChangeShareOfSubsidiari.objects.get(stk_cd_id=self.stk_cd_id,
                                                                             project_name=project_name,
                                                                             acc_per=self.acc_per,
                                                                             typ_rep_id='A',
                                                                             name_id=obj_name.id)
                        obj.amount = amount
                        obj.save()
                    else:
                        models.TransactImpactInChangeShareOfSubsidiari.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            typ_rep_id='A',
                            name_id=obj_name.id,
                            project_name=project_name,
                            amount=amount
                        )
        else:
            pass

class TheDeterminBasiAndAccountPolic(HandleIndexContent):
    '''
          报告分部的确定依据与会计政策
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(TheDeterminBasiAndAccountPolic, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b100601']:
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

        if len(instructi) > 1:
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.determin_basi_and_account_report_divis = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    determin_basi_and_account_report_divis=instructi
                )

class ReportDivisFinanciInform(HandleIndexContent):
    '''
              报告分部的财务信息
           '''
    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ReportDivisFinanciInform, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b100602']:
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
            company_names = list(df.iloc[0,1:])
            project_names = list(df.iloc[1:,0])

            for key, company_name in enumerate(company_names):
                if models.CompanyName.objects.filter(name=company_name):
                    obj_name = models.CompanyName.objects.get(name=company_name)
                else:
                    obj_name = models.CompanyName.objects.create(name=company_name)

                for i, project_name in enumerate(project_names):

                    amount = df.iloc[(i + 1), (key + 1)]
                    amount = Decimal(re.sub(',', '', str(amount))) * unit_change[unit] if is_num(amount) else 0.00
                    print(amount)
                    if models.ReportDivisFinanciInform.objects.filter(stk_cd_id=self.stk_cd_id,
                                                                         acc_per=self.acc_per,
                                                                         project_name=project_name,
                                                                         typ_rep_id='A',
                                                                         name_id=obj_name.id):
                        obj = models.ReportDivisFinanciInform.objects.get(stk_cd_id=self.stk_cd_id,
                                                                             project_name=project_name,
                                                                             acc_per=self.acc_per,
                                                                             typ_rep_id='A',
                                                                             name_id=obj_name.id)
                        obj.amount = amount
                        obj.save()
                    else:
                        models.ReportDivisFinanciInform.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            typ_rep_id='A',
                            name_id=obj_name.id,
                            project_name=project_name,
                            amount=amount
                        )
        else:
            pass

class OtherImportTransactAndEvent(HandleIndexContent):
    '''
          其他对投资者决策有影响的重要事项
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OtherImportTransactAndEvent, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b100700']:
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

        if len(instructi) > 1:
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.other_import_transact_and_event = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    other_import_transact_and_event=instructi
                )