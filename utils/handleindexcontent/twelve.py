# _author : litufu
# date : 2018/5/10
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import re
import numpy as np
import jieba
from collections import OrderedDict
from itertools import chain
import pandas as pd

from report_data_extract import models
from config.fs import manage_config
from utils.handleindexcontent.base import HandleIndexContent,create_and_update
from utils.mytools import remove_space_from_df,remove_per_from_df,similar,num_to_decimal
from utils.handleindexcontent.commons import save_instructi,save_combine_instructi,get_values,compute_start_pos,\
    recognize_df_and_instucti,recognize_instucti

class CompositOfEnterprisGroup(HandleIndexContent):
    '''
                  企业集团的构成
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CompositOfEnterprisGroup, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b09010100','0b09030100','0b090101','0b090301']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        natures = {'0b09010100':'s','0b09030100':'j','0b090101':'s','0b090301':"j"}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            company_name_pos = list(np.where(df.iloc[0, :].str.contains('名称'))[0])
            main_place_of_busi_pos = list(np.where(df.iloc[0, :].str.contains('主要经营地'))[0])
            registr_place_pos = list(np.where(df.iloc[0, :].str.contains('注册地'))[0])
            busi_natur_pos = list(np.where(df.iloc[0, :].str.contains('业务性质'))[0])
            direct_sharehold_pos = list(np.where(df.iloc[1, :].str.contains('直接'))[0])
            indirect_sharehold_pos = list(np.where(df.iloc[1, :].str.contains('间接'))[0])
            acquisit_style_pos = list(np.where(df.iloc[0, :].str.contains('取得方式'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                company_names = get_values(df,start_pos,company_name_pos,'t')
                main_place_of_busis = get_values(df,start_pos,main_place_of_busi_pos,'t')
                registr_places = get_values(df,start_pos,registr_place_pos,'t')
                busi_naturs =  get_values(df,start_pos,busi_natur_pos,'t')
                direct_shareholds =  get_values(df,start_pos,direct_sharehold_pos,'d')
                indirect_shareholds =  get_values(df,start_pos,indirect_sharehold_pos,'d')
                acquisit_styles = get_values(df,start_pos,acquisit_style_pos,'t')

                for (company_name, main_place_of_busi, registr_place, busi_natur,
                            direct_sharehold,indirect_sharehold,acquisit_style) in \
                        zip(company_names, main_place_of_busis, registr_places, busi_naturs,
                            direct_shareholds,indirect_shareholds,acquisit_styles):
                    if models.CompanyName.objects.filter(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per, company_name=company_name):
                        obj_name = models.CompanyName.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per, company_name=company_name)
                    else:
                        obj_name = models.CompanyName.objects.create(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,natur_of_the_unit=natures[self.indexno], company_name=company_name)

                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        company_name_id=obj_name.id,
                        main_place_of_busi=main_place_of_busi,
                        registr_place=registr_place,
                        busi_natur=busi_natur,
                        direct_sharehold=direct_sharehold,
                        indirect_sharehold=indirect_sharehold,
                        acquisit_style=acquisit_style,
                    )
                    create_and_update('CompositOfEnterprisGroup',**value_dict)
        else:
            pass

        if len(instructi) > 0 and self.indexno=='0b09010100':
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,typ_rep_id='A'):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,typ_rep_id='A')
                obj.composit_of_enterpris_group = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    composit_of_enterpris_group=instructi
                )

        if len(instructi) > 0 and self.indexno=='0b09030100':
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,typ_rep_id='A'):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,typ_rep_id='A')
                obj.joint_ventur = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    joint_ventur=instructi
                )

class ImportNonwhollyownSubsidia(HandleIndexContent):
    '''
                  重要的非全资子公司
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ImportNonwhollyownSubsidia, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b09010200','0b090102']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            subcompani_name_pos = list(np.where(df.iloc[0, :].str.contains('子公司名称'))[0])
            minor_sharehold_pos = list(np.where(df.iloc[0, :].str.contains('少数股东持股比例'))[0])
            profit_attrib_to_minor_pos = list(np.where(df.iloc[0, :].str.contains('归属于少数股东的损益'))[0])
            dividend_to_minor_pos = list(np.where(df.iloc[0, :].str.contains('本期向少数股东宣告分派的股利'))[0])
            minor_equiti_pos = list(np.where(df.iloc[1, :].str.contains('期末少数股东权益余额'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                subcompani_names = get_values(df,start_pos,subcompani_name_pos,'t')
                minor_shareholds = get_values(df,start_pos,minor_sharehold_pos,'t')
                profit_attrib_to_minors = get_values(df,start_pos,profit_attrib_to_minor_pos,'d')
                dividend_to_minors = get_values(df,start_pos,dividend_to_minor_pos,'d')
                minor_equitis = get_values(df,start_pos,minor_equiti_pos,'d')

                for (subcompani_name, minor_sharehold, profit_attrib_to_minor, dividend_to_minor,minor_equiti) in \
                        zip(subcompani_names, minor_shareholds, profit_attrib_to_minors, dividend_to_minors,minor_equitis):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        subcompani_name=subcompani_name,
                        minor_sharehold=num_to_decimal(minor_sharehold, unit),
                        profit_attrib_to_minor=num_to_decimal(profit_attrib_to_minor, unit),
                        dividend_to_minor=num_to_decimal(dividend_to_minor, unit),
                        minor_equiti=num_to_decimal(minor_equiti, unit),
                    )
                    create_and_update('ImportNonwhollyownSubsidia',**value_dict)
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
        subject_dict = {'流动资产':'1','非流动资产':'2','资产合计':'3',
                        '流动负债':'4','非流动负债':'5','负债合计':'6',
                        '营业收入':'7','净利润':'8','综合收益总额':'9','经营活动现金流量':'10'}
        if dfs.get('asset') is not None :
            df = dfs['asset']
            df = df.set_index([0])
            df = df.T
            df = df.set_index(['子公司名称'])
            all_dict = df.to_dict()
            for company_name in all_dict:
                for item in all_dict[company_name]:
                    before_end_item,subject_item = item
                    before_end = before_end_dict[before_end_item]
                    name = subject_dict[subject_item]
                    value = all_dict[company_name][item]
                    value = num_to_decimal(value,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        company_type='s',
                        before_end=before_end,
                        company_name=company_name,
                        name=name,
                        amount=value
                    )
                    create_and_update('MajorNonwhollyownSubsidiaryFinanciInform',**value_dict)

class JointPoolFinanciInform(HandleIndexContent):
    '''
                      联营企业和合营企业财务信息
                   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(JointPoolFinanciInform, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos =  ['0b09030200','0b09030300','0b090302','0b090303']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        company_type_dict = {'0b09030200':'j','0b09030300':'p','0b090302':'j','0b090303':'p'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        subject_dict = {'流动资产':'1','非流动资产':'2','资产合计':'3',\
                        '流动负债':'4','非流动负债':'5','负债合计':'6', \
                        '营业收入': '7', '净利润': '8', '综合收益总额': '9', '经营活动现金流量': '10',
                        '现金及现金等价物':'11','少数股东权益':'12','净资产':'13','净资产份额':'14',\
                        '调整事项':'15','商誉':'16','内部交易未实现利润':'17','其他调整':'18',\
                        '权益投资的账面价值':'19','权益投资的公允价值':'20','财务费用':'21','所得税费用':'22',\
                        '终止经营的净利润':'23','其他综合收益':'24','股利':'25'
                        }
        if df is not None  and len(df)>1:
            end_poses = list(np.where(df.iloc[0, :].str.contains('期末'))[0])
            before_poses = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            subjects = list(df.iloc[:,0])
            before_end_poses = {'e':end_poses,'b':before_poses}
            for before_end in before_end_poses:
                for pos in before_end_poses[before_end]:
                    company_name = df.iloc[1,pos]
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
                            name = subject_dict[subject_name]
                            value = df.iloc[subject_pos,pos]
                            value = num_to_decimal(value,unit)
                            value_dict = dict(
                                stk_cd_id=self.stk_cd_id,
                                acc_per=self.acc_per,
                                typ_rep_id='A',
                                company_type=company_type_dict[self.indexno],
                                before_end=before_end,
                                company_name=company_name,
                                name=name,
                                amount=value
                            )
                            create_and_update('MajorNonwhollyownSubsidiaryFinanciInform',**value_dict)
                        else:
                            pass

class RiskRelatToFinanciInstrument(HandleIndexContent):
    '''
                      与金融工具相关的风险
                   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RiskRelatToFinanciInstrument, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b0a000000','0b0a0000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_combine_instructi(instructi,models.ComprehensNote,self.stk_cd_id,self.acc_per,'A','risk_relat_to_financi_instrument')


class ParentCompaniAndActualControl(HandleIndexContent):
    '''
                          本企业的母公司情况
                       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ParentCompaniAndActualControl, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b0c010000','0b0c0100']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        pattern = re.compile('^.*?最终控制方是(.*?)。其他说明：(.*?)$')
        parent_compani_name = ''
        registr_place = ''
        busi_natur = ''
        regist_capit = 0.00
        parent_company_share = 0.00
        parent_company_vote_right = 0.00
        if df is not None and len(df)>1:
            parent_compani_name_pos = list(np.where(df.iloc[0, :].str.contains('母公司名称'))[0])
            registr_place_pos = list(np.where(df.iloc[0, :].str.contains('注册地'))[0])
            busi_natur_pos = list(np.where(df.iloc[0, :].str.contains('业务性质'))[0])
            regist_capit_pos = list(np.where(df.iloc[0, :].str.contains('注册资本'))[0])
            parent_company_share_pos = list(np.where(df.iloc[0, :].str.contains('持股比例'))[0])
            parent_company_vote_right_pos = list(np.where(df.iloc[0, :].str.contains('表决权比例'))[0])
            if len(df) == 2:
                parent_compani_name = df.iloc[1, parent_compani_name_pos[0]]
                registr_place = df.iloc[1, registr_place_pos[0]]
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
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                typ_rep_id='A',
                parent_compani_name=parent_compani_name,
                registr_place=registr_place,
                busi_natur=busi_natur,
                regist_capit=regist_capit,
                parent_company_share=parent_company_share,
                parent_company_vote_right=parent_company_vote_right,
                actual_control=actual_control,
                desc=desc,
            )
            create_and_update('ParentCompaniAndActualControl',**value_dict)

class OtherRelat(HandleIndexContent):
    '''
                             其他关联方
                          '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OtherRelat, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b0c040000','0b0c0400']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('名称'))[0])
            relationship_pos = list(np.where(df.iloc[0, :].str.contains('关系'))[0])

            names = list(df.iloc[1:,name_pos[0]])
            relationships = list(df.iloc[1:,relationship_pos[0]])
            for (name,relationship) in zip(names,relationships):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    name=name,
                    relationship=relationship,
                )
                create_and_update('OtherRelat',**value_dict)

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
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        transact_type=transact_type,
                        name=name,
                        content=content,
                        before=num_to_decimal(before, unit),
                        end=num_to_decimal(end, unit),
                        approv_transact_amou=approv_transact_amou,
                        is_exceed_amount=is_exceed_amount,
                    )
                    create_and_update('PurchasAndSale',**value_dict)

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
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        transact_type=transact_type,
                        name=name,
                        content=content,
                        before=num_to_decimal(before, unit),
                        end=num_to_decimal(end, unit),
                    )
                    create_and_update('RelatPartiLeas',**value_dict)

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
                instructs = list(df.iloc[:, 4])

                for (name, amount, start_date, expiri_date,instruct) in \
                        zip(names, amounts, start_dates, expiri_dates,instructs):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        transact_type=transact_type,
                        name=name,
                        amount=num_to_decimal(amount, unit),
                        start_date=start_date,
                        expiri_date=expiri_date,
                        instruct=instruct,
                    )
                    create_and_update('MoneyLend',**value_dict)

class RelatAssetTransferDebtRestructur(HandleIndexContent):
    '''
             关联方资产转让、债务重组情况
          '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RelatAssetTransferDebtRestructur, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b0c050600','0b0c0506']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
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
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    transact_type='atdr',
                    name=name,
                    content=content,
                    before=num_to_decimal(before, unit),
                    end=num_to_decimal(end, unit),
                )
                create_and_update('PurchasAndSale',**value_dict)

class KeyManagStaffRemuner(HandleIndexContent):
    '''
                 关键管理人员薪酬
              '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(KeyManagStaffRemuner, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b0c050700','0b0c0507']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
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
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    name=name,
                    before=num_to_decimal(before, unit),
                    end=num_to_decimal(end, unit),
                )
                create_and_update("KeyManagStaffRemuner",**value_dict)

class OtherRelatTransact(HandleIndexContent):
    '''
                  其他关联交易
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OtherRelatTransact, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b0c050800','0b0c0508']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A',
                       'other_relat_transact')

class RelatReceivPayabl(HandleIndexContent):
    '''
                 关联方应收应付款
              '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RelatReceivPayabl, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b0c060100','0b0c060200','0b0c0601','0b0c0602']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        natur_of_payment_dict = {'0b0c060100':'r','0b0c060200':'p','0b0c0601':'r','0b0c0602':'p'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            df = df[df.iloc[:, 0] != '合计']
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            relat_parti_name_pos = list(np.where(df.iloc[0, :].str.contains('关联方'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])
            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                relat_parti_names = get_values(df,start_pos,relat_parti_name_pos,'t')
                before_values = get_values(df,start_pos,before_pos,'d')
                before_bad_debt_prepars = get_values(df,start_pos, before_pos[1],'d') if len(before_pos) == 2 else [0.00 for i in range(len(names))]
                end_values = get_values(df,start_pos, end_pos,'d')
                end_bad_debt_prepars = get_values(df,start_pos, end_pos[1],'d')  if len(end_pos) == 2 else [0.00 for i in range(len(names))]

                all_dict = {'b':list(zip(before_values,before_bad_debt_prepars)),
                            'e':list(zip(end_values,end_bad_debt_prepars))}

                for before_end in all_dict:
                    for name,relat_parti_name,value in zip(names,relat_parti_names,all_dict[before_end]):
                        book_value,bad_debt_prepar = value
                        value_dict = dict(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            typ_rep_id='A',
                            before_end=before_end,
                            natur_of_payment=natur_of_payment_dict[self.indexno],
                            subject=name,
                            relat_parti_name=relat_parti_name,
                            balanc=num_to_decimal(book_value, unit),
                            bad_debt_prepar=num_to_decimal(bad_debt_prepar, unit),
                        )
                        create_and_update('RelatReceivPayabl',**value_dict)

class RelatPartiCommit(HandleIndexContent):
    '''
                  关联方承诺
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RelatPartiCommit, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b0c070000','0b0c0700']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A',
                       'relat_parti_commit')

class ImportCommit(HandleIndexContent):
    '''
                  重要承诺事项
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ImportCommit, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b0e010000','0b0e0100']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A',
                       'import_commit')

class Conting(HandleIndexContent):
    '''
                  或有事项
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(Conting, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos= ['0b0e020100','0b0e0201']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A',
                       'conting')

class InvestInSubsidiari(HandleIndexContent):
    '''
                      对子公司的投资
                   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(InvestInSubsidiari, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b11030100','0b110301']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            print(df)
            # df = df[df.iloc[:,0]!="合计"]
            company_name_pos = list(np.where(df.iloc[0, :].str.contains('被投资单位'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初余额'))[0])
            increase_pos = list(np.where(df.iloc[0, :].str.contains('本期增加'))[0])
            cut_back_pos = list(np.where(df.iloc[0, :].str.contains('本期减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末余额'))[0])
            impair_pos = list(np.where(df.iloc[0, :].str.contains('计提减值准备'))[0])
            impair_balanc_pos = list(np.where(df.iloc[0, :].str.contains('减值准备期末余额'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                company_names = get_values(df,start_pos,company_name_pos,'t')
                befores = get_values(df,start_pos,before_pos,'d')
                increases = get_values(df,start_pos,increase_pos,'d')
                cut_backs = get_values(df,start_pos,cut_back_pos,'d')
                ends = get_values(df,start_pos,end_pos,'d')
                impairs = get_values(df,start_pos,impair_pos,'d')
                impair_balancs = get_values(df,start_pos,impair_balanc_pos,'d')
                for (company_name, before, increase, cut_back, end,impair,impair_balanc) in \
                        zip(company_names, befores, increases, cut_backs, ends,impairs,impair_balancs):

                    if models.CompanyName.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, company_name=company_name):
                        obj_name = models.CompanyName.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, company_name=company_name)
                    else:
                        obj_name = models.CompanyName.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,natur_of_the_unit='s', company_name=company_name)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        company_name_id=obj_name.id,
                        before=num_to_decimal(before, unit),
                        increase=num_to_decimal(increase, unit),
                        cut_back=num_to_decimal(cut_back, unit),
                        end=num_to_decimal(end, unit),
                        impair=num_to_decimal(impair, unit),
                        impair_balanc=num_to_decimal(impair_balanc, unit),
                    )
                    create_and_update('InvestInSubsidiari',**value_dict)
        else:
            pass


class ReturnOnEquitiAndEarnPerShare(HandleIndexContent):
    '''
                          净资产收益率及每股收益
                       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ReturnOnEquitiAndEarnPerShare, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b12020000','0b120200']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
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
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    gain_or_loss_type=gain_or_loss_type,
                    return_on_equiti=num_to_decimal(return_on_equiti),
                    eps=num_to_decimal(basic_earn_per_share),
                    deps=num_to_decimal(dilut_earn_per_share),
                )
                create_and_update('ReturnOnEquitiAndEarnPerShare',**value_dict)
        else:
            pass

class BusiMergerNotUnderTheSameControl(HandleIndexContent):
    '''
                  本期发生的非同一控制下企业合并
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BusiMergerNotUnderTheSameControl, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b080101']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            company_name_pos = list(np.where(df.iloc[0, :].str.contains('被购买方名称'))[0])
            acquisit_time_pos = list(np.where(df.iloc[0, :].str.contains('股权取得时点'))[0])
            acquisit_cost_pos = list(np.where(df.iloc[0, :].str.contains('股权取得成本'))[0])
            acquisit_rate_pos = list(np.where(df.iloc[0, :].str.contains('股权取得比例'))[0])
            acquisit_style_pos = list(np.where(df.iloc[0, :].str.contains('取得方式'))[0])
            purchas_day_pos = list(np.where(df.iloc[0, :].str.contains('购买日'))[0])
            purchas_day_determi_basi_pos = list(np.where(df.iloc[0, :].str.contains('购买日的确定依据'))[0])
            income_pos = list(np.where(df.iloc[0, :].str.contains('购买日至期末被购买方的收入'))[0])
            np_pos = list(np.where(df.iloc[0, :].str.contains('购买日至期末被购买方的净利润'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                company_names = get_values(df,start_pos,company_name_pos,'t')
                acquisit_times = get_values(df,start_pos,acquisit_time_pos,'t')
                acquisit_costs = get_values(df,start_pos,acquisit_cost_pos,'d')
                acquisit_rates = get_values(df,start_pos,acquisit_rate_pos,'d')
                acquisit_styles = get_values(df,start_pos,acquisit_style_pos,'t')
                purchas_days = get_values(df,start_pos,purchas_day_pos,'t')
                purchas_day_determi_basis =  get_values(df,start_pos,purchas_day_determi_basi_pos,'t')
                incomes = get_values(df,start_pos,income_pos,'d')
                nps = get_values(df,start_pos,np_pos,'d')

                for (company_name, acquisit_time, acquisit_cost, acquisit_rate,acquisit_style,purchas_day,
                            purchas_day_determi_basi,income,net_profit) in\
                        zip(company_names, acquisit_times, acquisit_costs, acquisit_rates,acquisit_styles,purchas_days,
                            purchas_day_determi_basis,incomes,nps):
                    if models.CompanyName.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, company_name=company_name):
                        obj_name = models.CompanyName.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, company_name=company_name)
                    else:
                        obj_name = models.CompanyName.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, company_name=company_name)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        company_name_id=obj_name.id,
                        acquisit_time=acquisit_time,
                        acquisit_cost=num_to_decimal(acquisit_cost, unit),
                        acquisit_rate=num_to_decimal(acquisit_rate),
                        acquisit_style=acquisit_style,
                        purchas_day=purchas_day,
                        purchas_day_determi_basi=purchas_day_determi_basi,
                        income=num_to_decimal(income, unit),
                        np=num_to_decimal(net_profit, unit)
                    )
                    create_and_update('BusiMergerNotUnderTheSameControl',**value_dict)
        else:
            pass



class ConsolidCostAndGoodwil(HandleIndexContent):
    '''
      合并成本及商誉
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ConsolidCostAndGoodwil, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b080102']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 8:
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

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                company_names = get_values(df,start_pos,0,'t')
                cashs = get_values(df,start_pos,cash_pos,'d')
                non_cash_assets = get_values(df,start_pos,non_cash_asset_pos,'d')
                issu_or_assum_debts = get_values(df,start_pos,issu_or_assum_debt_pos,'d')
                issuanc_of_equiti_securs = get_values(df,start_pos,issuanc_of_equiti_secur_pos,'d')
                or_have_considers = get_values(df,start_pos,or_have_consider_pos,'d')
                share_held_prior_to_the_acquiss = get_values(df,start_pos,share_held_prior_to_the_acquis_pos,'d')
                others = get_values(df,start_pos,other_pos,'d')
                total_combin_costs =  get_values(df,start_pos,total_combin_cost_pos,'d')
                recogniz_net_asset_fair_valus = get_values(df,start_pos,recogniz_net_asset_fair_valu_pos,'d')
                goodwils = get_values(df,start_pos,goodwil_pos,'d')

                for (company_name,cash, non_cash_asset, issu_or_assum_debt, issuanc_of_equiti_secur, or_have_consider, share_held_prior_to_the_acquis,
                            other, total_combin_cost, recogniz_net_asset_fair_valu,goodwil) in \
                        zip(company_names,cashs, non_cash_assets, issu_or_assum_debts, issuanc_of_equiti_securs, or_have_considers, share_held_prior_to_the_acquiss,
                            others, total_combin_costs, recogniz_net_asset_fair_valus,goodwils):
                    if models.CompanyName.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, company_name=company_name):
                        obj_name = models.CompanyName.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, company_name=company_name)
                    else:
                        obj_name = models.CompanyName.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                     company_name=company_name)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        company_name_id=obj_name.id,
                        cash=num_to_decimal(cash, unit),
                        non_cash_asset=num_to_decimal(non_cash_asset, unit),
                        issu_or_assum_debt=num_to_decimal(issu_or_assum_debt, unit),
                        issuanc_of_equiti_secur=num_to_decimal(issuanc_of_equiti_secur, unit),
                        or_have_consider=num_to_decimal(or_have_consider, unit),
                        share_held_prior_to_the_acquis=num_to_decimal(share_held_prior_to_the_acquis, unit),
                        other=num_to_decimal(other, unit),
                        total_combin_cost=num_to_decimal(total_combin_cost, unit),
                        recogniz_net_asset_fair_valu=num_to_decimal(recogniz_net_asset_fair_valu, unit),
                        goodwil=num_to_decimal(goodwil, unit),
                    )
                    create_and_update('ConsolidCostAndGoodwil',**value_dict)
        else:
            pass
        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A',
                       'consolid_cost_and_goodwil')

class AcquireRecognisAssetAndLiab(HandleIndexContent):
    '''
          被购买方于购买日可辨认资产、负债
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AcquireRecognisAssetAndLiab, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b080103']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        value_type_dict={'购买日公允价值':'f','购买日账面价值':'b'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            df = df.set_index([0])
            df = df.dropna(how='all')
            df = df.reset_index()

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                subjects = list(df.iloc[start_pos[0]:,:])
                company_names = list(df.iloc[0,1:])
                value_types = list(df.iloc[1,1:])

                for key,company_name in enumerate(company_names):
                    if models.CompanyName.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, company_name=company_name):
                        obj_name = models.CompanyName.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, company_name=company_name)
                    else:
                        obj_name = models.CompanyName.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                     company_name=company_name)

                    value_type_name = value_types[key]

                    if value_type_dict.get(value_type_name) is not None:
                        value_type = value_type_dict[value_type_name]
                        for i,subject in enumerate(subjects):

                            if models.SubjectName.objects.filter(name=subject):
                                subject_name = models.SubjectName.objects.get(name=subject)
                            else:
                                subject_name = models.SubjectName.objects.create(name=subject)


                            amount = df.iloc[(start_pos[0]+i),(key+1)]
                            amount = num_to_decimal(amount,unit)
                            value_dict = dict(
                                stk_cd_id=self.stk_cd_id,
                                acc_per=self.acc_per,
                                typ_rep_id='A',
                                company_name_id=obj_name.id,
                                value_type=value_type,
                                subject_id=subject_name.id,
                                amount=amount
                            )
                            create_and_update('AcquireRecognisAssetAndLiab',**value_dict)
        else:
            pass

class BusiMergerUnderTheSameControl(HandleIndexContent):
    '''
                      本期发生的同一控制下企业合并
                   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BusiMergerUnderTheSameControl, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b080201']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            company_name_pos = list(np.where(df.iloc[0, :].str.contains('被合并方名称'))[0])
            acquisit_rate_pos = list(np.where(df.iloc[0, :].str.contains('企业合并中取得的权益比例'))[0])
            same_control_basi_pos = list(np.where(df.iloc[0, :].str.contains('构成同一控制下企业合并的依据'))[0])
            merger_date_pos = list(np.where(df.iloc[0, :].str.contains('合并日'))[0])
            merger_date_determi_basi_pos = list(np.where(df.iloc[0, :].str.contains('合并日的确定依据'))[0])
            this_income_pos = list(np.where(df.iloc[0, :].str.contains('初至合并日被合并方的收入'))[0])
            this_np_pos = list(np.where(df.iloc[0, :].str.contains('初至合并日被合并方的净利润'))[0])
            before_income_pos = list(np.where(df.iloc[0, :].str.contains('比较期间被合并方的收入'))[0])
            before_np_pos = list(np.where(df.iloc[0, :].str.contains('比较期间被合并方的净利润'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                company_names = get_values(df,start_pos,company_name_pos,'t')
                acquisit_rates = get_values(df,start_pos,acquisit_rate_pos,'t')
                same_control_basis = get_values(df,start_pos,same_control_basi_pos,'t')
                merger_dates = get_values(df,start_pos,merger_date_pos,'t')
                merger_date_determi_basis = get_values(df,start_pos,merger_date_determi_basi_pos,'t')
                this_incomes = get_values(df,start_pos,this_income_pos,'d')
                this_nps = get_values(df,start_pos,this_np_pos,'d')
                before_incomes = get_values(df,start_pos,before_income_pos,'d')
                before_nps = get_values(df,start_pos,before_np_pos,'d')

                for (company_name, acquisit_rate,same_control_basi,merger_date,merger_date_determi_basi,
                            this_income,this_np,before_income,before_np) in \
                        zip(company_names, acquisit_rates,same_control_basis,merger_dates,merger_date_determi_basis,
                            this_incomes,this_nps,before_incomes,before_nps):
                    if models.CompanyName.objects.filter(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name):
                        obj_name = models.CompanyName.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name)
                    else:
                        obj_name = models.CompanyName.objects.create(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        company_name_id=obj_name.id,
                        acquisit_rate=num_to_decimal(acquisit_rate),
                        same_control_basi=same_control_basi,
                        merger_date=merger_date,
                        merger_date_determi_basi=merger_date_determi_basi,
                        this_income=num_to_decimal(this_income, unit),
                        this_np=num_to_decimal(this_np, unit),
                        before_income=num_to_decimal(before_income, unit),
                        before_np=num_to_decimal(before_np, unit)
                    )
                    create_and_update('BusiMergerUnderTheSameControl',**value_dict)
        else:
            pass

class ConsolidCost(HandleIndexContent):
    '''
          合并成本
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ConsolidCost, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b080202']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 4:
            df = df.T
            cash_pos = list(np.where(df.iloc[0, :].str.contains('现金'))[0])
            non_cash_asset_pos = list(np.where(df.iloc[0, :].str.contains('非现金资产'))[0])
            issu_or_assum_debt_pos = list(np.where(df.iloc[0, :].str.contains('发行或承担的债务'))[0])
            issuanc_of_equiti_secur_pos = list(np.where(df.iloc[0, :].str.contains('权益性证券'))[0])
            or_have_consider_pos = list(np.where(df.iloc[0, :].str.contains('或有对价'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                company_names = get_values(df,start_pos,0,'t')
                cashs = get_values(df,start_pos,cash_pos,'d')
                non_cash_assets = get_values(df,start_pos,non_cash_asset_pos,'d')
                issu_or_assum_debts = get_values(df,start_pos,issu_or_assum_debt_pos,'d')
                issuanc_of_equiti_securs = get_values(df,start_pos,issuanc_of_equiti_secur_pos,'d')
                or_have_considers = get_values(df,start_pos,or_have_consider_pos,'d')

                for (company_name, cash, non_cash_asset, issu_or_assum_debt, issuanc_of_equiti_secur, or_have_consider,
                     ) in \
                        zip(company_names, cashs, non_cash_assets, issu_or_assum_debts, issuanc_of_equiti_securs, or_have_considers,
                            ):
                    if models.CompanyName.objects.filter(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name):
                        obj_name = models.CompanyName.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name)
                    else:
                        obj_name = models.CompanyName.objects.create(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        company_name_id=obj_name.id,
                        cash=num_to_decimal(cash, unit),
                        non_cash_asset=num_to_decimal(non_cash_asset, unit),
                        issu_or_assum_debt=num_to_decimal(issu_or_assum_debt, unit),
                        issuanc_of_equiti_secur=num_to_decimal(issuanc_of_equiti_secur, unit),
                        or_have_consider=num_to_decimal(or_have_consider, unit),
                    )
                    create_and_update('ConsolidCost',**value_dict)
        else:
            pass
        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A',
                       'consolid_cost')

class BookValuOfAssetAndLiabil(HandleIndexContent):
    '''
              合并日被合并方资产、负债的账面价值
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BookValuOfAssetAndLiabil, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b080203']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        deadlin_dict = {'合并日': 'm', '上年年末': 'b'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            df = df.set_index([0])
            df = df.dropna(how='all')
            df = df.reset_index()

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                subjects = list(df.iloc[start_pos[0]:, :])
                company_names = list(df.iloc[0, 1:])
                deadlins = list(df.iloc[1, 1:])

                for key, company_name in enumerate(company_names):
                    if models.CompanyName.objects.filter(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name):
                        obj_name = models.CompanyName.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name)
                    else:
                        obj_name = models.CompanyName.objects.create(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name)

                    deadlin_name = deadlins[key]
                    if deadlin_dict.get(deadlin_name) is not None:
                        deadlin = deadlin_dict[deadlin_name]
                        for i, subject in enumerate(subjects):

                            if models.SubjectName.objects.filter(name=subject):
                                subject_name = models.SubjectName.objects.get(name=subject)
                            else:
                                subject_name = models.SubjectName.objects.create(name=subject)

                            amount = df.iloc[(start_pos[0] + i), (key + 1)]
                            amount = num_to_decimal(amount,unit)
                            value_dict = dict(
                                stk_cd_id=self.stk_cd_id,
                                acc_per=self.acc_per,
                                typ_rep_id='A',
                                company_name_id=obj_name.id,
                                deadlin=deadlin,
                                subject_id=subject_name.id,
                                amount=amount
                            )
                            create_and_update('AcquireRecognisAssetAndLiab',**value_dict)
        else:
            pass

class ReversPurchas(HandleIndexContent):
    '''
          反向购买
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ReversPurchas, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b080300']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A',
                       'revers_purchas')

class ChangInConsolidScopeWithOtherReason(HandleIndexContent):
    '''
              其他原因的合并范围变动
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInConsolidScopeWithOtherReason, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b080500']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A',
                       'chang_in_consolid_scope_with_other_reason')


class ChangInShareOfOwnerEquitiInSu(HandleIndexContent):
    '''
          在子公司所有者权益份额发生变化的情况说明
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInShareOfOwnerEquitiInSu, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b090201']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A',
                       'chang_share_of_owner_equiti_in_subsidiari')


class TransactImpactInChangeShareOfSubsidiari(HandleIndexContent):
    '''
              交易对于少数股东权益及归属于母公司所有者权益的影响
           '''
    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(TransactImpactInChangeShareOfSubsidiari, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b090202']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            company_names = list(df.iloc[0,1:])
            project_names = list(df.iloc[1:,0])

            for key, company_name in enumerate(company_names):
                if models.CompanyName.objects.filter(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name):
                    obj_name = models.CompanyName.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name)
                else:
                    obj_name = models.CompanyName.objects.create(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name)

                for i, project_name in enumerate(project_names):

                    amount = df.iloc[(i + 1), (key + 1)]
                    amount = num_to_decimal(amount,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        project_name=project_name,
                        amount=amount
                    )
                    create_and_update('TransactImpactInChangeShareOfSubsidiari',**value_dict)
        else:
            pass

class TheDeterminBasiAndAccountPolic(HandleIndexContent):
    '''
          报告分部的确定依据与会计政策
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(TheDeterminBasiAndAccountPolic, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b100601']
        pass

    def converse(self):
        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A',
                       'determin_basi_and_account_report_divis')

class ReportDivisFinanciInform(HandleIndexContent):
    '''
              报告分部的财务信息
           '''
    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ReportDivisFinanciInform, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b100602']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            company_names = list(df.iloc[0,1:])
            names = list(df.iloc[1:,0])

            for key, company_name in enumerate(company_names):
                if models.CompanyName.objects.filter(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name):
                    obj_name = models.CompanyName.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name)
                else:
                    obj_name = models.CompanyName.objects.create(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,company_name=company_name)

                for i, name in enumerate(names):

                    amount = df.iloc[(i + 1), (key + 1)]
                    amount = num_to_decimal(amount,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        company_name_id=obj_name.id,
                        name=name,
                        amount=amount
                    )
                    create_and_update('ReportDivisFinanciInform',**value_dict)
        else:
            pass

class OtherImportTransactAndEvent(HandleIndexContent):
    '''
          其他对投资者决策有影响的重要事项
       '''
    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OtherImportTransactAndEvent, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b100700']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A',
                       'other_import_transact_and_event')
