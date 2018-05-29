# _author : litufu
# date : 2018/4/24

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import re
import numpy as np
from collections import OrderedDict
from itertools import chain
import pandas as pd

from report_data_extract import models
from utils.handleindexcontent.commons import save_instructi,recognize_df_and_instucti,recognize_instucti,get_dfs
from utils.handleindexcontent.base import create_and_update
from utils.handleindexcontent.base import HandleIndexContent
from utils.mytools import remove_space_from_df,remove_per_from_df,similar,num_to_decimal

class ChangInOrdinariShare(HandleIndexContent):
    '''
       普通股股份变动情况表
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInOrdinariShare, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0601010100','06010100']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            quantiti_befor_chang_pos = list(np.where((df.iloc[0, :].str.contains('本次变动前'))&(df.iloc[1, :].str.contains('数量')))[0])
            issu_new_share_pos = list(np.where(df.iloc[1, :].str.contains('发行新股'))[0])
            give_share_pos = list(np.where(df.iloc[1, :].str.contains('送股'))[0])
            turnov_from_cpf_pos = list(np.where(df.iloc[1, :].str.contains('公积金转股'))[0])
            other_pos = list(np.where(df.iloc[1, :].str.contains('其他'))[0])
            subtot_chang_pos = list(np.where(df.iloc[1, :].str.contains('小计'))[0])
            quantiti_after_chang_pos = list(np.where((df.iloc[0, :].str.contains('本次变动后'))&(df.iloc[1, :].str.contains('数量')))[0])

            choice_dict = {
                '一、有限售条件股份':'restrict_sale',
                '1、国家持股':'state_hold',
                '2、国有法人持股':'state_own_legal_pers',
                '3、其他内资持股':'other_domest_capit',
                '其中：境内非国有法人持股':'domest_non_state_own',
                '境内自然人持股':'domest_natur_person',
                '4、外资持股':'foreign_hold',
                '其中：境外法人持股':'oversea_legal_person',
                '境外自然人持股':'oversea_natur_person',
                '二、无限售条件流通股份':'unlimit_sale',
                '1、人民币普通股':'rmb_ordinari_share',
                '2、境内上市的外资股':'domest_list_foreign',
                '3、境外上市的外资股':'overseas_list_foreig',
                '4、其他':'others',
                '三、普通股股份总数':'total_number',
            }
            df = df.drop([0,1])
            projects = []
            for item in df.iloc[:, 0]:
                for key in choice_dict.keys():
                    if similar(str(item),str(key)):
                        projects.append(choice_dict[key])


            quantiti_befor_changs = list(df.iloc[:, quantiti_befor_chang_pos[0]])
            issu_new_shares = list(df.iloc[:, issu_new_share_pos[0]])
            give_shares = list(df.iloc[:, give_share_pos[0]])
            turnov_from_cpfs = list(df.iloc[:, turnov_from_cpf_pos[0]])
            others = list(df.iloc[:, other_pos[0]])
            subtot_changs = list(df.iloc[:, subtot_chang_pos[0]])
            quantiti_after_changs = list(df.iloc[:, quantiti_after_chang_pos[0]])

            for (project,quantiti_befor_chang,issu_new_share,give_share,turnov_from_cpf,
                           other,subtot_chang ,quantiti_after_chang) \
                    in zip(projects,quantiti_befor_changs,issu_new_shares,give_shares,turnov_from_cpfs,
                           others,subtot_changs ,quantiti_after_changs):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    name=project,
                    quantiti_befor_chang=quantiti_befor_chang if quantiti_befor_chang != 'nan' else 0,
                    issu_new_share=issu_new_share if issu_new_share != 'nan' else 0,
                    give_share=give_share if give_share != 'nan' else 0,
                    turnov_from_cpf=turnov_from_cpf if turnov_from_cpf != 'nan' else 0,
                    other=other if other != 'nan' else 0,
                    subtot_chang=subtot_chang if subtot_chang != 'nan' else 0,
                    quantiti_after_chang=quantiti_after_chang if quantiti_after_chang != 'nan' else 0,
                )
                create_and_update('ChangInOrdinariShare',**value_dict)
        else:
            pass
        save_instructi(instructi,models.ChangInShareAndSharehold,self.stk_cd_id,self.acc_per,'change_desc')

class DescriptOfChangInCommonStock(HandleIndexContent):
    '''
               普通股股份变动情况说明
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DescriptOfChangInCommonStock, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0601010200']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.ChangInShareAndSharehold, self.stk_cd_id, self.acc_per, 'change_desc')

class ChangInRestrictSaleOfShare(HandleIndexContent):
    '''
           限售股份变动情况
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInRestrictSaleOfShare, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0601020000','06010200']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            sharehold_name_pos = list(np.where(df.iloc[0, :].str.contains('股东名称'))[0])
            begin_pos = list(np.where(df.iloc[0, :].str.contains('初限售股数'))[0])
            releas_pos = list(np.where(df.iloc[0, :].str.contains('解除限售股数'))[0])
            increas_pos = list(np.where(df.iloc[0, :].str.contains('增加限售股数'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('末限售股数'))[0])
            reason_pos = list(np.where(df.iloc[0, :].str.contains('限售原因'))[0])
            restrict_sale_date_pos = list(np.where(df.iloc[0, :].str.contains('解除限售日期'))[0])

            df = df.drop([0,len(df)-1])

            sharehold_names = list(df.iloc[:, sharehold_name_pos[0]])
            begins = list(df.iloc[:, begin_pos[0]])
            releases = list(df.iloc[:, releas_pos[0]])
            increases = list(df.iloc[:, increas_pos[0]])
            ends = list(df.iloc[:, end_pos[0]])
            reasons = list(df.iloc[:, reason_pos[0]])
            restrict_sale_dates = list(df.iloc[:, restrict_sale_date_pos[0]])

            for (sharehold_name,begin,releas,increas,end, reason,restrict_sale_date) \
                    in zip(sharehold_names,begins,releases,increases,ends, reasons,restrict_sale_dates):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    sharehold_name=sharehold_name,
                    begin=begin if begin != 'nan' else 0,
                    releas=releas if releas != 'nan' else 0,
                    increas=increas if increas != 'nan' else 0,
                    end=end if end != 'nan' else 0,
                    reason=reason,
                    restrict_sale_date=restrict_sale_date,
                )
                create_and_update('ChangInRestrictSaleOfShare',**value_dict)
        else:
            pass

class SecurIssuanc(HandleIndexContent):
    '''
           证券发行情况
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(SecurIssuanc, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['06020100']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        dfs = get_dfs(('股票','债券','衍生证券'),item)
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
        if dfs.get('股票') is not None:
            df = dfs.get('股票')
            type = 'stock'
            stock = df.iloc[0,0]
            date =df.iloc[0,1]
            price =df.iloc[0,2]
            num =df.iloc[0,3]
            to_market_date =df.iloc[0,4]
            number_permit_trade =df.iloc[0,5]
            transact_termin_date =df.iloc[0,6]

            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                type=type,
                stock=stock,
                date=date,
                price=price,
                num=num,
                to_market_date=to_market_date,
                number_permit_trade=number_permit_trade,
                transact_termin_date=transact_termin_date,
            )
            create_and_update('SecurIssuanc',**value_dict)
        else:
            pass
        save_instructi(instructi, models.ChangInShareAndSharehold, self.stk_cd_id, self.acc_per, 'secur_issuanc')


class ChangInShare(HandleIndexContent):
    '''
    公司股份总数及股东结构的变动、公司资产和负债结构的变动情况说明
    '''
    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInShare, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['06020200']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.ChangInShareAndSharehold, self.stk_cd_id, self.acc_per, 'share_change_desc')


class TotalNumberOfSharehold(HandleIndexContent):
    '''
       股东总数
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(TotalNumberOfSharehold, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0603010000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            report_end_sharehold_num_pos = list(np.where(df.iloc[:, 0].str.contains('截止报告期末普通股股东总数'))[0])
            disclos_last_month_sharehold_num_pos = list(np.where(df.iloc[:, 0].str.contains('披露日前上一月末的普通股股东总数'))[0])

            report_end_sharehold_num = df.iloc[report_end_sharehold_num_pos[0],1]
            disclos_last_month_sharehold_num = df.iloc[disclos_last_month_sharehold_num_pos[0],1]

            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                report_end_sharehold_num=report_end_sharehold_num,
                disclos_last_month_sharehold_num=disclos_last_month_sharehold_num,
            )
            create_and_update('ChangInShareAndSharehold',**value_dict)
        else:
            pass

class TopTenSharehold(HandleIndexContent):
    '''
    前十名股东持股情况
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(TopTenSharehold, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0603020000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('质押或冻结情况').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['topten'] = df
                                elif table.iloc[0, :].str.contains('股份种类').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['unlimit_sale'] = df
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
        # print(dfs)
        if dfs.get('topten') is not None:
            df= dfs.get('topten')
            sharehold_name_pos = list(np.where(df.iloc[0, :].str.contains('股东名称'))[0])
            increas_and_decreas_pos = list(np.where(df.iloc[0, :].str.contains('报告期内增减'))[0])
            end_hold_num_pos = list(np.where(df.iloc[0, :].str.contains('期末持股数量'))[0])
            ratio_pos = list(np.where(df.iloc[0, :].str.contains('比例'))[0])
            restrict_share_pos = list(np.where(df.iloc[0, :].str.contains('持有有限售条件股份数量'))[0])
            natur_of_sharehold_pos = list(np.where(df.iloc[0, :].str.contains('股东性质'))[0])

            df = df.drop([0,1])

            sharehold_names = list(df.iloc[:, sharehold_name_pos[0]])
            increas_and_decreases = list(df.iloc[:, increas_and_decreas_pos[0]])
            end_hold_nums = list(df.iloc[:, end_hold_num_pos[0]])
            ratios = list(df.iloc[:, ratio_pos[0]])
            restrict_shares = list(df.iloc[:, restrict_share_pos[0]])
            pledg_or_freez_statuses = list(df.iloc[:, (restrict_share_pos[0]+1)])
            pledg_or_freez_nums = list(df.iloc[:, (restrict_share_pos[0]+2)])
            natur_of_shareholds = list(df.iloc[:, (natur_of_sharehold_pos[0])])

            for (sharehold_name, increas_and_decreas, end_hold_num, ratio, \
                           restrict_share,pledg_or_freez_status,pledg_or_freez_num,natur_of_sharehold) \
                    in zip(sharehold_names, increas_and_decreases, end_hold_nums, ratios, \
                           restrict_shares,pledg_or_freez_statuses,pledg_or_freez_nums,natur_of_shareholds ):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    sharehold_name=sharehold_name,
                    increas_and_decreas=increas_and_decreas if increas_and_decreas != 'nan' else 0,
                    end_hold_num=end_hold_num if end_hold_num != 'nan' else 0,
                    ratio=num_to_decimal(ratio),
                    restrict_share=restrict_share if restrict_share != 'nan' else 0,
                    pledg_or_freez_status=pledg_or_freez_status,
                    pledg_or_freez_num=pledg_or_freez_num if pledg_or_freez_num != 'nan' else 0,
                    natur_of_sharehold=natur_of_sharehold,
                )
                create_and_update('TopTenSharehold',**value_dict)
        else:
            pass

        if dfs.get('unlimit_sale') is not None:
            df= dfs.get('unlimit_sale')
            sharehold_name_pos = list(np.where(df.iloc[0, :].str.contains('股东名称'))[0])
            hold_num_pos = list(np.where(df.iloc[0, :].str.contains('持有无限售条件流通股的数量'))[0])

            sharehold_relat_pos = list(np.where(df.iloc[:,0].str.contains('上述股东关联关系或一致行动的说明'))[0])
            sharehold_relat = df.iloc[sharehold_relat_pos[0],1]

            df = df.drop([0,1,len(df)-1])

            sharehold_names = list(df.iloc[:, sharehold_name_pos[0]])
            hold_nums = list(df.iloc[:, hold_num_pos[0]])
            types = list(df.iloc[:, (hold_num_pos[0]+1)])
            type_nums = list(df.iloc[:, (hold_num_pos[0]+2)])


            for (sharehold_name,hold_num,type,type_num) \
                    in zip(sharehold_names,hold_nums,types,type_nums):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    sharehold_name=sharehold_name,
                    hold_num=hold_num if hold_num != 'nan' else 0,
                    type=type,
                    type_num=type_num if type_num != 'nan' else 0,

                )
                create_and_update('TopTenUnlimitSharehold',**value_dict)

            save_instructi(sharehold_relat,models.ChangInShareAndSharehold,self.stk_cd_id,self.acc_per,'sharehold_relat')

        else:
            pass

class TopTenShareholdSZ(HandleIndexContent):
    '''
        前十名股东持股情况
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(TopTenShareholdSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['06030100']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        dfs = get_dfs(('持股5%以上','无限售条件'),item)
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
        if dfs.get('持股5%以上') is not None:
            df = dfs.get('持股5%以上')
            sharehold_name_pos = list(np.where(df.iloc[0, :].str.contains('股东名称'))[0])
            increas_and_decreas_pos = list(np.where(df.iloc[0, :].str.contains('报告期内增减'))[0])
            end_hold_num_pos = list(np.where(df.iloc[0, :].str.contains('期末持股数量'))[0])
            ratio_pos = list(np.where(df.iloc[0, :].str.contains('比例'))[0])
            restrict_share_pos = list(np.where(df.iloc[0, :].str.contains('持有有限售条件'))[0])
            natur_of_sharehold_pos = list(np.where(df.iloc[0, :].str.contains('股东性质'))[0])
            pledg_or_freez_pos = list(np.where(df.iloc[0, :].str.contains('质押或冻结情况'))[0])

            stragy_investor = list(np.where(df.iloc[:, 0].str.contains('战略投资者'))[0])
            sharehold_relat_pos = list(np.where(df.iloc[:, 0].str.contains('上述股东关联关系或一致行动的说明'))[0])
            sharehold_relat = df.iloc[sharehold_relat_pos[0], 2]

            df  =  df.iloc[2:stragy_investor[0],:] if len(stragy_investor)>0 else df.drop([0, 1,len(df)-1])

            sharehold_names = list(df.iloc[:, sharehold_name_pos[0]])
            increas_and_decreases = list(df.iloc[:, increas_and_decreas_pos[0]])
            end_hold_nums = list(df.iloc[:, end_hold_num_pos[0]])
            ratios = list(df.iloc[:, ratio_pos[0]])
            restrict_shares = list(df.iloc[:, restrict_share_pos[0]])
            pledg_or_freez_statuses = list(df.iloc[:, pledg_or_freez_pos[0]])
            pledg_or_freez_nums = list(df.iloc[:, pledg_or_freez_pos[1]])
            natur_of_shareholds = list(df.iloc[:, (natur_of_sharehold_pos[0])])

            for (sharehold_name, increas_and_decreas, end_hold_num, ratio, \
                 restrict_share, pledg_or_freez_status, pledg_or_freez_num, natur_of_sharehold) \
                    in zip(sharehold_names, increas_and_decreases, end_hold_nums, ratios, \
                           restrict_shares, pledg_or_freez_statuses, pledg_or_freez_nums, natur_of_shareholds):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    sharehold_name=sharehold_name,
                    increas_and_decreas=num_to_decimal(increas_and_decreas),
                    end_hold_num=num_to_decimal(end_hold_num),
                    ratio=num_to_decimal(ratio),
                    restrict_share=num_to_decimal(restrict_share),
                    pledg_or_freez_status=pledg_or_freez_status,
                    pledg_or_freez_num=num_to_decimal(pledg_or_freez_num),
                    natur_of_sharehold=natur_of_sharehold,
                )
                create_and_update('TopTenSharehold',**value_dict)

            save_instructi(sharehold_relat,models.ChangInShareAndSharehold,self.stk_cd_id,self.acc_per,'sharehold_relat')
        else:
            pass

        if dfs.get('无限售条件') is not None:
            df = dfs.get('无限售条件')
            sharehold_name_pos = list(np.where(df.iloc[0, :].str.contains('股东名称'))[0])
            hold_num_pos = list(np.where(df.iloc[0, :].str.contains('持有无限售条件'))[0])
            type_pos = list(np.where(df.iloc[0, :].str.contains('股份种类'))[0])

            unlimit_sharehold_relat_pos = list(np.where(df.iloc[:, 0].str.contains('前10名无限售流通股股东之间'))[0])
            unlimit_sharehold_relat = df.iloc[unlimit_sharehold_relat_pos[0], 1]

            pattern = re.compile('^[\d,\.]*?$')
            start_pos = list(
                np.where(df.iloc[:, hold_num_pos[0]].str.match(pattern) | df.iloc[:, hold_num_pos[0]].str.match('nan'))[0])

            sharehold_names = list(df.iloc[start_pos[0]:start_pos[-1], sharehold_name_pos[0]])
            hold_nums = list(df.iloc[start_pos[0]:start_pos[-1], hold_num_pos[0]])
            types = list(df.iloc[start_pos[0]:start_pos[-1], type_pos[0]])
            type_nums = list(df.iloc[start_pos[0]:start_pos[-1], type_pos[1]])

            for (sharehold_name, hold_num, type, type_num) \
                    in zip(sharehold_names, hold_nums, types, type_nums):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    sharehold_name=sharehold_name,
                    hold_num=hold_num if hold_num != 'nan' else 0,
                    type=type,
                    type_num=type_num if type_num != 'nan' else 0,
                )
                create_and_update('TopTenUnlimitSharehold',**value_dict)
            save_instructi(unlimit_sharehold_relat,models.ChangInShareAndSharehold,self.stk_cd_id,self.acc_per,'unlimit_sharehold_relat')
        else:
            pass

        if dfs.get('first') is not None:
            df = dfs.get('first')
            print(df)
            report_end_sharehold_num_pos = list(np.where(df.iloc[0, :].str.contains('报告期末普通股股东总数'))[0])
            disclos_last_month_sharehold_num_pos = list(np.where(df.iloc[0, :].str.contains('报告披露日前上一月末普通股股东总数'))[0])

            report_end_sharehold_num = df.iloc[0,report_end_sharehold_num_pos[0]+1]
            disclos_last_month_sharehold_num = df.iloc[0,disclos_last_month_sharehold_num_pos[0]+1]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                report_end_sharehold_num=report_end_sharehold_num,
                disclos_last_month_sharehold_num=disclos_last_month_sharehold_num,
            )
            create_and_update('ChangInShareAndSharehold',**value_dict)
        else:
            pass

class ControlShareholdCorpor(HandleIndexContent):
    '''
        控股股东情况-法人
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ControlShareholdCorpor, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0604010100']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df)>0:
            name_pos = list(np.where(df.iloc[:, 0].str.contains('名称'))[0])
            unit_owner_pos = list(np.where(df.iloc[:, 0].str.contains('单位负责人或法定代表人'))[0])
            date_of_establish_pos = list(np.where(df.iloc[:, 0].str.contains('成立日期'))[0])
            main_busines_pos = list(np.where(df.iloc[:, 0].str.contains('主要经营业务'))[0])
            contor_other_list_com_pos = list(np.where(df.iloc[:, 0].str.contains('报告期内控股和参股的其他境内外上市公司的股权情况'))[0])
            other_desc_pos = list(np.where(df.iloc[:, 0].str.contains('其他情况说明'))[0])

            # df = df.drop([0, 1])

            name = df.iloc[name_pos[0],1]
            unit_owner = df.iloc[unit_owner_pos[0],1]
            date_of_establish = df.iloc[date_of_establish_pos[0],1]
            main_busines = df.iloc[main_busines_pos[0],1]
            contor_other_list_com = df.iloc[contor_other_list_com_pos[0],1]
            other_desc = df.iloc[other_desc_pos[0],1]

            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                type='cs',
                name=name,
                unit_owner=unit_owner,
                date_of_establish=date_of_establish,
                main_busines=main_busines,
                control_other_list_com=contor_other_list_com,
                other_desc=other_desc,
            )
            create_and_update('ShareholdCorpor',**value_dict)
        else:
            pass

class ControlShareholdSZ(HandleIndexContent):
    '''
            控股股东情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ControlShareholdSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['06030200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:, 0].str.contains('主要职业及职务').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['np_control'] = df
                                elif table.iloc[:, 0].str.contains('变更日期').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['control_change'] = df
                                else:
                                    #增加法人描述
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
        if dfs.get('np_control') is not None:
            df = dfs.get('np_control')
            name_pos = list(np.where(df.iloc[0, :].str.contains('控股股东姓名'))[0])
            countri_of_citizensh_pos = list(np.where(df.iloc[0, :].str.contains('国籍'))[0])
            other_right_of_abod_pos = list(np.where(df.iloc[0, :].str.contains('是否取得其他国家或地区居留权'))[0])
            major_occup_and_job_pos = list(np.where(df.iloc[:, 0].str.contains('主要职业及职务'))[0])
            control_other_list_com_pos = list(np.where(df.iloc[:, 0].str.contains('报告期内控股和参股的其他境内外上市公司的股权情况'))[0])

            name = df.iloc[1, name_pos[0]]
            countri_of_citizensh = df.iloc[1, countri_of_citizensh_pos[0]]
            other_right_of_abod = df.iloc[1, other_right_of_abod_pos[0]]
            major_occup_and_job = df.iloc[major_occup_and_job_pos[0], 1]
            control_other_list_com = df.iloc[control_other_list_com_pos[0], 1]

            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                type='cs',
                name=name,
                countri_of_citizensh=countri_of_citizensh,
                other_right_of_abod=other_right_of_abod,
                major_occup_and_job=major_occup_and_job,
                control_other_list_com=control_other_list_com,
            )
            create_and_update('ControlShareholdNaturPerson',**value_dict)
        else:
            pass

        if dfs.get('np_control') is not None and dfs.get('control_change') is not None:
            df = dfs.get('control_change')
            chang_date_pos = list(np.where(df.iloc[:, 0].str.contains('变更日期'))[0])
            chang_date = df.iloc[chang_date_pos[0], 1]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                chang_date=chang_date,
            )
            create_and_update('ControlShareholdNaturPerson',**value_dict)
        else:
            pass

class TheActualControlCorpor(HandleIndexContent):
    '''
            实际控制人-法人
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(TheActualControlCorpor, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0604020100']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        # print(dfs)
        if df is not None and len(df) > 0:
            name_pos = list(np.where(df.iloc[:, 0].str.contains('名称'))[0])
            # unit_owner_pos = list(np.where(df.iloc[:, 0].str.contains('单位负责人或法定代表人'))[0])
            # date_of_establish_pos = list(np.where(df.iloc[:, 0].str.contains('成立日期'))[0])
            # main_busines_pos = list(np.where(df.iloc[:, 0].str.contains('主要经营业务'))[0])
            # contor_other_list_com_pos = list(np.where(df.iloc[:, 0].str.contains('报告期内控股和参股的其他境内外上市公司的股权情况'))[0])
            # other_desc_pos = list(np.where(df.iloc[:, 0].str.contains('其他情况说明'))[0])

            # df = df.drop([0, 1])

            name = df.iloc[name_pos[0], 1]
            # unit_owner = df.iloc[unit_owner_pos[0], 1]
            # date_of_establish = df.iloc[date_of_establish_pos[0], 1]
            # main_busines = df.iloc[main_busines_pos[0], 1]
            # contor_other_list_com = df.iloc[contor_other_list_com_pos[0], 1]
            # other_desc = df.iloc[other_desc_pos[0], 1]

            if models.ShareholdCorpor.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ShareholdCorpor.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.type = 'ac'
                obj.name = name
                # obj.unit_owner = unit_owner
                # obj.date_of_establish = date_of_establish
                # obj.main_busines = main_busines
                # obj.contor_other_list_com = contor_other_list_com
                # obj.other_desc = other_desc
                obj.save()
            else:
                models.ShareholdCorpor.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    type='ac',
                    name=name,
                    # unit_owner=unit_owner,
                    # date_of_establish=date_of_establish,
                    # main_busines=main_busines,
                    # contor_other_list_com=contor_other_list_com,
                    # other_desc=other_desc,

                )
        else:
            pass

class TheActualControlSZ(HandleIndexContent):
    '''
            实际控制人
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(TheActualControlSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['06030300']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:, 0].str.contains('主要职业及职务').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['np_control'] = df
                                elif table.iloc[:, 0].str.contains('变更日期').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['control_change'] = df
                                else:
                                    #增加法人描述
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
        if dfs.get('np_control') is not None:
            df = dfs.get('np_control')
            name_pos = list(np.where(df.iloc[0, :].str.contains('实际控制人姓名'))[0])
            countri_of_citizensh_pos = list(np.where(df.iloc[0, :].str.contains('国籍'))[0])
            other_right_of_abod_pos = list(np.where(df.iloc[0, :].str.contains('是否取得其他国家或地区居留权'))[0])
            major_occup_and_job_pos = list(np.where(df.iloc[:, 0].str.contains('主要职业及职务'))[0])
            sharehold_other_company_pos = list(np.where(df.iloc[:, 0].str.contains('过去10年曾控股的境内外上市公司情况'))[0])

            name = df.iloc[1, name_pos[0]]
            countri_of_citizensh = df.iloc[1, countri_of_citizensh_pos[0]]
            other_right_of_abod = df.iloc[1, other_right_of_abod_pos[0]]
            major_occup_and_job = df.iloc[major_occup_and_job_pos[0], 1]
            sharehold_other_company = df.iloc[sharehold_other_company_pos[0], 1]

            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                type='ac',
                name=name,
                countri_of_citizensh=countri_of_citizensh,
                other_right_of_abod=other_right_of_abod,
                major_occup_and_job=major_occup_and_job,
                sharehold_other_company=sharehold_other_company,
            )
            create_and_update('ControlShareholdNaturPerson',**value_dict)
        else:
            pass

        if dfs.get('np_control') is not None and dfs.get('control_change') is not None:
            df = dfs.get('control_change')
            chang_date_pos = list(np.where(df.iloc[:, 0].str.contains('变更日期'))[0])
            chang_date = df.iloc[chang_date_pos[0], 1]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                ac_chang_date=chang_date,
            )
            create_and_update('ControlShareholdNaturPerson',**value_dict)
        else:
            pass

class OtherCorporShareholdMoreThanTen(HandleIndexContent):
    '''
    其他持股在 10%以上的法人股东
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OtherCorporShareholdMoreThanTen, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['06030400']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df)>0:
            name_pos = list(np.where(df.iloc[0, :].str.contains('法人股东名称'))[0])
            unit_owner_pos = list(np.where(df.iloc[0, :].str.contains('法定代表人'))[0])
            date_of_establish_pos = list(np.where(df.iloc[0, :].str.contains('成立日期'))[0])
            main_busines_pos = list(np.where(df.iloc[0, :].str.contains('主要经营业务或管理活动'))[0])
            regist_capit_pos = list(np.where(df.iloc[0, :].str.contains('注册资本'))[0])

            names = list(df.iloc[:, name_pos[0]])
            unit_owners = list(df.iloc[:, unit_owner_pos[0]])
            date_of_establishs = list(df.iloc[:, date_of_establish_pos[0]])
            main_busineses = list(df.iloc[:, main_busines_pos[0]])
            regist_capits = list(df.iloc[:, regist_capit_pos[0]])

            for (name,unit_owner,date_of_establish,main_busines,regist_capit) in\
                    zip(names,unit_owners,date_of_establishs,main_busineses,regist_capits):

                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    type='os',
                    name=name,
                    unit_owner=unit_owner,
                    date_of_establish=date_of_establish,
                    main_busines=main_busines,
                    regist_capit=regist_capit,
                )
                create_and_update('ShareholdCorpor',**value_dict)
        else:
            pass

class RestrictOnSharehold(HandleIndexContent):
    '''
           控股股东、实际控制人、重组方及其他承诺主体股份限制减持情况
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RestrictOnSharehold, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['06030500']
        pass


    def converse(self):
        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.ChangInShareAndSharehold, self.stk_cd_id, self.acc_per, 'restrict_on_sharehold')

