# _author : litufu
# date : 2018/4/23

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import re
import numpy as np
from utils.mytools import HandleIndexContent,remove_space_from_df,remove_per_from_df
from report_data_extract import models
from decimal import Decimal
import decimal
from collections import OrderedDict
from itertools import chain
import pandas as pd

class CashDividendPolici(HandleIndexContent):
    '''
               现金分红政策的制定、执行或调整情况
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CashDividendPolici, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0501010000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
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
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.cash_dividend_polici = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    cash_dividend_polici=instructi
                )
        else:
            pass

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
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.posit_profit_no_divi = posit_profit_no_divi
                obj.purpos_of_profit = purpos_of_profit
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    posit_profit_no_divi=posit_profit_no_divi,
                    purpos_of_profit=purpos_of_profit
                )

        if len(instructi) > 0:
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.cash_dividend_polici = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    cash_dividend_polici=instructi
                )
        else:
            pass

class DistributPlan(HandleIndexContent):
    '''
        公司近三年（含报告期）的普通股股利分配方案或预案、资本公积金转增股本方案或预案
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DistributPlan, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0501020000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_per_from_df(remove_space_from_df(item[0][0]))
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
        year = str(self.acc_per.year)
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 0:
            year_pos = list(np.where((df.iloc[:, 0].str.contains(year)))[0])
            number_of_bonu_share_pos = list(np.where((df.iloc[0, :].str.contains('每10股送红股数')))[0])
            number_of_dividend_pos = list(np.where((df.iloc[0, :].str.contains('每10股派息数')))[0])
            transfer_increas_pos = list(np.where((df.iloc[0, :].str.contains('每10股转增数')))[0])
            amount_of_cash_divid_pos = list(np.where((df.iloc[0, :].str.contains('现金分红的数额')))[0])
            common_sharehold_np_pos = list(np.where((df.iloc[0, :].str.contains('合并报表中归属于上市公司普通股股东的净利润')))[0])
            distribut_ratio_pos = list(np.where((df.iloc[0, :].str.contains('占合并报表中归属于上市公司普通股股东的净利润的比率')))[0])
            number_of_bonu_share = Decimal(re.sub(',','',str(df.iloc[year_pos[0],number_of_bonu_share_pos[0]])))
            number_of_dividend =  Decimal(re.sub(',','',str(df.iloc[year_pos[0],number_of_dividend_pos[0]])))
            transfer_increas =  Decimal(re.sub(',','',str(df.iloc[year_pos[0],transfer_increas_pos[0]])))
            amount_of_cash_divid = Decimal(re.sub(',','',str(df.iloc[year_pos[0],amount_of_cash_divid_pos[0]])))*unit_change[unit]
            common_sharehold_np = Decimal(re.sub(',','',str(df.iloc[year_pos[0],common_sharehold_np_pos[0]])))*unit_change[unit]
            distribut_ratio = Decimal(re.sub(',','',str(df.iloc[year_pos[0],distribut_ratio_pos[0]])))


            if models.CashDividendPolici.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.CashDividendPolici.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.number_of_bonu_share = number_of_bonu_share
                obj.number_of_dividend = number_of_dividend
                obj.transfer_increas = transfer_increas
                obj.amount_of_cash_divid = amount_of_cash_divid
                obj.common_sharehold_np = common_sharehold_np
                obj.distribut_ratio = distribut_ratio
                obj.save()
            else:
                models.CashDividendPolici.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    number_of_bonu_share=number_of_bonu_share,
                    number_of_dividend=number_of_dividend,
                    transfer_increas=transfer_increas,
                    amount_of_cash_divid=amount_of_cash_divid,
                    common_sharehold_np=common_sharehold_np,
                    distribut_ratio=distribut_ratio
                )
        else:
            pass

        if len(instructi) > 0:
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.distribute_plan = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    distribute_plan=instructi
                )
        else:
            pass

class DistributPlanSZ(HandleIndexContent):
    '''
        本报告期利润分配及资本公积金转增股本预案
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DistributPlanSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['05020000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_per_from_df(remove_space_from_df(item[0][0]))
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
        year = str(self.acc_per.year)
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 0:
            pattern = re.compile('^.*?现金分红总额（(.*?元)）.*?$')

            number_of_bonu_share_pos = list(np.where((df.iloc[:,0].str.contains('每10股送红股数')))[0])
            number_of_dividend_pos = list(np.where((df.iloc[:,0].str.contains('每10股派息数')))[0])
            transfer_increas_pos = list(np.where((df.iloc[:,0].str.contains('每10股转增数')))[0])
            amount_of_cash_divid_pos = list(np.where((df.iloc[:,0].str.contains('现金分红')))[0])
            distribut_profit_pos = list(np.where((df.iloc[:,0].str.contains('可分配利润')))[0])
            prop_of_distribut_profit_pos = list(np.where((df.iloc[:,0].str.contains('现金分红占利润分配总额的比例')))[0])

            unit = pattern.match(df.iloc[amount_of_cash_divid_pos[0],0]).groups()[0]

            number_of_bonu_share = Decimal(re.sub(',','',str(df.iloc[number_of_bonu_share_pos[0],1])))
            number_of_dividend =  Decimal(re.sub(',','',str(df.iloc[number_of_dividend_pos[0],1])))
            transfer_increas =  Decimal(re.sub(',','',str(df.iloc[transfer_increas_pos[0],1])))
            amount_of_cash_divid = Decimal(re.sub(',','',str(df.iloc[amount_of_cash_divid_pos[0],1])))*unit_change[unit]
            distribut_profit = Decimal(re.sub(',','',str(df.iloc[distribut_profit_pos[0],1])))*unit_change[unit]
            prop_of_distribut_profit = Decimal(re.sub(',','',str(df.iloc[prop_of_distribut_profit_pos[0],1])))


            if models.CashDividendPolici.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.CashDividendPolici.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.number_of_bonu_share = number_of_bonu_share
                obj.number_of_dividend = number_of_dividend
                obj.transfer_increas = transfer_increas
                obj.amount_of_cash_divid = amount_of_cash_divid
                obj.distribut_profit = distribut_profit
                obj.prop_of_distribut_profit = prop_of_distribut_profit
                obj.save()
            else:
                models.CashDividendPolici.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    number_of_bonu_share=number_of_bonu_share,
                    number_of_dividend=number_of_dividend,
                    transfer_increas=transfer_increas,
                    amount_of_cash_divid=amount_of_cash_divid,
                    distribut_profit=distribut_profit,
                    prop_of_distribut_profit=prop_of_distribut_profit
                )
        else:
            pass

        if len(instructi) > 0:
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.distribute_plan = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    distribute_plan=instructi
                )
        else:
            pass

class Commit(HandleIndexContent):
    '''
       公司实际控制人、股东、关联方、收购人以及公司等承诺相关方在报告期内或持续到报告
       期内的承诺事项
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(Commit, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0502010000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_per_from_df(remove_space_from_df(item[0][0]))
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
                if models.Commit.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                background=background,commit_type=commit_type,parti=parti,content=content):
                    obj = models.Commit.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                    background=background, commit_type=commit_type, parti=parti, content=content)
                    obj.background = background
                    obj.commit_type = commit_type
                    obj.parti = parti
                    obj.content = content
                    obj.time_and_deadline = time_and_deadline
                    obj.is_there_deadline = is_there_deadline
                    obj.is_strictli_perform = is_strictli_perform
                    obj.reason_for_incomplet = reason_for_incomplet
                    obj.failur_to_perform = failur_to_perform
                    obj.save()
                else:
                    models.Commit.objects.create(
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
        else:
            pass

        if len(instructi) > 0:
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.commit = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    commit=instructi
                )
        else:
            pass


class CommitSZ(HandleIndexContent):
    '''
       公司实际控制人、股东、关联方、收购人以及公司等承诺相关方在报告期内或持续到报告
       期内的承诺事项
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CommitSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['05030100']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_per_from_df(remove_space_from_df(item[0][0]))
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
            background_pos = list(np.where((df.iloc[0, :].str.contains('承诺事由')))[0])
            type_pos = list(np.where((df.iloc[0, :].str.contains('承诺类型')))[0])
            parti_pos = list(np.where((df.iloc[0, :].str.contains('承诺方')))[0])
            content_pos = list(np.where((df.iloc[0, :].str.contains('承诺内容')))[0])
            time_pos = list(np.where((df.iloc[0, :].str.contains('承诺时间')))[0])
            deadline_pos = list(np.where((df.iloc[0, :].str.contains('承诺期限')))[0])
            perform_pos = list(np.where((df.iloc[0, :].str.contains('履行情况')))[0])

            df = df.drop([0,len(df)-1])

            backgrounds = list(df.iloc[:, background_pos[0]])
            types = list(df.iloc[:, type_pos[0]])
            partis = list(df.iloc[:, parti_pos[0]])
            contents = list(df.iloc[:, content_pos[0]])
            times = list(df.iloc[:, time_pos[0]])
            deadlines = list(df.iloc[:, deadline_pos[0]])
            performs = list(df.iloc[:, perform_pos[0]])

            for (background, commit_type, parti, content,time,deadline,perform ) \
                    in zip(backgrounds, types, partis, contents,times,deadlines,performs):
                if models.Commit.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                background=background, commit_type=commit_type, parti=parti, content=content):
                    obj = models.Commit.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                    background=background, commit_type=commit_type, parti=parti, content=content)
                    obj.background = background
                    obj.commit_type = commit_type
                    obj.parti = parti
                    obj.content = content
                    obj.time = time
                    obj.deadline = deadline
                    obj.perform = perform
                    obj.save()
                else:
                    models.Commit.objects.create(
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
        else:
            pass

        if len(instructi) > 0:
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.commit = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    commit=instructi
                )
        else:
            pass

class ProfitPredict(HandleIndexContent):
    '''
       业绩预测
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ProfitPredict, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0502020000','05030200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_per_from_df(remove_space_from_df(item[0][0]))
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
                if models.ProfitPredict.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                asset_or_project_nam=asset_or_project_nam):
                    obj = models.ProfitPredict.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                    asset_or_project_nam=asset_or_project_nam)
                    obj.asset_or_project_nam = asset_or_project_nam
                    obj.start_time = start_time
                    obj.end_time = end_time
                    obj.forecast_perform = Decimal(re.sub(',','',str(forecast_perform)))*unit_change[forecast_perform_unit]
                    obj.actual_result = Decimal(re.sub(',','',str(actual_result)))*unit_change[actual_result_unit]
                    obj.unpredict_reason = unpredict_reason
                    obj.origin_disclosur_date = origin_disclosur_date
                    obj.origin_disclosur_index = origin_disclosur_index
                    obj.save()
                else:
                    models.ProfitPredict.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        asset_or_project_nam=asset_or_project_nam,
                        start_time=start_time,
                        end_time=end_time,
                        forecast_perform=Decimal(re.sub(',','',str(forecast_perform)))*unit_change[forecast_perform_unit],
                        actual_result=Decimal(re.sub(',','',str(actual_result)))*unit_change[actual_result_unit],
                        unpredict_reason=unpredict_reason,
                        origin_disclosur_date=origin_disclosur_date,
                        origin_disclosur_index=origin_disclosur_index,
                    )
        else:
            pass

        if len(instructi) > 0:
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.profit_predict = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    profit_predict=instructi
                )
        else:
            pass

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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
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

            if models.AccountFirm.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.AccountFirm.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,)
                obj.name = name
                obj.remuner = Decimal(re.sub(',','',str(remuner)))*unit_change[unit]
                obj.audit_period = audit_period
                obj.intern_control_name = intern_control_name
                obj.intern_control_remuner = Decimal(re.sub(',','',str(intern_control_remuner)))*unit_change[unit]
                obj.save()
            else:
                models.AccountFirm.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    name=name,
                    remuner=Decimal(re.sub(',','',str(remuner)))*unit_change[unit],
                    audit_period=audit_period,
                    intern_control_name=intern_control_name,
                    intern_control_remuner=Decimal(re.sub(',','',str(intern_control_remuner)))*unit_change[unit],
                )
        else:
            pass

        if len(instructi) > 0:
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.account_firm = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    account_firm=instructi
                )
        else:
            pass

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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
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


            if models.AccountFirm.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.AccountFirm.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,)
                obj.name = name
                obj.remuner = Decimal(re.sub(',','',str(remuner)))*unit_change[unit]
                obj.audit_period = audit_period
                obj.cpa_name = cpa_name
                obj.cpa_period = cpa_period
                obj.oversea_name = oversea_name
                obj.oversea_remuner = Decimal(re.sub(',','',str(oversea_remuner)))*unit_change[oversea_unit]
                obj.oversea_audit_period = oversea_audit_period
                obj.oversea_cpa_name = oversea_cpa_name
                obj.save()
            else:
                models.AccountFirm.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    name=name,
                    remuner=Decimal(re.sub(',','',str(remuner)))*unit_change[unit],
                    audit_period=audit_period,
                    cpa_name=cpa_name,
                    cpa_period=cpa_period,
                    oversea_name=oversea_name,
                    oversea_remuner=Decimal(re.sub(',','',str(oversea_remuner)))*unit_change[oversea_unit],
                    oversea_audit_period=oversea_audit_period,
                    oversea_cpa_name=oversea_cpa_name
                )
        else:
            pass

        if len(instructi) > 0:
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.account_firm = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    account_firm=instructi
                )
        else:
            pass

class RelatTransact(HandleIndexContent):
    '''
       关联交易情况
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RelatTransact, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['050e010200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_per_from_df(remove_space_from_df(item[0][0]))
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
                if models.RelatTransact.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                     dealer=dealer,transact_type=transact_type,transact_content=transact_content):
                    obj = models.RelatTransact.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                         dealer=dealer, transact_type=transact_type,
                                                         transact_content=transact_content)
                    obj.dealer = dealer
                    obj.relationship = relationship
                    obj.transact_type = transact_type
                    obj.transact_content = transact_content
                    obj.price_principl = price_principl
                    obj.trade_price = trade_price
                    obj.transact_amount = Decimal(re.sub(',','',str(transact_amount)))*unit_change[unit]
                    obj.proport_of_similar = Decimal(re.sub(',','',str(proport_of_similar)))
                    obj.bill_method = bill_method
                    obj.market_price = market_price
                    obj.price_diff_reason = price_diff_reason
                    obj.save()
                else:
                    models.RelatTransact.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        dealer=dealer,
                        relationship=relationship,
                        transact_type=transact_type,
                        transact_content=transact_content,
                        price_principl=price_principl,
                        trade_price=trade_price,
                        transact_amount=Decimal(re.sub(',','',str(transact_amount)))*unit_change[unit],
                        proport_of_similar=Decimal(re.sub(',','',str(proport_of_similar))),
                        bill_method=bill_method,
                        market_price=market_price,
                        price_diff_reason=price_diff_reason,
                    )

            if len(big_sale_return) > 0:
                if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                    obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                    obj.big_sale_return = big_sale_return
                    obj.save()
                else:
                    models.ImportMatter.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        big_sale_return=big_sale_return
                    )
            else:
                pass

            if len(relat_transact_desc) > 0:
                if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                    obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                    obj.relat_transact_desc = relat_transact_desc
                    obj.save()
                else:
                    models.ImportMatter.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        relat_transact_desc=relat_transact_desc
                    )
            else:
                pass
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
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['050e020400']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
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
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.perf_agre_rt = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    perf_agre_rt=instructi
                )
        else:
            pass

class OtherRelatTransact(HandleIndexContent):
    '''
       其他重大关联交易
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OtherRelatTransact, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['05100500']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_space_from_df(item[0][0])
                        content = df.to_string()
                        instructi.append(content)
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
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.other_relat_trade = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    other_relat_trade=instructi
                )
        else:
            pass

class OtherMajorContract(HandleIndexContent):
    '''
          其他重大合同
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OtherMajorContract, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['05110400']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_per_from_df(remove_space_from_df(item[0][0]))
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
            compani_parti_name_pos = list(np.where((df.iloc[0, :].str.contains('合同订立公司方名称')))[0])
            other_side_name_pos = list(np.where((df.iloc[0, :].str.contains('合同订立对方名称')))[0])
            subject_pos = list(np.where((df.iloc[0, :].str.contains('合同标的')))[0])
            date_pos = list(np.where((df.iloc[0, :].str.contains('合同签订日期')))[0])
            book_valu_of_asset_pos = list(np.where((df.iloc[0, :].str.contains('合同涉及资产的账面价值')))[0])
            evalu_of_asset_pos = list(np.where((df.iloc[0, :].str.contains('合同涉及资产的评估价值')))[0])
            evalu_agenc_name_pos = list(np.where((df.iloc[0, :].str.contains('评估机构名称')))[0])
            base_date_of_assess_pos = list(np.where((df.iloc[0, :].str.contains('评估基准日')))[0])
            price_principl_pos = list(np.where((df.iloc[0, :].str.contains('定价原则')))[0])
            price_pos = list(np.where((df.iloc[0, :].str.contains('交易价格')))[0])
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
            prices = list(df.iloc[:, price_pos[0]])
            is_relat_trades = list(df.iloc[:, is_relat_trade_pos[0]])
            relationships = list(df.iloc[:, relationship_pos[0]])
            progresses = list(df.iloc[:, progress_pos[0]])
            date_of_disclosurs = list(df.iloc[:, date_of_disclosur_pos[0]])
            disclosur_indexs = list(df.iloc[:, disclosur_index_pos[0]])

            for (compani_parti_name,other_side_name,subject,date,book_valu_of_asset,evalu_of_asset, \
                           evalu_agenc_name,base_date_of_assess,price_principl,price,is_relat_trade, \
                           relationship,progress,date_of_disclosur,disclosur_index) \
                    in zip(compani_parti_names,other_side_names,subjects,dates,book_valu_of_assets,evalu_of_assets, \
                           evalu_agenc_names,base_date_of_assesses,price_principls,prices,is_relat_trades, \
                           relationships,progresses,date_of_disclosurs,disclosur_indexs):
                if models.OtherMajorContract.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                    compani_parti_name=compani_parti_name, other_side_name=other_side_name, subject=subject):
                    obj = models.OtherMajorContract.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                compani_parti_name=compani_parti_name,other_side_name=other_side_name, subject=subject)
                    obj.compani_parti_name = compani_parti_name
                    obj.other_side_name = other_side_name
                    obj.subject = subject
                    obj.date = date
                    obj.book_valu_of_asset = book_valu_of_asset
                    obj.evalu_of_asset = evalu_of_asset
                    obj.evalu_agenc_name = evalu_agenc_name
                    obj.base_date_of_assess = base_date_of_assess
                    obj.price_principl = price_principl
                    obj.price = price
                    obj.is_relat_trade = is_relat_trade
                    obj.relationship = relationship
                    obj.progress = progress
                    obj.date_of_disclosur = date_of_disclosur
                    obj.disclosur_index = disclosur_index
                    obj.save()
                else:
                    models.OtherMajorContract.objects.create(
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
                        price=price,
                        is_relat_trade=is_relat_trade,
                        relationship=relationship,
                        progress=progress,
                        date_of_disclosur=date_of_disclosur,
                        disclosur_index=disclosur_index,
                    )
        else:
            pass



class DescriptOfOtherMajorIssu(HandleIndexContent):
    '''
           其他重大事项的说明
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DescriptOfOtherMajorIssu, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0510000000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
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
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.other_major_issu = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    other_major_issu=instructi
                )
        else:
            pass

class SocialResponsWorkSituat(HandleIndexContent):
    '''
           其他重大事项的说明
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(SocialResponsWorkSituat, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0511020000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_space_from_df(item[0][0])
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
        if len(instructi) > 0:
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.social_respons_work = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    social_respons_work=instructi
                )
        else:
            pass

class CompaniOutsidOfKeyEmitt(HandleIndexContent):
    '''
           重点排污单位之外的公司
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CompaniOutsidOfKeyEmitt, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0511030200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
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
            if models.ImportMatter.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.ImportMatter.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.outsid_of_key_emitt = instructi
                obj.save()
            else:
                models.ImportMatter.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    outsid_of_key_emitt=instructi
                )
        else:
            pass