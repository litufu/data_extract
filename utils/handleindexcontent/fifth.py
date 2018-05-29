# _author : litufu
# date : 2018/4/23

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import re
import numpy as np
from collections import OrderedDict
from itertools import chain
import pandas as pd

from report_data_extract import models
from utils.handleindexcontent.commons import save_instructi
from utils.handleindexcontent.base import HandleIndexContent
from utils.mytools import remove_space_from_df,remove_per_from_df,num_to_decimal
from utils.handleindexcontent.commons import recognize_df_and_instucti,recognize_instucti,save_instructi
from utils.handleindexcontent.base import create_and_update

class CashDividendPolici(HandleIndexContent):
    '''
               现金分红政策的制定、执行或调整情况
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CashDividendPolici, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0501010000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi,models.ImportMatter,self.stk_cd_id,self.acc_per,'cash_dividend_polici')


class CashDividendPoliciSZ(HandleIndexContent):
    '''
               现金分红政策的制定、执行或调整情况
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CashDividendPoliciSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['05010000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('报告期内盈利且母公司可供普通股股东分配利润为正但未提出普通股现金红利分配预案的原因').any():
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
        if df is not None and len(df)>0:
            posit_profit_no_divi = df.iloc[1,0]
            purpos_of_profit = df.iloc[1,1]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                posit_profit_no_divi=posit_profit_no_divi,
                purpos_of_profit=purpos_of_profit
            )
            create_and_update('ImportMatter',**value_dict)
        save_instructi(instructi, models.ImportMatter, self.stk_cd_id, self.acc_per, 'cash_dividend_polici')


class DistributPlan(HandleIndexContent):
    '''
        公司近三年（含报告期）的普通股股利分配方案或预案、资本公积金转增股本方案或预案
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DistributPlan, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0501020000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        year = str(self.acc_per.year)
        if df is not None and len(df) > 0:
            year_pos = list(np.where((df.iloc[:, 0].str.contains(year)))[0])
            number_of_bonu_share_pos = list(np.where((df.iloc[0, :].str.contains('每10股送红股数')))[0])
            number_of_dividend_pos = list(np.where((df.iloc[0, :].str.contains('每10股派息数')))[0])
            transfer_increas_pos = list(np.where((df.iloc[0, :].str.contains('每10股转增数')))[0])
            amount_of_cash_divid_pos = list(np.where((df.iloc[0, :].str.contains('现金分红的数额')))[0])
            common_sharehold_np_pos = list(np.where((df.iloc[0, :].str.contains('合并报表中归属于上市公司普通股股东的净利润')))[0])
            distribut_ratio_pos = list(np.where((df.iloc[0, :].str.contains('占合并报表中归属于上市公司普通股股东的净利润的比率')))[0])
            number_of_bonu_share = num_to_decimal(df.iloc[year_pos[0],number_of_bonu_share_pos[0]])
            number_of_dividend =  num_to_decimal(df.iloc[year_pos[0],number_of_dividend_pos[0]])
            transfer_increas =  num_to_decimal(df.iloc[year_pos[0],transfer_increas_pos[0]])
            amount_of_cash_divid = num_to_decimal(df.iloc[year_pos[0],amount_of_cash_divid_pos[0]],unit)
            common_sharehold_np = num_to_decimal(df.iloc[year_pos[0],common_sharehold_np_pos[0]],unit)
            distribut_ratio = num_to_decimal(df.iloc[year_pos[0],distribut_ratio_pos[0]],unit)

            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                number_of_bonu_share=number_of_bonu_share,
                number_of_dividend=number_of_dividend,
                transfer_increas=transfer_increas,
                amount_of_cash_divid=amount_of_cash_divid,
                common_sharehold_np=common_sharehold_np,
                distribut_ratio=distribut_ratio
            )
            create_and_update('CashDividendPolici',**value_dict)
        else:
            pass
        save_instructi(instructi, models.ImportMatter, self.stk_cd_id, self.acc_per, 'distribute_plan')


class DistributPlanSZ(HandleIndexContent):
    '''
        本报告期利润分配及资本公积金转增股本预案
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DistributPlanSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['05020000']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        year = str(self.acc_per.year)
        if df is not None and len(df) > 0:
            pattern = re.compile('^.*?现金分红总额（(.*?元)）.*?$')

            number_of_bonu_share_pos = list(np.where((df.iloc[:,0].str.contains('每10股送红股数')))[0])
            number_of_dividend_pos = list(np.where((df.iloc[:,0].str.contains('每10股派息数')))[0])
            transfer_increas_pos = list(np.where((df.iloc[:,0].str.contains('每10股转增数')))[0])
            amount_of_cash_divid_pos = list(np.where((df.iloc[:,0].str.contains('现金分红')))[0])
            distribut_profit_pos = list(np.where((df.iloc[:,0].str.contains('可分配利润')))[0])
            prop_of_distribut_profit_pos = list(np.where((df.iloc[:,0].str.contains('现金分红占利润分配总额的比例')))[0])

            unit = pattern.match(df.iloc[amount_of_cash_divid_pos[0],0]).groups()[0]

            number_of_bonu_share = num_to_decimal(df.iloc[number_of_bonu_share_pos[0],1])
            number_of_dividend = num_to_decimal(df.iloc[number_of_dividend_pos[0],1])
            transfer_increas = num_to_decimal(df.iloc[transfer_increas_pos[0],1])
            amount_of_cash_divid = num_to_decimal(df.iloc[amount_of_cash_divid_pos[0],1],unit)
            distribut_profit = num_to_decimal(df.iloc[distribut_profit_pos[0],1],unit)
            prop_of_distribut_profit = num_to_decimal(df.iloc[prop_of_distribut_profit_pos[0],1])

            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                number_of_bonu_share=number_of_bonu_share,
                number_of_dividend=number_of_dividend,
                transfer_increas=transfer_increas,
                amount_of_cash_divid=amount_of_cash_divid,
                distribut_profit=distribut_profit,
                prop_of_distribut_profit=prop_of_distribut_profit
            )
            create_and_update('CashDividendPolici',**value_dict)
        else:
            pass
        save_instructi(instructi, models.ImportMatter, self.stk_cd_id, self.acc_per, 'distribute_plan')


class Commit(HandleIndexContent):
    '''
       公司实际控制人、股东、关联方、收购人以及公司等承诺相关方在报告期内或持续到报告
       期内的承诺事项
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(Commit, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0502010000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            background_pos = list(np.where((df.iloc[0, :].str.contains('承诺背景')))[0])
            type_pos = list(np.where((df.iloc[0, :].str.contains('承诺类型')))[0])
            parti_pos = list(np.where((df.iloc[0, :].str.contains('承诺方')))[0])
            content_pos = list(np.where((df.iloc[0, :].str.contains('承诺内容')))[0])
            time_and_deadline_pos = list(np.where((df.iloc[0, :].str.contains('承诺时间及期限')))[0])
            is_there_deadline_pos = list(np.where((df.iloc[0, :].str.contains('是否有履行期限')))[0])
            is_strictli_perform_pos = list(np.where((df.iloc[0, :].str.contains('是否及时严格履行')))[0])
            reason_for_incomplet_pos = list(np.where((df.iloc[0, :].str.contains('如未能及时履行应说明未完成履行的具体原因')))[0])
            failur_to_perform_pos = list(np.where((df.iloc[0, :].str.contains('如未能及时履行应说明下一步计划')))[0])

            df = df.drop([0])

            backgrounds = list(df.iloc[:,background_pos[0]])
            types = list(df.iloc[:,type_pos[0]])
            partis = list(df.iloc[:,parti_pos[0]])
            contents = list(df.iloc[:,content_pos[0]])
            time_and_deadlines = list(df.iloc[:,time_and_deadline_pos[0]])
            is_there_deadlines = list(df.iloc[:,is_there_deadline_pos[0]])
            is_strictli_performs = list(df.iloc[:,is_strictli_perform_pos[0]])
            reason_for_incomplets = list(df.iloc[:,reason_for_incomplet_pos[0]])
            failur_to_performs = list(df.iloc[:,failur_to_perform_pos[0]])


            for (background,commit_type,parti,content,time_and_deadline, \
                       is_there_deadline,is_strictli_perform,reason_for_incomplet,failur_to_perform) \
                in zip(backgrounds,types,partis,contents,time_and_deadlines, \
                       is_there_deadlines,is_strictli_performs,reason_for_incomplets,failur_to_performs ):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    background=background,
                    commit_type=commit_type,
                    parti=parti,
                    content=content,
                    time_and_deadline=time_and_deadline,
                    is_there_deadline=is_there_deadline,
                    is_strictli_perform=is_strictli_perform,
                    reason_for_incomplet=reason_for_incomplet,
                    failur_to_perform=failur_to_perform,
                )
                create_and_update('Commit',**value_dict)
        else:
            pass
        save_instructi(instructi, models.ImportMatter, self.stk_cd_id, self.acc_per, 'commit')

class CommitSZ(HandleIndexContent):
    '''
       公司实际控制人、股东、关联方、收购人以及公司等承诺相关方在报告期内或持续到报告
       期内的承诺事项
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CommitSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['05030100']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            background_pos = list(np.where((df.iloc[0, :].str.contains('承诺事由')|df.iloc[0, :].str.contains('承诺来源')))[0])
            type_pos = list(np.where((df.iloc[0, :].str.contains('承诺类型')))[0])
            parti_pos = list(np.where((df.iloc[0, :].str.contains('承诺方')))[0])
            content_pos = list(np.where((df.iloc[0, :].str.contains('承诺内容')))[0])
            time_pos = list(np.where((df.iloc[0, :].str.contains('承诺时间')))[0])
            deadline_pos = list(np.where((df.iloc[0, :].str.contains('承诺期限')))[0])
            perform_pos = list(np.where((df.iloc[0, :].str.contains('履行情况')))[0])

            df = df.drop([0,len(df)-1])

            backgrounds = list(df.iloc[:, background_pos[0]])
            types = list(df.iloc[:, type_pos[0]]) if len(type_pos)>0 else ['' for i in range(len(backgrounds))]
            partis = list(df.iloc[:, parti_pos[0]]) if len(parti_pos)>0 else ['' for i in range(len(backgrounds))]
            contents = list(df.iloc[:, content_pos[0]]) if len(content_pos)>0 else ['' for i in range(len(backgrounds))]
            times = list(df.iloc[:, time_pos[0]]) if len(time_pos)>0 else ['' for i in range(len(backgrounds))]
            deadlines = list(df.iloc[:, deadline_pos[0]]) if len(deadline_pos)>0 else ['' for i in range(len(backgrounds))]
            performs = list(df.iloc[:, perform_pos[0]]) if len(perform_pos)>0 else ['' for i in range(len(backgrounds))]

            for (background, commit_type, parti, content,time,deadline,perform ) \
                    in zip(backgrounds, types, partis, contents,times,deadlines,performs):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    background=background,
                    commit_type=commit_type,
                    parti=parti,
                    content=content,
                    time=time,
                    deadline=deadline,
                    perform=perform,
                )
                create_and_update('Commit',**value_dict)
        else:
            pass
        save_instructi(instructi, models.ImportMatter, self.stk_cd_id, self.acc_per, 'commit')


class ProfitPredict(HandleIndexContent):
    '''
       业绩预测
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ProfitPredict, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0502020000','05030200']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):

        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        pattern0 = re.compile('^.*?当期预测业绩（(.*?元)）.*?$')
        pattern1 = re.compile('^.*?当期实际业绩（(.*?元)）.*?$')
        if df is not None and len(df) > 0:
            asset_or_project_nam_pos = list(np.where((df.iloc[0, :].str.contains('项目名称')))[0])
            start_time_pos = list(np.where((df.iloc[0, :].str.contains('预测起始时间')))[0])
            end_time_pos = list(np.where((df.iloc[0, :].str.contains('预测终止时间')))[0])
            forecast_perform_pos = list(np.where((df.iloc[0, :].str.contains('当期预测业绩')))[0])
            actual_result_pos = list(np.where((df.iloc[0, :].str.contains('当期实际业绩')))[0])
            unpredict_reason_pos = list(np.where((df.iloc[0, :].str.contains('未达预测的原因')))[0])
            origin_disclosur_date_pos = list(np.where((df.iloc[0, :].str.contains('原预测披露日期')))[0])
            origin_disclosur_index_pos = list(np.where((df.iloc[0, :].str.contains('原预测披露索引')))[0])
            forecast_perform_unit = pattern0.match(df.iloc[0, forecast_perform_pos[0]]).groups()[0]
            actual_result_unit = pattern1.match(df.iloc[0, actual_result_pos[0]]).groups()[0]

            df = df.drop([0])

            asset_or_project_nams = list(df.iloc[:,asset_or_project_nam_pos[0]])
            start_times = list(df.iloc[:,start_time_pos[0]])
            end_times = list(df.iloc[:,end_time_pos[0]])
            forecast_performs = list(df.iloc[:,forecast_perform_pos[0]])
            actual_results = list(df.iloc[:,actual_result_pos[0]])
            unpredict_reasons = list(df.iloc[:,unpredict_reason_pos[0]])
            origin_disclosur_dates = list(df.iloc[:,origin_disclosur_date_pos[0]])
            origin_disclosur_indexs = list(df.iloc[:,origin_disclosur_index_pos[0]])



            for (asset_or_project_nam,start_time,end_time,forecast_perform,actual_result, \
                       unpredict_reason,origin_disclosur_date,origin_disclosur_index) \
                in zip(asset_or_project_nams,start_times,end_times,forecast_performs,actual_results, \
                       unpredict_reasons,origin_disclosur_dates,origin_disclosur_indexs ):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    asset_or_project_nam=asset_or_project_nam,
                    start_time=start_time,
                    end_time=end_time,
                    forecast_perform=num_to_decimal(forecast_perform, forecast_perform_unit),
                    actual_result=num_to_decimal(actual_result, actual_result_unit),
                    unpredict_reason=unpredict_reason,
                    origin_disclosur_date=origin_disclosur_date,
                    origin_disclosur_index=origin_disclosur_index,
                )
                create_and_update('ProfitPredict',**value_dict)
        else:
            pass
        save_instructi(instructi, models.ImportMatter, self.stk_cd_id, self.acc_per, 'profit_predict')

class AppointAndDismissOfAccountFirm(HandleIndexContent):
    '''
       解聘、续聘会计师事务所情况
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AppointAndDismissOfAccountFirm, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0506000000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:, 0].str.contains('境内会计师事务所名称').any():
                                    df = remove_space_from_df(table)
                                    dfs['first'] = df
                                elif table.iloc[:, 0].str.contains('内部控制审计会计师事务所').any():
                                    df = remove_space_from_df(table)
                                    dfs['second'] = df
                                else:
                                    pass
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.适用.不适用', '', item)
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
        if dfs.get('first') is not None and dfs.get('second') is not None:
            df_first = dfs['first']
            value_pos = list(np.where((df_first.iloc[0, :].str.contains('现聘任')))[0])
            name_pos = list(np.where((df_first.iloc[:, 0].str.contains('境内会计师事务所名称')))[0])
            remuner_pos = list(np.where((df_first.iloc[:, 0].str.contains('境内会计师事务所报酬')))[0])
            audit_period_pos = list(np.where((df_first.iloc[:, 0].str.contains('境内会计师事务所审计年限')))[0])

            name = df_first.iloc[name_pos[0],value_pos[0]]
            remuner = df_first.iloc[remuner_pos[0],value_pos[0]]
            audit_period = df_first.iloc[audit_period_pos[0],value_pos[0]]

            df_second = dfs['second']
            intern_control_audit_pos = list(np.where((df_second.iloc[:, 0].str.contains('内部控制审计会计师事务所')))[0])
            intern_control_name = df_second.iloc[intern_control_audit_pos[0],1]
            intern_control_remuner = df_second.iloc[intern_control_audit_pos[0],2]

            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                name=name,
                remuner=num_to_decimal(remuner, unit),
                audit_period=audit_period,
                intern_control_name=intern_control_name,
                intern_control_remuner=num_to_decimal(intern_control_remuner, unit),
            )
            create_and_update('AccountFirm',**value_dict)
        else:
            pass
        save_instructi(instructi,models.ImportMatter,self.stk_cd_id,self.acc_per,'account_firm')

class AppointAndDismissOfAccountFirmSZ(HandleIndexContent):
    '''
       解聘、续聘会计师事务所情况
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AppointAndDismissOfAccountFirmSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '万元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['05090000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_per_from_df(remove_space_from_df(item[0][0]))
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.适用.不适用', '', item)
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
        oversea_unit = '万元'
        if df is not None and len(df) > 0:
            pattern0 = re.compile('^.*?境内会计师事务所报酬（(.*?元)）.*?$')
            pattern1 = re.compile('^.*?境外会计师事务所报酬（(.*?元)）.*?$')
            name_pos = list(np.where((df.iloc[:, 0].str.contains('境内会计师事务所名称')))[0])
            remuner_pos = list(np.where((df.iloc[:, 0].str.contains('境内会计师事务所报酬')))[0])
            audit_period_pos = list(np.where((df.iloc[:, 0].str.contains('境内会计师事务所审计服务的连续年限')))[0])
            cpa_name_pos = list(np.where((df.iloc[:, 0].str.contains('境内会计师事务所注册会计师姓名')))[0])
            cpa_period_pos = list(np.where((df.iloc[:, 0].str.contains('境内会计师事务所注册会计师审计服务的连续年限')))[0])
            oversea_name_pos = list(np.where((df.iloc[:, 0].str.contains('境外会计师事务所名称')))[0])
            oversea_remuner_pos = list(np.where((df.iloc[:, 0].str.contains('境外会计师事务所报酬')))[0])
            oversea_audit_period_pos = list(np.where((df.iloc[:, 0].str.contains('境外会计师事务所审计服务的连续年限')))[0])
            oversea_cpa_name_pos = list(np.where((df.iloc[:, 0].str.contains('境外会计师事务所注册会计师姓名')))[0])

            if len(name_pos)>0:
                name = df.iloc[name_pos[0],1]
            else:
                name = ''

            if len(remuner_pos) > 0:
                remuner = df.iloc[remuner_pos[0], 1]
                unit = pattern0.match(df.iloc[remuner_pos[0], 0]).groups()[0]
            else:
                remuner = 0

            if len(audit_period_pos)>0:
                audit_period = df.iloc[audit_period_pos[0], 1]
            else:
                audit_period = ''

            if len(cpa_name_pos)>0:
                cpa_name = df.iloc[cpa_name_pos[0], 1]
            else:
                cpa_name = ''

            if len(cpa_period_pos)>0:
                cpa_period = df.iloc[cpa_period_pos[0], 1]
            else:
                cpa_period = ''

            if len(oversea_name_pos)>0:
                oversea_name = df.iloc[oversea_name_pos[0], 1]
            else:
                oversea_name = ''

            if len(oversea_remuner_pos) > 0:
                oversea_remuner = df.iloc[oversea_remuner_pos[0], 1]
                oversea_unit = pattern1.match(df.iloc[oversea_remuner_pos[0], 0]).groups()[0]
            else:
                oversea_remuner = 0

            if len(oversea_audit_period_pos) > 0:
                oversea_audit_period = df.iloc[oversea_audit_period_pos[0], 1]
            else:
                oversea_audit_period = ''

            if len(oversea_cpa_name_pos) > 0:
                oversea_cpa_name = df.iloc[oversea_cpa_name_pos[0], 1]
            else:
                oversea_cpa_name = ''

            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                name=name,
                remuner=num_to_decimal(remuner, unit),
                audit_period=audit_period,
                cpa_name=cpa_name,
                cpa_period=cpa_period,
                oversea_name=oversea_name,
                oversea_remuner=num_to_decimal(oversea_remuner, oversea_unit),
                oversea_audit_period=oversea_audit_period,
                oversea_cpa_name=oversea_cpa_name
            )
            create_and_update('AccountFirm',**value_dict)
        else:
            pass
        save_instructi(instructi,models.ImportMatter,self.stk_cd_id,self.acc_per,'account_firm')


class RelatTransact(HandleIndexContent):
    '''
       关联交易情况
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RelatTransact, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['050e010200']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            dealer_pos = list(np.where((df.iloc[0, :].str.contains('交易方')))[0])
            relationship_pos = list(np.where((df.iloc[0, :].str.contains('关联关系')))[0])
            transact_type_pos = list(np.where((df.iloc[0, :].str.contains('关联交易类型')))[0])
            transact_content_pos = list(np.where((df.iloc[0, :].str.contains('关联交易内容')))[0])
            price_principl_pos = list(np.where((df.iloc[0, :].str.contains('关联交易定价原则')))[0])
            trade_price_pos = list(np.where((df.iloc[0, :].str.contains('关联交易价格')))[0])
            transact_amount_pos = list(np.where((df.iloc[0, :].str.contains('关联交易金额')))[0])
            proport_of_similar_pos = list(np.where((df.iloc[0, :].str.contains('占同类交易金额的比例')))[0])
            bill_method_pos = list(np.where((df.iloc[0, :].str.contains('关联交易结算方式')))[0])
            market_price_pos = list(np.where((df.iloc[0, :].str.contains('市场价格')|df.iloc[0, :].str.contains('可获得的同类交易市价')))[0])
            price_diff_reason_pos = list(np.where((df.iloc[0, :].str.contains('交易价格与市场参考价格差异较大的原因')))[0])

            total_pos = list(np.where((df.iloc[:, 0].str.contains('合计')))[0])
            big_sale_return_pos = list(np.where((df.iloc[:, 0].str.contains('大额销货退回的详细情况')))[0])
            relat_transact_desc_pos = list(np.where((df.iloc[:, 0].str.contains('关联交易的说明')))[0])

            big_sale_return = df.iloc[big_sale_return_pos[0], 3]
            relat_transact_desc = df.iloc[relat_transact_desc_pos[0], 2]

            df = df.drop([0])

            dealers = list(df.iloc[:total_pos[0],dealer_pos[0]])
            relationships = list(df.iloc[:total_pos[0],relationship_pos[0]])
            transact_types = list(df.iloc[:total_pos[0],transact_type_pos[0]])
            transact_contents = list(df.iloc[:total_pos[0],transact_content_pos[0]])
            price_principls = list(df.iloc[:total_pos[0],price_principl_pos[0]])
            trade_prices = list(df.iloc[:total_pos[0],trade_price_pos[0]])
            transact_amounts = list(df.iloc[:total_pos[0],transact_amount_pos[0]])
            proport_of_similars = list(df.iloc[:total_pos[0],proport_of_similar_pos[0]])
            bill_methods = list(df.iloc[:total_pos[0],bill_method_pos[0]])
            market_prices = list(df.iloc[:total_pos[0],market_price_pos[0]])
            price_diff_reasons = list(df.iloc[:total_pos[0],price_diff_reason_pos[0]])

            for (dealer,relationship,transact_type,transact_content,price_principl,trade_price, \
                       transact_amount,proport_of_similar,bill_method,market_price,price_diff_reason)\
                in zip(dealers,relationships,transact_types,transact_contents,price_principls,trade_prices, \
                       transact_amounts,proport_of_similars,bill_methods,market_prices,price_diff_reasons):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    dealer=dealer,
                    relationship=relationship,
                    transact_type=transact_type,
                    transact_content=transact_content,
                    price_principl=price_principl,
                    trade_price=trade_price,
                    transact_amount=num_to_decimal(transact_amount, unit),
                    proport_of_similar=num_to_decimal(proport_of_similar),
                    bill_method=bill_method,
                    market_price=market_price,
                    price_diff_reason=price_diff_reason,
                )
                create_and_update('RelatTransact',**value_dict)

            save_instructi(big_sale_return,models.ImportMatter,self.stk_cd_id,self.acc_per,'big_sale_return')
            save_instructi(relat_transact_desc, models.ImportMatter, self.stk_cd_id, self.acc_per, 'relat_transact_desc')
        else:
            pass

class AcquisitOrSaleOfAssetOrEquitiPerformAgreement(HandleIndexContent):
    '''
       资产或股权收购、出售发生的关联交易
       涉及业绩约定的，应当披露报告期内的业绩实现情况
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AcquisitOrSaleOfAssetOrEquitiPerformAgreement, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['050e020400']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi,models.ImportMatter,self.stk_cd_id,self.acc_per,'perf_agre_rt')


class OtherRelatTransact(HandleIndexContent):
    '''
       其他重大关联交易
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OtherRelatTransact, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['05100500']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.ImportMatter, self.stk_cd_id, self.acc_per, 'other_relat_trade')

class OtherMajorContract(HandleIndexContent):
    '''
          其他重大合同
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OtherMajorContract, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['05110400']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            compani_parti_name_pos = list(np.where((df.iloc[0, :].str.contains('合同订立公司方名称')))[0])
            other_side_name_pos = list(np.where((df.iloc[0, :].str.contains('合同订立对方名称')))[0])
            subject_pos = list(np.where((df.iloc[0, :].str.contains('合同标的')))[0])
            date_pos = list(np.where((df.iloc[0, :].str.contains('合同签订日期')))[0])
            book_valu_of_asset_pos = list(np.where((df.iloc[0, :].str.contains('合同涉及资产的账面价值')))[0])
            evalu_of_asset_pos = list(np.where((df.iloc[0, :].str.contains('合同涉及资产的评估价值')))[0])
            evalu_agenc_name_pos = list(np.where((df.iloc[0, :].str.contains('评估机构名称')))[0])
            base_date_of_assess_pos = list(np.where((df.iloc[0, :].str.contains('评估基准日')))[0])
            price_principl_pos = list(np.where((df.iloc[0, :].str.contains('定价原则')))[0])
            trade_price_pos = list(np.where((df.iloc[0, :].str.contains('交易价格')))[0])
            is_relat_trade_pos = list(np.where((df.iloc[0, :].str.contains('是否关联交易')))[0])
            relationship_pos = list(np.where((df.iloc[0, :].str.contains('关联关系')))[0])
            progress_pos = list(np.where((df.iloc[0, :].str.contains('截至报告期末的执行情况')))[0])
            date_of_disclosur_pos = list(np.where((df.iloc[0, :].str.contains('披露日期')))[0])
            disclosur_index_pos = list(np.where((df.iloc[0, :].str.contains('披露索引')))[0])

            df = df.drop([0])

            compani_parti_names = list(df.iloc[:, compani_parti_name_pos[0]])
            other_side_names = list(df.iloc[:, other_side_name_pos[0]])
            subjects = list(df.iloc[:, subject_pos[0]])
            dates = list(df.iloc[:, date_pos[0]])
            book_valu_of_assets = list(df.iloc[:, book_valu_of_asset_pos[0]])
            evalu_of_assets = list(df.iloc[:, evalu_of_asset_pos[0]])
            evalu_agenc_names = list(df.iloc[:, evalu_agenc_name_pos[0]])
            base_date_of_assesses = list(df.iloc[:, base_date_of_assess_pos[0]])
            price_principls = list(df.iloc[:, price_principl_pos[0]])
            trade_prices = list(df.iloc[:, trade_price_pos[0]])
            is_relat_trades = list(df.iloc[:, is_relat_trade_pos[0]])
            relationships = list(df.iloc[:, relationship_pos[0]])
            progresses = list(df.iloc[:, progress_pos[0]])
            date_of_disclosurs = list(df.iloc[:, date_of_disclosur_pos[0]])
            disclosur_indexs = list(df.iloc[:, disclosur_index_pos[0]])

            for (compani_parti_name,other_side_name,subject,date,book_valu_of_asset,evalu_of_asset, \
                           evalu_agenc_name,base_date_of_assess,price_principl,trade_price,is_relat_trade, \
                           relationship,progress,date_of_disclosur,disclosur_index) \
                    in zip(compani_parti_names,other_side_names,subjects,dates,book_valu_of_assets,evalu_of_assets, \
                           evalu_agenc_names,base_date_of_assesses,price_principls,trade_prices,is_relat_trades, \
                           relationships,progresses,date_of_disclosurs,disclosur_indexs):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    compani_parti_name=compani_parti_name,
                    other_side_name=other_side_name,
                    subject=subject,
                    date=date,
                    book_valu_of_asset=book_valu_of_asset,
                    evalu_of_asset=evalu_of_asset,
                    evalu_agenc_name=evalu_agenc_name,
                    price_principl=price_principl,
                    trade_price=trade_price,
                    is_relat_trade=is_relat_trade,
                    relationship=relationship,
                    progress=progress,
                    date_of_disclosur=date_of_disclosur,
                    disclosur_index=disclosur_index,
                )
                create_and_update('OtherMajorContract',**value_dict)
        else:
            pass



class DescriptOfOtherMajorIssu(HandleIndexContent):
    '''
           其他重大事项的说明
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DescriptOfOtherMajorIssu, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0510000000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi,models.ImportMatter,self.stk_cd_id,self.acc_per,'other_major_issu')


class SocialResponsWorkSituat(HandleIndexContent):
    '''
           其他重大事项的说明
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(SocialResponsWorkSituat, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos= ['0511020000']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.ImportMatter, self.stk_cd_id, self.acc_per, 'social_respons_work')


class CompaniOutsidOfKeyEmitt(HandleIndexContent):
    '''
           重点排污单位之外的公司
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CompaniOutsidOfKeyEmitt, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0511030200']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.ImportMatter, self.stk_cd_id, self.acc_per, 'outsid_of_key_emitt')

class ExternGuarante(HandleIndexContent):
    '''
              担保情况
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ExternGuarante, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['05110201']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:, 0].str.contains('A').any() and \
                                        (not table.iloc[:, 0].str.contains('B').any()) and\
                                        (not table.iloc[:, 0].str.contains('C').any()):
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['A'] = df
                                elif (not table.iloc[:, 0].str.contains('A').any()) and \
                                        (table.iloc[:, 0].str.contains('B').any()) and\
                                        (not table.iloc[:, 0].str.contains('C').any()):
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['B'] = df
                                elif (not table.iloc[:, 0].str.contains('A').any()) and \
                                        (not table.iloc[:, 0].str.contains('B').any()) and\
                                        (table.iloc[:, 0].str.contains('C').any()):
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['C'] = df
                                elif (table.iloc[:, 0].str.contains('A').any()) and \
                                        (table.iloc[:, 0].str.contains('B').any()) and\
                                        (table.iloc[:, 0].str.contains('C').any()):
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['sum'] = df
                                elif (table.iloc[:, 0].str.contains('D').any()) :
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['analys'] = df
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
        object_classifies = ['A','B','C']
        for object_classify in object_classifies:
            if dfs.get(object_classify) is not None:
                df = dfs[object_classify]
                company_name_pos = list(np.where((df.iloc[0, :].str.contains('担保对象名称')))[0])
                date_of_disclosur_pos = list(np.where((df.iloc[0, :].str.contains('披露日期')))[0])
                amount_pos = list(np.where((df.iloc[0, :]=='担保额度'))[0])
                actual_date_of_occurr_pos = list(np.where((df.iloc[0, :].str.contains('实际发生日期')))[0])
                actual_amount_pos = list(np.where((df.iloc[0, :].str.contains('实际担保金额')))[0])
                type_pos = list(np.where((df.iloc[0, :].str.contains('担保类型')))[0])
                period_pos = list(np.where((df.iloc[0, :].str.contains('担保期')))[0])
                is_complet_pos = list(np.where((df.iloc[0, :].str.contains('是否履行完毕')))[0])
                is_related_pos = list(np.where((df.iloc[0, :].str.contains('是否为关联方担保')))[0])

                end_pos = list(np.where((df.iloc[:,0].str.contains('审批')))[0])
                due_period_pos = list(np.where((df.iloc[:,0].str.contains('期内')|
                                                df.iloc[:,0].str.contains('年内')))[0])
                end_period_pos = list(np.where((df.iloc[:,0].str.contains('期末')|
                                                df.iloc[:, 0].str.contains('年末')))[0])

                approv_amount_due_period = df.iloc[due_period_pos[0],amount_pos[0]]
                actual_amount_due_period = df.iloc[due_period_pos[0],period_pos[0]]
                approv_amount_end_period = df.iloc[end_period_pos[0],amount_pos[0]]
                actual_amount_end_period = df.iloc[end_period_pos[0],period_pos[0]]

                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    object_classify=object_classify,
                    approv_amount_due_period=num_to_decimal(approv_amount_due_period, unit),
                    actual_amount_due_period=num_to_decimal(actual_amount_due_period, unit),
                    approv_amount_end_period=num_to_decimal(approv_amount_end_period, unit),
                    actual_amount_end_period=num_to_decimal(actual_amount_end_period, unit),
                )
                create_and_update('GuaranteAmount',**value_dict)

                company_names = list(df.iloc[1:end_pos[0], company_name_pos[0]])
                date_of_disclosurs = list(df.iloc[1:end_pos[0], date_of_disclosur_pos[0]])
                amounts = list(df.iloc[1:end_pos[0], amount_pos[0]])
                actual_date_of_occurrs = list(df.iloc[1:end_pos[0], actual_date_of_occurr_pos[0]])
                actual_amounts = list(df.iloc[1:end_pos[0], actual_amount_pos[0]])
                types = list(df.iloc[1:end_pos[0], type_pos[0]])
                periods = list(df.iloc[1:end_pos[0], period_pos[0]])
                is_complets = list(df.iloc[1:end_pos[0], is_complet_pos[0]])
                is_relateds = list(df.iloc[1:end_pos[0], is_related_pos[0]])

                for (company_name,date_of_disclosur,amount,actual_date_of_occurr,actual_amount,type,period,
                     is_complet,is_related) in  zip(company_names,date_of_disclosurs,amounts,actual_date_of_occurrs,
                                                    actual_amounts,types,periods,is_complets,is_relateds):
                    if models.CompanyName.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,company_name=company_name):
                        obj_name = models.CompanyName.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,company_name=company_name)
                    else:
                        obj_name = models.CompanyName.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,natur_of_the_unit='g', company_name=company_name)

                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        company_name_id=obj_name.id,
                        object_classify=object_classify,
                        date_of_disclosur=date_of_disclosur,
                        amount=num_to_decimal(amount, unit),
                        type=type,
                        is_complet=is_complet,
                        is_related=is_related,
                    )
                    create_and_update('ExternGuarante',**value_dict)
            else:
                pass

        if dfs.get('sum') is not None:
            df = dfs['sum']

            approv_amount_due_period = df.iloc[0, 1]
            actual_amount_due_period = df.iloc[0, 3]
            approv_amount_end_period = df.iloc[1, 1]
            actual_amount_end_period = df.iloc[1, 3]

            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                object_classify='sum',
                approv_amount_due_period=num_to_decimal(approv_amount_due_period, unit),
                actual_amount_due_period=num_to_decimal(actual_amount_due_period, unit),
                approv_amount_end_period=num_to_decimal(approv_amount_end_period, unit),
                actual_amount_end_period=num_to_decimal(actual_amount_end_period, unit),
            )
            create_and_update('GuaranteAmount',**value_dict)
        else:
            pass

        if dfs.get('analys') is not None:
            df = dfs['analys']
            related_pos = list(np.where((df.iloc[:,0].str.contains('关联方')))[0])
            asset_li_ratio_exce_70_per_pos = list(np.where((df.iloc[:,0].str.contains('资产负债率')))[0])
            more_than_50_per_of_net_asset_pos = list(np.where((df.iloc[:,0].str.contains('净资产')))[0])
            sum_pos = list(np.where((df.iloc[:,0].str.contains('合计')))[0])
            warranti_respons_desc_pos = list(np.where((df.iloc[:,0].str.contains('已发生担保责任或可能承担连带清偿责任的情况说明')))[0])
            non_compli_guarante_pos = list(np.where((df.iloc[:,0].str.contains('违反规定程序对外提供担保的说明')))[0])

            related = df.iloc[related_pos[0],1]
            asset_li_ratio_exce_70_per = df.iloc[asset_li_ratio_exce_70_per_pos[0],1]
            more_than_50_per_of_net_asset = df.iloc[more_than_50_per_of_net_asset_pos[0],1]
            sum = df.iloc[sum_pos[0],1]
            warranti_respons_desc = df.iloc[warranti_respons_desc_pos[0],1] if len(warranti_respons_desc_pos)>0 else ''
            non_compli_guarante = df.iloc[non_compli_guarante_pos[0],1] if len(non_compli_guarante_pos)>0 else ''

            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                related=num_to_decimal(related, unit),
                asset_li_ratio_exce_70_per=num_to_decimal(asset_li_ratio_exce_70_per, unit),
                more_than_50_per_of_net_asset=num_to_decimal(more_than_50_per_of_net_asset, unit),
                sum=num_to_decimal(sum, unit),
                warranti_respons_desc=warranti_respons_desc,
                non_compli_guarante=non_compli_guarante,
            )
            create_and_update('AnalysiOfGuarante',**value_dict)
