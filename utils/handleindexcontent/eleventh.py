# _author : litufu
# date : 2018/5/1

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

class AuditReport(HandleIndexContent):
    '''
            审计报告
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AuditReport, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = []
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b01000000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_per_from_df(remove_space_from_df(table))
                                dfs.append(df)
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

        return dfs, unit, ''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs, unit, instructi = self.recognize()
        instructi = re.sub('\s+','',instructi)
        opinions = []
        patt1 = re.compile('.*?财务报表在所有重大方面按照企业会计准则的规定编制，公允反映了.*?')
        patt2 = re.compile('^.*?(....年.{1,2}月.{1,3}日)$')
        patt3 = re.compile('.*?审计报告(.*?号).*?')
        if '保留意见我们审计了' in instructi:
            temp_pattern1 = re.compile('.*?形成保留意见的基础(.*?)我们按照中国注册会计师审计准则的规定执行了审计工作.*?')
            if temp_pattern1.match(instructi):
                opinions.append(temp_pattern1.match(instructi).groups()[0])
            type_of_opinion = '保留意见'
        elif '否定意见' in instructi:
            temp_pattern1 = re.compile('.*?形成否定意见的基础(.*?)我们按照中国注册会计师审计准则的规定执行了审计工作.*?')
            if temp_pattern1.match(instructi):
                opinions.append(temp_pattern1.match(instructi).groups()[0])
            type_of_opinion = '否定意见'
        elif '无法表示意见' in instructi:
            type_of_opinion = '无法表示意见'
        elif '强调事项' in instructi:
            temp_pattern1 = re.compile('.*?强调事项(.*?)。.*?不影响已发表的审计意见.*?')
            if temp_pattern1.match(instructi):
                opinions.append(temp_pattern1.match(instructi).groups()[0])
            type_of_opinion = '带强调事项段的无保留意见'
        elif '与持续经营相关的重大不确定性' in instructi:
            temp_pattern1 = re.compile('.*?与持续经营相关的重大不确定性(.*?)。.*?不影响已发表的审计意见.*?')
            if temp_pattern1.match(instructi):
                opinions.append(temp_pattern1.match(instructi).groups()[0])
            type_of_opinion = '带强调事项段的无保留意见'
        elif '审计意见' in instructi:
            type_of_opinion = '标准的无保留意见'
        else:
            raise Exception
        opinion = ''.join(opinions)
        if len(patt2.match(instructi).groups())==1:
            date = patt2.match(instructi).groups()[0]
        else:
            raise Exception

        if len(patt3.match(instructi).groups())==1:
            report_num = patt3.match(instructi).groups()[0]
        else:
            raise Exception

        if models.AuditReport.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                             report_num=report_num):
            obj = models.AuditReport.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                 report_num=report_num)
            obj.type_of_opinion = type_of_opinion
            obj.date = date
            obj.report_num = report_num
            obj.full_text = instructi
            obj.opinion = opinion
            obj.save()
        else:
            models.AuditReport.objects.create(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                type_of_opinion=type_of_opinion,
                date=date,
                report_num=report_num,
                full_text=instructi,
                opinion=opinion,
            )

        pattern0 = re.compile('.*?我们将(.*?)(识别为)?(作为)?(确认为)?(确定为)?(是)?关键审计事项.*?')
        pattern1 = re.compile('(.*?)是.*?该事项是关键审计事项.*?')
        pattern3 = re.compile('.*?公司的')

        if len(dfs)>0:
            matter_descripts = []
            audit_responses = []
            titles = []
            matter_descript = ''
            audit_respons = ''
            for df in dfs:
                if len(df)==1:
                    if df.iloc[0,0] == '关键审计事项':
                        continue
                    else:
                        matter_descript = df.iloc[0,0]
                        audit_respons = df.iloc[0,1]
                elif len(df)>1:
                    matter_descript = ''.join(list(df.iloc[:,0]))
                    audit_respons = ''.join(list(df.iloc[:,1]))
                else:
                    raise Exception
                desc = matter_descript

                if pattern0.match(desc):
                    title = re.sub(pattern3,'', pattern0.match(desc).groups()[0])
                elif pattern1.match(desc):
                    title = re.sub(pattern3,'', pattern1.match(desc).groups()[0])
                else:
                    print('未找到标题')
                    raise Exception
                matter_descripts.append(matter_descript)
                audit_responses.append(audit_respons)
                titles.append(title)

            obj = models.AuditReport.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,report_num=report_num)
            for (title, matter_descript, audit_respons) \
                    in zip(titles, matter_descripts, audit_responses):
                if models.KeySegment.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                         audit_report_id=obj.id,title=title):
                    obj = models.KeySegment.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                             audit_report_id=obj.id, title=title)
                    obj.matter_descript = matter_descript
                    obj.audit_respons = audit_respons
                    obj.save()
                else:
                    models.KeySegment.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        audit_report_id=obj.id,
                        title=title,
                        matter_descript=matter_descript,
                        audit_respons=audit_respons,
                    )
        else:
            pattern4 = re.compile('.*?关键审计事项(.*?)[四五六七]、其他信息.*?')
            key_seg_desc = pattern4.match(instructi).groups()[0]
            key_segs = re.split(r'(事项描述|审计应对)', key_seg_desc)
            ret = []
            for i in range(len(key_segs)):
                if key_segs[i] == '事项描述' and i + 3 < len(key_segs):
                    ret.append((key_segs[i + 1], key_segs[i + 3]))

            if len(ret) > 0:
                obj = models.AuditReport.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                     report_num=report_num)
                for matter_descript, audit_respons in ret:
                    if pattern0.match(matter_descript):
                        title = re.sub(pattern3, '', pattern0.match(matter_descript).groups()[0])
                    elif pattern1.match(matter_descript):
                        title = re.sub(pattern3, '', pattern1.match(matter_descript).groups()[0])
                    else:
                        print('未找到标题')
                        raise Exception

                    if models.KeySegment.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                        audit_report_id=obj.id, title=title):
                        obj = models.KeySegment.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                            audit_report_id=obj.id, title=title)
                        obj.matter_descript = matter_descript
                        obj.audit_respons = audit_respons
                        obj.save()
                    else:
                        models.KeySegment.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            audit_report_id=obj.id,
                            title=title,
                            matter_descript=matter_descript,
                            audit_respons=audit_respons,
                        )

class AuditReportSZ(HandleIndexContent):
    '''
            审计报告
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AuditReportSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = []
        audit_df = None
        instructi = []
        if self.indexno in ['0b010000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:, 0].str.contains('审计意见类型').any():
                                    audit_df = remove_per_from_df(remove_space_from_df(table))
                                else:
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs.append(df)
                                    instructi.append(df.to_string())
                    elif classify == 't' and len(item) > 0:
                        ret = re.sub('.*?.适用.不适用', '', item)
                        if ret != '':
                            instructi.append(ret)
                    else:
                        pass
        else:
            pass

        return dfs,  ''.join(instructi),audit_df

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs,  instructi,audit_df = self.recognize()
        instructi = re.sub('\s+','',instructi)
        opinions = []
        patt2 = re.compile('^.*?(....年.{1,2}月.{1,3}日)$')
        patt3 = re.compile('.*?审计报告(.*?号).*?')
        if '保留意见我们审计了' in instructi:
            temp_pattern1 = re.compile('.*?形成保留意见的基础(.*?)我们按照中国注册会计师审计准则的规定执行了审计工作.*?')
            if temp_pattern1.match(instructi):
                opinions.append(temp_pattern1.match(instructi).groups()[0])
            type_of_opinion = '保留意见'
        elif '否定意见' in instructi:
            temp_pattern1 = re.compile('.*?形成否定意见的基础(.*?)我们按照中国注册会计师审计准则的规定执行了审计工作.*?')
            if temp_pattern1.match(instructi):
                opinions.append(temp_pattern1.match(instructi).groups()[0])
            type_of_opinion = '否定意见'
        elif '无法表示意见' in instructi:
            type_of_opinion = '无法表示意见'
        elif '强调事项' in instructi:
            temp_pattern1 = re.compile('.*?强调事项(.*?)。.*?不影响已发表的审计意见.*?')
            if temp_pattern1.match(instructi):
                opinions.append(temp_pattern1.match(instructi).groups()[0])
            type_of_opinion = '带强调事项段的无保留意见'
        elif '与持续经营相关的重大不确定性' in instructi:
            temp_pattern1 = re.compile('.*?与持续经营相关的重大不确定性(.*?)。.*?不影响已发表的审计意见.*?')
            if temp_pattern1.match(instructi):
                opinions.append(temp_pattern1.match(instructi).groups()[0])
            type_of_opinion = '带强调事项段的无保留意见'
        elif '审计意见' in instructi:
            type_of_opinion = '标准的无保留意见'
        else:
            raise Exception
        opinion = ''.join(opinions)
        if len(patt2.match(instructi).groups())==1:
            date = patt2.match(instructi).groups()[0]
        else:
            raise Exception

        if len(patt3.match(instructi).groups())==1:
            report_num = patt3.match(instructi).groups()[0]
        else:
            raise Exception

        if models.AuditReport.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                             report_num=report_num):
            obj = models.AuditReport.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                 report_num=report_num)
            obj.type_of_opinion = type_of_opinion
            obj.date = date
            obj.report_num = report_num
            obj.full_text = instructi
            obj.opinion = opinion
            obj.save()
        else:
            models.AuditReport.objects.create(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                type_of_opinion=type_of_opinion,
                date=date,
                report_num=report_num,
                full_text=instructi,
                opinion=opinion,
            )

        pattern0 = re.compile('.*?我们将(.*?)(识别为)?(作为)?(确认为)?(确定为)?(是)?关键审计事项.*?')
        pattern1 = re.compile('(.*?)是.*?该事项是关键审计事项.*?')
        pattern3 = re.compile('.*?公司的')

        if len(dfs)>0:
            matter_descripts = []
            audit_responses = []
            titles = []
            for df in dfs:
                if len(df)==1:
                    if df.iloc[0,0] == '关键审计事项':
                        continue
                    else:
                        matter_descript = df.iloc[0,0]
                        audit_respons = df.iloc[0,1]
                elif len(df)>1:
                    if df.iloc[0,0] == '关键审计事项':
                        matter_descript = ''.join(list(df.iloc[1:,0]))
                        audit_respons =''.join(list(df.iloc[1:,1]))
                    else:
                        matter_descript = ''.join(list(df.iloc[:, 0]))
                        audit_respons = ''.join(list(df.iloc[:, 1]))
                else:
                    raise Exception
                desc = matter_descript

                if pattern0.match(desc):
                    title = re.sub(pattern3,'', pattern0.match(desc).groups()[0])
                elif pattern1.match(desc):
                    title = re.sub(pattern3,'', pattern1.match(desc).groups()[0])
                else:
                    print('未找到标题')
                    raise Exception
                matter_descripts.append(matter_descript)
                audit_responses.append(audit_respons)
                titles.append(title)

            obj = models.AuditReport.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,report_num=report_num)
            for (title, matter_descript, audit_respons) \
                    in zip(titles, matter_descripts, audit_responses):
                if models.KeySegment.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                         audit_report_id=obj.id,title=title):
                    obj = models.KeySegment.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                             audit_report_id=obj.id, title=title)
                    obj.matter_descript = matter_descript
                    obj.audit_respons = audit_respons
                    obj.save()
                else:
                    models.KeySegment.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        audit_report_id=obj.id,
                        title=title,
                        matter_descript=matter_descript,
                        audit_respons=audit_respons,
                    )
        else:
            pattern4 = re.compile('.*?关键审计事项(.*?)[四五六七]、其他信息.*?')
            key_seg_desc = pattern4.match(instructi).groups()[0]
            key_segs = re.split(r'(事项描述|审计应对)', key_seg_desc)
            ret = []
            for i in range(len(key_segs)):
                if key_segs[i] == '事项描述' and i + 3 < len(key_segs):
                    ret.append((key_segs[i + 1], key_segs[i + 3]))

            if len(ret) > 0:
                obj = models.AuditReport.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                     report_num=report_num)
                for matter_descript, audit_respons in ret:
                    if pattern0.match(matter_descript):
                        title = re.sub(pattern3, '', pattern0.match(matter_descript).groups()[0])
                    elif pattern1.match(matter_descript):
                        title = re.sub(pattern3, '', pattern1.match(matter_descript).groups()[0])
                    else:
                        print('未找到标题')
                        raise Exception

                    if models.KeySegment.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                        audit_report_id=obj.id, title=title):
                        obj = models.KeySegment.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                            audit_report_id=obj.id, title=title)
                        obj.matter_descript = matter_descript
                        obj.audit_respons = audit_respons
                        obj.save()
                    else:
                        models.KeySegment.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            audit_report_id=obj.id,
                            title=title,
                            matter_descript=matter_descript,
                            audit_respons=audit_respons,
                        )

class FS(HandleIndexContent):
    '''
   财务报表
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(FS, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?公司单位：(.*?元).*?$')
        pattern1= re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b02000000','0b020100','0b020200','0b020300','0b020400','0b020500','0b020600']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:, 0].str.contains('少数股东权益').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['c_bs'] = df
                                elif table.iloc[:, 0].str.contains('权益合计').any() and (not table.iloc[0, :].str.contains('少数股东权益').any()):
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['s_bs'] = df
                                elif table.iloc[:, 0].str.contains('归属于母公司').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['c_ps'] = df
                                elif table.iloc[:, 0].str.contains('净利润').any() and (not table.iloc[0, :].str.contains('归属于母公司').any()):
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['s_ps'] = df
                                elif table.iloc[:, 0].str.contains('子公司吸收少数股东投资收到的现金').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['c_cfs'] = df
                                elif table.iloc[:, 0].str.contains('现金流量').any() and (not table.iloc[0, :].str.contains('子公司吸收少数股东投资收到的现金').any()):
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['s_cfs'] = df
                                else:
                                    pass

                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        elif pattern1.match(item):
                            unit = pattern1.match(item).groups()[0]
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
        std_set = {
            'c_bs':['zcfzbpp.json','A',models.BalanceSheet],
            's_bs':['zcfzbpp.json','B',models.BalanceSheet],
            'c_ps':['lrbpp.json','A',models.IncomeStatement],
            's_ps':['lrbpp.json','B',models.IncomeStatement],
            'c_cfs':['xjllbpp.json','A',models.CashFlow],
            's_cfs':['xjllbpp.json','B',models.CashFlow],

        }
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        dfs, unit, instructi = self.recognize()
        for item in std_set:
            if dfs.get(item) is not None:
                df = dfs[item]
                pp_df = manage_config.read_config(std_set[item][0])
                pp_df_dict = dict(zip(list(pp_df.item),list(pp_df.field)))
                subject_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
                begin_pos = list(np.where(df.iloc[0, :].str.contains('期初')|df.iloc[0, :].str.contains('年初')
                                          | df.iloc[0, :].str.contains('上期')| df.iloc[0, :].str.contains('上年'))[0])

                end_pos = list(np.where(df.iloc[0, :].str.contains('期末')|df.iloc[0, :].str.contains('年末')
                                        | df.iloc[0, :].str.contains('本期') | df.iloc[0, :].str.contains('本年') )[0])
                begins = {}
                ends = {}
                for i in range(1,len(df)):
                    subject = df.iloc[i, subject_pos[0]]
                    if subject in pp_df_dict:
                        begin = Decimal(re.sub(',', '', str(df.iloc[i, begin_pos[0]]))) * unit_change[unit] \
                            if is_num(df.iloc[i, begin_pos[0]]) else 0.00
                        end = Decimal(re.sub(',', '', str(df.iloc[i, end_pos[0]]))) * unit_change[unit] \
                            if is_num(df.iloc[i, end_pos[0]]) else 0.00
                        field = pp_df_dict[subject]
                        begins[field] = begin
                        ends[field] = end
                    else:
                        patt1 = re.compile('^.*?[：\.、\)）](.*?)$')
                        patt2 = re.compile('^(.*?)[\(（].*?$')
                        if patt1.match(subject) and patt1.match(subject).groups()[0] != '':
                            temp = patt1.match(subject).groups()[0]
                            if patt2.match(temp):
                                new_subject = patt2.match(temp).groups()[0]
                            else:
                                new_subject = temp

                            if new_subject in pp_df_dict:
                                begin = Decimal(re.sub(',', '', str(df.iloc[i, begin_pos[0]]))) * unit_change[unit] \
                                    if is_num(df.iloc[i, begin_pos[0]]) else 0.00
                                end = Decimal(re.sub(',', '', str(df.iloc[i, end_pos[0]]))) * unit_change[unit] \
                                    if is_num(df.iloc[i, end_pos[0]]) else 0.00
                                field = pp_df_dict[new_subject]
                                begins[field] = begin
                                ends[field] = end
                            else:
                                print('{}科目没有在配置表中'.format(subject))
                        elif patt2.match(subject) and patt2.match(subject).groups()[0] != '':
                            new_subject = patt2.match(subject).groups()[0]
                            if new_subject in pp_df_dict:
                                begin = Decimal(re.sub(',', '', str(df.iloc[i, begin_pos[0]]))) * unit_change[unit] \
                                    if is_num(df.iloc[i, begin_pos[0]]) else 0.00
                                end = Decimal(re.sub(',', '', str(df.iloc[i, end_pos[0]]))) * unit_change[unit] \
                                    if is_num(df.iloc[i, end_pos[0]])  else 0.00
                                field = pp_df_dict[new_subject]
                                begins[field] = begin
                                ends[field] = end
                            else:
                                print('{}科目没有在配置表中'.format(subject))
                        else:
                            print('{}科目没有在配置表中'.format(subject))

                if std_set[item][2].objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                      typ_rep_id=std_set[item][1], before_end='before'):
                    obj = std_set[item][2].objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                          typ_rep_id=std_set[item][1], before_end='before')
                    for field in begins:
                        begin = begins[field]
                        setattr(obj, field, begin)
                    obj.save()
                else:
                    obj = std_set[item][2].objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                             typ_rep_id=std_set[item][1], before_end='before')
                    for field in begins:
                        begin = begins[field]
                        setattr(obj, field, begin)
                    obj.save()

                obj_begin = std_set[item][2].objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                      typ_rep_id=std_set[item][1], before_end='before')
                if obj_begin.check_logic():
                    pass
                else:
                    print('报表错误{}'.format(item))
                    raise Exception

                if std_set[item][2].objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                      typ_rep_id=std_set[item][1], before_end='end'):
                    obj = std_set[item][2].objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                          typ_rep_id=std_set[item][1], before_end='end')
                    for field in ends:
                        end = ends[field]
                        setattr(obj, field, end)
                    obj.save()
                else:
                    obj = std_set[item][2].objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                             typ_rep_id=std_set[item][1], before_end='end')
                    for field in ends:
                        end = ends[field]
                        setattr(obj, field, end)
                    obj.save()

                obj_end = std_set[item][2].objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                      typ_rep_id=std_set[item][1], before_end='end')
                if obj_end.check_logic():
                    pass
                else:
                    print('报表错误{}'.format(item))
                    raise Exception

class CompaniOverview(HandleIndexContent):
    '''
        公司概况
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CompaniOverview, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b03010000','0b030000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            if models.CompaniBasicSituat.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.CompaniBasicSituat.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.compani_overview = instructi
                obj.save()
            else:
                models.CompaniBasicSituat.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    compani_overview=instructi
                )
        else:
            pass

class ScopeOfMerger(HandleIndexContent):
    '''
            合并范围
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ScopeOfMerger, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b03020000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            if models.CompaniBasicSituat.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.CompaniBasicSituat.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.scope_of_merger = instructi
                obj.save()
            else:
                models.CompaniBasicSituat.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    scope_of_merger=instructi
                )
        else:
            pass

class SignificAmount(HandleIndexContent):
    '''
        单项金额重大并单独计提坏账准备的应收款项
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(SignificAmount, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b050b0100','0b050b01']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            signific_amount_judgement = df.iloc[0,1]
            signific_amount_withdraw =  df.iloc[1,1]
            if models.CompaniBasicSituat.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.CompaniBasicSituat.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per)
                obj.signific_amount_judgement = signific_amount_judgement
                obj.signific_amount_withdraw = signific_amount_withdraw
                obj.save()
            else:
                models.CompaniBasicSituat.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    signific_amount_judgement=signific_amount_judgement,
                    signific_amount_withdraw=signific_amount_withdraw
                )
        else:
            pass

class AgeAnalysi(HandleIndexContent):
    '''
        账龄分析法
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AgeAnalysi, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b050b0200','0b050b02']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:,0].str.contains('账龄').any() and table.iloc[:,0].str.contains('年').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['age'] = df
                                elif (not table.iloc[:,0].str.contains('账龄').any()) and table.iloc[:,0].str.contains('年').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['age1'] = df
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
        patt_m1 = re.compile('^.*?(\d+).*?月.*?以.*?$')
        patt_m2 = re.compile('^.*?(\d+).*?(\d+).*?月.*?$')
        patt_m3 = re.compile('^.*?(\d+).*?月.*?1年.*?$')
        patt_y0 = re.compile('^.*?1年以内.*?$')
        patt_y1 = re.compile('^.*?(\d+).*?年.*?以上.*?$')
        patt_y2 = re.compile('^.*?(\d+).*?(\d+).*?年.*?$')
        std_dict = {
            '1月':'one_month',
            '2月':'two_month',
            '3月':'three_month',
            '4月':'four_month',
            '5月':'five_month',
            '6月':'six_month',
            '7月':'seven_month',
            '8月':'eight_month',
            '9月':'nine_month',
            '10月':'ten_month',
            '11月':'eleven_month',
            '12月':'twelve_month',
            '2年':'two_year',
            '3年':'three_year',
            '4年':'four_year',
            '5年':'five_year',
            'over5':'over_five_year',
        }
        per_dict = {}
        all_dict = {}
        if (dfs.get('age') is not None) and (dfs.get('age1') is not None):
            df1 = dfs['age']
            df2 = dfs['age1']
            df_age = pd.concat([df1,df2],ignore_index=True)
        elif dfs.get('age') is not None:
            df_age = dfs['age']
        else:
            df_age = None
        if df_age is not None:
            df = df_age
            for i in range(1,len(df.iloc[0,:])):
                item = df.iloc[0,i]
                for k,v in zip(list(df.iloc[1:,0]),list(df.iloc[1:,i])):
                    if v == 'nan' or v == '':
                        continue
                    if patt_m1.match(k):
                        m1 = int(patt_m1.match(k).groups()[0])
                        for i in range(1,m1+1):
                            per_dict['{}月'.format(i)] = v
                    elif patt_m2.match(k):
                        m2 = int(patt_m2.match(k).groups()[0])
                        m3 = int(patt_m2.match(k).groups()[1])
                        for i in range(m2+1,m3+1):
                            per_dict['{}月'.format(i)] = v
                    elif patt_m3.match(k):
                        m2 = int(patt_m2.match(k).groups()[0])
                        for i in range(m2 + 1, 13):
                            per_dict['{}月'.format(i)] = v
                    elif patt_y0.match(k):
                        for i in range(1, 13):
                            per_dict['{}月'.format(i)] = v
                    elif patt_y1.match(k):
                        y1 = int(patt_y1.match(k).groups()[0])
                        if y1 < 5:
                            for i in range(y1+1,6):
                                per_dict['{}年'.format(i)] = v
                        per_dict['over5'] = v
                    elif patt_y2.match(k):
                        y1 = int(patt_y2.match(k).groups()[0])
                        y2 = int(patt_y2.match(k).groups()[1])
                        for i in range(y1+1,y2+1):
                            per_dict['{}年'.format(i)] = v
                    else:
                        print('{},未匹配,百分比是{}'.format(k,v))
                        raise Exception
                all_dict[item] = per_dict
                per_dict = {}

        for item in all_dict:
            if models.AgeAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,item=item):
                obj = models.AgeAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,item=item)
                for k,v in all_dict[item].items():
                    setattr(obj,std_dict[k],v)
                obj.save()
            else:
                obj  = models.AgeAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    item=item,
                )
                for k,v in all_dict[item].items():
                    setattr(obj,std_dict[k],v)
                obj.save()

class NoSignificAmount(HandleIndexContent):
    '''
        单项金额不重大并单独计提坏账准备的应收款项
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(NoSignificAmount, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b050b0300','0b050b03']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            no_signific_amount_judgement = df.iloc[0,1]
            no_signific_amount_withdraw =  df.iloc[1,1]
            if models.CompaniBasicSituat.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.CompaniBasicSituat.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per)
                obj.no_signific_amount_judgement = no_signific_amount_judgement
                obj.no_signific_amount_withdraw = no_signific_amount_withdraw
                obj.save()
            else:
                models.CompaniBasicSituat.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    no_signific_amount_judgement=no_signific_amount_judgement,
                    no_signific_amount_withdraw=no_signific_amount_withdraw
                )
        else:
            pass

class DepreciOfFixAssetMethod(HandleIndexContent):
    '''
        固定资产折旧方法
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DepreciOfFixAssetMethod, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b05100200','0b051002']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            asset_type_pos = list(np.where(df.iloc[0, :].str.contains('类别'))[0])
            method_pos = list(np.where(df.iloc[0, :].str.contains('折旧方法'))[0])
            years_pos = list(np.where(df.iloc[0, :].str.contains('折旧年限'))[0])
            residu_rate_pos = list(np.where(df.iloc[0, :].str.contains('残值率'))[0])
            annual_depreci_rate_pos = list(np.where(df.iloc[0, :].str.contains('年折旧率'))[0])

            df = df.drop([0])
            asset_types = list(df.iloc[:,asset_type_pos[0]])
            methods = list(df.iloc[:,method_pos[0]])
            yearses = list(df.iloc[:,years_pos[0]])
            residu_rates = list(df.iloc[:,residu_rate_pos[0]])
            annual_depreci_rates = list(df.iloc[:,annual_depreci_rate_pos[0]])
            for (asset_type,method,years,residu_rate,annual_depreci_rate) in \
                zip(asset_types,methods,yearses,residu_rates,annual_depreci_rates):
                if models.DepreciOfFixAssetMethod.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,asset_type=asset_type):
                    obj = models.DepreciOfFixAssetMethod.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,asset_type=asset_type)
                    obj.method = method
                    obj.years = years
                    obj.residu_rate = residu_rate
                    obj.annual_depreci_rate = annual_depreci_rate
                    obj.save()
                else:
                    models.DepreciOfFixAssetMethod.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        asset_type=asset_type,
                        method=method,
                        years=years,
                        residu_rate=residu_rate,
                        annual_depreci_rate=annual_depreci_rate,
                    )
        else:
            pass

class RDExpenseAccountPolici(HandleIndexContent):
    '''
                内部研发支出会计政策
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RDExpenseAccountPolici, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b05150200','0b051502']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            if models.CompaniBasicSituat.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.CompaniBasicSituat.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.rd_expense_account_polici = instructi
                obj.save()
            else:
                models.CompaniBasicSituat.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    rd_expense_account_polici=instructi
                )
        else:
            pass

class IncomeAccountPolici(HandleIndexContent):
    '''
                收入会计政策
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(IncomeAccountPolici, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b051c0000','0b051c00']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            if models.CompaniBasicSituat.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.CompaniBasicSituat.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.income_account_polici = instructi
                obj.save()
            else:
                models.CompaniBasicSituat.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    income_account_polici=instructi
                )
        else:
            pass

class ChangInAccountEstim(HandleIndexContent):
    '''
                    会计估计变更
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInAccountEstim, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b05210200','0b052102']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            if models.CompaniBasicSituat.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.CompaniBasicSituat.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.chang_in_account_estim = instructi
                obj.save()
            else:
                models.CompaniBasicSituat.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    chang_in_account_estim=instructi
                )
        else:
            pass

class MainTaxAndTaxRate(HandleIndexContent):
    '''
            主要税种及税率
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MainTaxAndTaxRate, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b06010000','0b060100']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0,:].str.contains('计税依据').any():
                                    df = remove_space_from_df(table)
                                    dfs['main'] = df
                                elif table.iloc[0,:].str.contains('纳税主体名称').any():
                                    df = remove_space_from_df(table)
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

        if dfs.get('main') is not None :
            df = dfs['main']
            tax_type_pos = list(np.where(df.iloc[0, :].str.contains('税种'))[0])
            basi_pos = list(np.where(df.iloc[0, :].str.contains('计税依据'))[0])
            rate_pos = list(np.where(df.iloc[0, :].str.contains('税率'))[0])

            df = df.drop([0])
            tax_types = list(df.iloc[:,tax_type_pos[0]])
            basis = list(df.iloc[:,basi_pos[0]])
            rates = list(df.iloc[:,rate_pos[0]])

            for (tax_type,basi,rate) in \
                zip(tax_types,basis,rates):
                if models.MainTaxAndTaxRate.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,tax_type=tax_type):
                    obj = models.MainTaxAndTaxRate.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,tax_type=tax_type)
                    obj.basi = basi
                    obj.rate = rate
                    obj.save()
                else:
                    models.MainTaxAndTaxRate.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        tax_type=tax_type,
                        basi=basi,
                        rate=rate
                    )
        else:
            pass

        if dfs.get('income') is not None :
            df = dfs['income']
            name_pos = list(np.where(df.iloc[0, :].str.contains('纳税主体名称'))[0])
            rate_pos = list(np.where(df.iloc[0, :].str.contains('所得税税率'))[0])
            if len(df)>1:

                df = df.drop([0])
                names = list(df.iloc[:,name_pos[0]])
                rates = list(df.iloc[:,rate_pos[0]])

                for (name,rate) in \
                    zip(names,rates):
                    if models.IncomTaxRate.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,name=name):
                        obj = models.IncomTaxRate.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,name=name)
                        obj.rate = rate
                        obj.save()
                    else:
                        models.IncomTaxRate.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            name=name,
                            rate=rate
                        )
                else:
                    pass
        else:
            pass

class TaxIncent(HandleIndexContent):
    '''
                税收优惠
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(TaxIncent, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b06020000','0b060200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            if models.CompaniBasicSituat.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.CompaniBasicSituat.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.tax_incent = instructi
                obj.save()
            else:
                models.CompaniBasicSituat.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    tax_incent=instructi
                )
        else:
            pass

class MoneyFund(HandleIndexContent):
    '''
        货币资金
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MoneyFund, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07010000','0b070100']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:, 0].str.contains('银行存款').any():
                                    df = remove_space_from_df(table)
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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df)>0:
            begin_pos = list(np.where(df.iloc[0, :].str.contains('期初') | df.iloc[0, :].str.contains('年初')
                                      | df.iloc[0, :].str.contains('上期') | df.iloc[0, :].str.contains('上年'))[0])

            end_pos = list(np.where(df.iloc[0, :].str.contains('期末') | df.iloc[0, :].str.contains('年末')
                                    | df.iloc[0, :].str.contains('本期') | df.iloc[0, :].str.contains('本年'))[0])

            cash_pos = list(np.where(df.iloc[:, 0].str.contains('现金'))[0])
            bank_save_pos = list(np.where(df.iloc[:, 0].str.contains('银行存款'))[0])
            other_monetari_fund_pos = list(np.where(df.iloc[:, 0].str.contains('其他货币资金'))[0])
            total_pos = list(np.where(df.iloc[:, 0].str.contains('合计'))[0])
            oversea_total_amount_pos = list(np.where(df.iloc[:, 0].str.contains('存放在境外的款项总额'))[0])

            positions = [cash_pos,bank_save_pos,other_monetari_fund_pos,total_pos,oversea_total_amount_pos]
            subjects = ['cash','bank_save','other_monetari_fund','total','oversea_total_amount']
            begins = []
            ends = []

            for position in positions:
                if len(position) == 0:
                    begin = 0.00
                    end = 0.00
                else:
                    begin = Decimal(re.sub(',', '', str(df.iloc[position[0], begin_pos[0]]))) * unit_change[unit] \
                        if is_num(df.iloc[position[0], begin_pos[0]]) else 0.00
                    end = Decimal(re.sub(',', '', str(df.iloc[position[0], end_pos[0]]))) * unit_change[unit] \
                        if is_num(df.iloc[position[0], end_pos[0]])  else 0.00
                begins.append(begin)
                ends.append(end)
            all_dicts = {'before':begins,'end':ends}

            for item,values in all_dicts.items():
                if models.MoneyFund.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           before_end=item,typ_rep_id='A'):
                    obj = models.MoneyFund.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                               before_end=item, typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        if value == 'nan' or value == '':
                            value = 0.00
                        setattr(obj,subject,value)
                    obj.save()
                else:
                    obj = models.MoneyFund.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       before_end=item, typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        if value == 'nan' or value == '':
                            value = 0.00
                        setattr(obj,subject,value)
                    obj.save()
        else:
            pass

        obj_before = models.MoneyFund.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                           before_end='before', typ_rep_id='A')
        if obj_before.check_logic():
            pass
        else:
            raise Exception

        obj_end = models.MoneyFund.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                  before_end='end', typ_rep_id='A')
        if obj_end.check_logic():
            pass
        else:
            raise Exception

        if len(instructi) > 0:
            if  models.MoneyFund.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           before_end='end',typ_rep_id='A'):
                obj = models.MoneyFund.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           before_end='end',typ_rep_id='A')
                obj.instruct = instructi
                obj.save()
            else:
                models.MoneyFund.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    before_end='end',
                    typ_rep_id='A',
                    instruct=instructi,
                )
        else:
            pass

class BillReceivList(HandleIndexContent):
    '''
            应收票据分类
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BillReceivList, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07040100']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            begin_pos = list(np.where(df.iloc[0, :].str.contains('期初') | df.iloc[0, :].str.contains('年初')
                                      | df.iloc[0, :].str.contains('上期') | df.iloc[0, :].str.contains('上年'))[0])

            end_pos = list(np.where(df.iloc[0, :].str.contains('期末') | df.iloc[0, :].str.contains('年末')
                                    | df.iloc[0, :].str.contains('本期') | df.iloc[0, :].str.contains('本年'))[0])

            bank_pos = list(np.where(df.iloc[:, 0].str.contains('银行承兑'))[0])
            trade_pos = list(np.where(df.iloc[:, 0].str.contains('商业承兑'))[0])
            total_pos = list(np.where(df.iloc[:, 0].str.contains('合计'))[0])

            positions = [bank_pos, trade_pos, total_pos]
            subjects = ['bank', 'trade', 'total']
            begins = []
            ends = []

            for position in positions:
                if len(position) == 0:
                    begin = 0.00
                    end = 0.00
                else:
                    begin = Decimal(re.sub(',', '', str(df.iloc[position[0], begin_pos[0]]))) * unit_change[unit] \
                        if is_num(df.iloc[position[0], begin_pos[0]]) else 0.00
                    end = Decimal(re.sub(',', '', str(df.iloc[position[0], end_pos[0]]))) * unit_change[unit] \
                        if is_num(df.iloc[position[0], end_pos[0]]) else 0.00
                begins.append(begin)
                ends.append(end)
            all_dicts = {'before': begins, 'end': ends}

            for item, values in all_dicts.items():
                if models.BillReceiv.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                   before_end=item, typ_rep_id='A'):
                    obj = models.BillReceiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       before_end=item, typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        if value == 'nan' or value == '':
                            value = 0.00
                        setattr(obj, subject, value)
                    obj.save()
                else:
                    obj = models.BillReceiv.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          before_end=item, typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        if value == 'nan' or value == '':
                            value = 0.00
                        setattr(obj, subject, value)
                    obj.save()
        else:
            pass

        obj_before = models.BillReceiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                  before_end='before', typ_rep_id='A')
        if obj_before.check_logic():
            pass
        else:
            raise Exception

        obj_end = models.BillReceiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                               before_end='end', typ_rep_id='A')
        if obj_end.check_logic():
            pass
        else:
            raise Exception

class BillReceivPledg(HandleIndexContent):
    '''
            质押的应收票据情况
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BillReceivPledg, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07040200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末') | df.iloc[0, :].str.contains('年末')
                                    | df.iloc[0, :].str.contains('本期') | df.iloc[0, :].str.contains('本年'))[0])

            bank_pos = list(np.where(df.iloc[:, 0].str.contains('银行承兑'))[0])
            trade_pos = list(np.where(df.iloc[:, 0].str.contains('商业承兑'))[0])
            total_pos = list(np.where(df.iloc[:, 0].str.contains('合计'))[0])

            positions = [bank_pos, trade_pos, total_pos]
            subjects = ['bank_pledg', 'trade_pledg', 'total_pledg']
            ends = []

            for position in positions:
                if len(position) == 0:
                    end = 0.00
                else:
                    end = Decimal(re.sub(',', '', str(df.iloc[position[0], end_pos[0]]))) * unit_change[unit] \
                        if df.iloc[position[0], end_pos[0]] != 'nan' else 0.00
                ends.append(end)
            all_dicts = { 'end': ends}

            for item, values in all_dicts.items():
                if models.BillReceiv.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                   before_end=item, typ_rep_id='A'):
                    obj = models.BillReceiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       before_end=item, typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        if value == 'nan' or value == '':
                            value = 0.00
                        setattr(obj, subject, value)
                    obj.save()
                else:
                    obj = models.BillReceiv.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          before_end=item, typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        if value == 'nan' or value == '':
                            value = 0.00
                        setattr(obj, subject, value)
                    obj.save()
        else:
            pass

        obj_end = models.BillReceiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                               before_end='end', typ_rep_id='A')
        if obj_end.check_logic():
            pass
        else:
            raise Exception

class EndorsOrDiscount(HandleIndexContent):
    '''
            年末已背书或贴现且在资产负债表日尚未到期的应收票据
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(EndorsOrDiscount, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07040300']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            derecognition_pos = list(np.where(df.iloc[0, :].str.contains('期末终止确认') | df.iloc[0, :].str.contains('年末终止确认')
                                    | df.iloc[0, :].str.contains('本期') | df.iloc[0, :].str.contains('本年'))[0])
            recognition_pos = list(
                np.where(df.iloc[0, :].str.contains('期末未终止确认') | df.iloc[0, :].str.contains('年末未终止确认')
                         | df.iloc[0, :].str.contains('本期') | df.iloc[0, :].str.contains('本年'))[0])

            bank_pos = list(np.where(df.iloc[:, 0].str.contains('银行承兑'))[0])
            trade_pos = list(np.where(df.iloc[:, 0].str.contains('商业承兑'))[0])
            total_pos = list(np.where(df.iloc[:, 0].str.contains('合计'))[0])

            positions = [bank_pos, trade_pos, total_pos]
            de_subjects = ['bank_derecognition', 'trade_derecognition', 'total_derecognition']
            re_subjects = ['bank_recognition', 'trade_recognition', 'total_recognition']
            derecognitions = []
            recognitions = []

            for position in positions:
                if len(position) == 0:
                    recognition = 0.00
                    derecognition = 0.00
                else:

                    recognition = Decimal(re.sub(',', '', str(df.iloc[position[0], recognition_pos[0]]))) * \
                                    unit_change[unit] \
                        if is_num(df.iloc[position[0], recognition_pos[0]]) else 0.00
                    derecognition = Decimal(re.sub(',', '', str(df.iloc[position[0], derecognition_pos[0]]))) * unit_change[unit] \
                        if is_num(df.iloc[position[0], derecognition_pos[0]]) else 0.00
                recognitions.append(recognition)
                derecognitions.append(derecognition)
            all_dicts = {'recognition':recognitions, 'derecognition': derecognitions}

            for item, values in all_dicts.items():
                if models.BillReceiv.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                   before_end='end', typ_rep_id='A'):
                    obj = models.BillReceiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       before_end='end', typ_rep_id='A')
                    if item == 'recognition':
                        for subject, value in zip(re_subjects, values):
                            if value == 'nan' or value == '':
                                value = 0.00
                            setattr(obj, subject, value)
                    else:
                        for subject, value in zip(de_subjects, values):
                            if value == 'nan' or value == '':
                                value = 0.00
                            setattr(obj, subject, value)
                    obj.save()
                else:
                    obj = models.BillReceiv.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          before_end='end', typ_rep_id='A')
                    if item == 'recognition':
                        for subject, value in zip(re_subjects, values):
                            if value == 'NaN' or value == '':
                                value = 0.00
                            setattr(obj, subject, value)
                    else:
                        for subject, value in zip(de_subjects, values):
                            if value == 'NaN' or value == '':
                                value = 0.00
                            setattr(obj, subject, value)
                    obj.save()
        else:
            pass

        obj_end = models.BillReceiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                               before_end='end', typ_rep_id='A')
        if obj_end.check_logic():
            pass
        else:
            raise Exception

class TransferReceiv(HandleIndexContent):
    '''
                年末因出票人未履约而将其转应收账款的票据
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(TransferReceiv, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07040400']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
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
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末') | df.iloc[0, :].str.contains('年末')
                                    | df.iloc[0, :].str.contains('本期') | df.iloc[0, :].str.contains('本年'))[0])

            bank_pos = list(np.where(df.iloc[:, 0].str.contains('银行承兑'))[0])
            trade_pos = list(np.where(df.iloc[:, 0].str.contains('商业承兑'))[0])
            total_pos = list(np.where(df.iloc[:, 0].str.contains('合计'))[0])

            positions = [bank_pos, trade_pos, total_pos]
            subjects = ['bank_transfer_receiv', 'trade_transfer_receiv', 'total_transfer_receiv']
            ends = []

            for position in positions:
                if len(position) == 0:
                    end = 0.00
                else:
                    end = Decimal(re.sub(',', '', str(df.iloc[position[0], end_pos[0]]))) * unit_change[unit] \
                        if is_num(df.iloc[position[0], end_pos[0]]) else 0.00
                ends.append(end)
            all_dicts = {'end': ends}

            for item, values in all_dicts.items():
                if models.BillReceiv.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                    before_end=item, typ_rep_id='A'):
                    obj = models.BillReceiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                        before_end=item, typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        if value == 'nan' or value == '':
                            value = 0.00
                        setattr(obj, subject, value)
                    obj.save()
                else:
                    obj = models.BillReceiv.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           before_end=item, typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        if value == 'nan' or value == '':
                            value = 0.00
                        setattr(obj, subject, value)
                    obj.save()
        else:
            pass

        obj_end = models.BillReceiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                before_end='end', typ_rep_id='A')
        if obj_end.check_logic():
            pass
        else:
            raise Exception

class ReceivClassifDisclosur(HandleIndexContent):
    '''
                    应收账款/其他应收款分类披露
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ReceivClassifDisclosur, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        dfs['age'] = []
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07050100','0b07090100']:
            for k,content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:,0].str.contains('单项金额重大').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['summari'] = df
                                elif table.iloc[:,0].str.contains('账龄').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['age'].append(df)
                                elif table.iloc[:,0].str.contains('按单位').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['signi'] = df
                                elif table.iloc[:,0].str.contains('组合').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    if '其他方法计提坏账准备' in self.indexcontent[k-1]['t']:
                                        dfs['other'] = df
                                    else:
                                        dfs['per'] = df
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
        accounts = {'0b07050100':'account','0b07090100':'other'}
        pattern_num = re.compile('^.*?\d+.*?$')
        dfs, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if dfs.get('summari') is not None:
            df = dfs['summari']
            # end_balanc_pos = list(np.where((df.iloc[0,:].str.contains('期末') | df.iloc[0, :].str.contains('年末'))\
            #                         & df.iloc[1, :].str.contains('账面余额') & df.iloc[2, :].str.contains('金额'))[0])
            # end_bad_debt_prepar_pos = list((np.where(df.iloc[0, :].str.contains('期末') | df.iloc[0, :].str.contains('年末'))\
            #                         & df.iloc[1, :].str.contains('坏账准备') & df.iloc[2, :].str.contains('金额'))[0])
            # end_value_pos = list(np.where((df.iloc[0, :].str.contains('期末') | df.iloc[0, :].str.contains('年末'))\
            #                             & df.iloc[2,:].str.contains('账面价值'))[0])
            # before_balanc_pos = list(np.where((df.iloc[0, :].str.contains('期初') | df.iloc[0, :].str.contains('年初'))
            #                                & df.iloc[1, :].str.contains('账面余额') & df.iloc[2, :].str.contains('金额'))[0])
            #
            # before_bad_debt_prepar_pos = list(np.where((df.iloc[0, :].str.contains('期初') | df.iloc[0, :].str.contains('年初'))
            #                                         & df.iloc[1, :].str.contains('坏账准备') & df.iloc[2,
            #                                                                                    :].str.contains('金额'))[
            #                                    0])
            # before_value_pos = list(np.where((df.iloc[0, :].str.contains('期初') | df.iloc[0, :].str.contains('年初'))
            #                               & df.iloc[2, :].str.contains('账面价值'))[0])

            signific_pos = list(np.where(df.iloc[:, 0].str.contains('单项金额重大'))[0])
            combin_pos = list(np.where(df.iloc[:, 0].str.contains('信用风险特征组合'))[0])
            no_signific_pos = list(np.where(df.iloc[:, 0].str.contains('单项金额不重大'))[0])
            total_pos = list(np.where(df.iloc[:, 0].str.match('合计'))[0])

            positions = [signific_pos, combin_pos, no_signific_pos,total_pos]
            ends_pos = [[1],[3],[5]]
            befores_pos = [[6],[8],[10]]
            subjects = ['signific_balanc', 'signific_bad_debt_prepar', 'signific_value', \
                        'combin_balanc','combin_bad_debt_prepar','combin_value',\
                        'no_signific_balanc','no_signific_bad_debt_prepar','no_signific_value', \
                        'total_balanc','total_bad_debt_prepar','total_value']

            ends = []
            befores = []
            for position in positions:
                for before_pos in befores_pos:
                    if len(position) == 0:
                        before = 0.00
                    else:
                        before = Decimal(re.sub(',', '', str(df.iloc[position[0], before_pos[0]]))) * unit_change[unit] \
                            if is_num(df.iloc[position[0], before_pos[0]])  else 0.00
                    befores.append(before)
                for end_pos in ends_pos:
                    if len(position) == 0:
                        end = 0.00
                    else:
                        end = Decimal(re.sub(',', '', str(df.iloc[position[0], end_pos[0]]))) * unit_change[unit] \
                            if is_num(df.iloc[position[0], end_pos[0]]) else 0.00
                    ends.append(end)

            all_dicts = {'end': ends,'before':befores}
            for item, values in all_dicts.items():
                if models.Receiv.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                    before_end=item,subject=accounts[self.indexno], typ_rep_id='A'):
                    obj = models.Receiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                        before_end=item,subject=accounts[self.indexno], typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        setattr(obj, subject, value)
                    obj.save()
                else:
                    obj = models.Receiv.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           before_end=item, subject=accounts[self.indexno],typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        setattr(obj, subject, value)
                    obj.save()
        else:
            pass

        obj_before = models.Receiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                            before_end='before', subject=accounts[self.indexno], typ_rep_id='A')
        if obj_before.check_logic():
            pass
        else:
            raise Exception

        obj_end = models.Receiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                before_end='end', subject=accounts[self.indexno],typ_rep_id='A')
        if obj_end.check_logic():
            pass
        else:
            raise Exception


        if dfs.get('signi') is not None and len(dfs['signi'])>1:
            df = dfs['signi']
            name_pos = list(np.where(df.iloc[1, :].str.contains('按单位'))[0])
            balanc_pos = list(np.where(df.iloc[1, :].str.contains('应收账款')|df.iloc[1, :].str.contains('其他应收款'))[0])
            bad_debt_prepar_pos = list(np.where(df.iloc[1, :].str.contains('坏账准备'))[0])
            reason_pos = list(np.where(df.iloc[1, :].str.contains('计提理由'))[0])

            names = list(df.iloc[1:,name_pos[0]])
            balancs = list(df.iloc[1:,balanc_pos[0]])
            bad_debt_prepars = list(df.iloc[1:,bad_debt_prepar_pos[0]])
            reasons = list(df.iloc[1:,reason_pos[0]])

            for (name,balanc,bad_debt_prepar,reason) in zip(names,balancs,bad_debt_prepars,reasons):
                if models.SignificReceiv.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                before_end='end', subject='account', typ_rep_id='A',name=name):
                    obj = models.SignificReceiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                    before_end='end', subject='account', typ_rep_id='A',name=name)
                    obj.balanc = balanc
                    obj.bad_debt_prepar = bad_debt_prepar
                    obj.reason = reason
                    obj.save()
                else:
                    models.SignificReceiv.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        before_end='end',
                        subject='account',
                        typ_rep_id='A',
                        name = name,
                        balanc = balanc,
                        bad_debt_prepar = bad_debt_prepar,
                        reason = reason,
                    )
        else:
            pass

        obj_end = models.SignificReceiv.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                            before_end='end', subject=accounts[self.indexno], typ_rep_id='A')
        if len(obj_end)>0:
            if obj_end[0].check_logic():
                pass
            else:
                raise Exception
        else:
            pass

        if dfs.get('age') is not None:
            if len(dfs['age']) == 1:
                df = dfs['age'][0]
            else:
                df = pd.concat(dfs['age'],ignore_index=True)

            one_year_pos = list(np.where(df.iloc[:, 0].str.contains('1年以内小计'))[0])
            two_year_pos = list(np.where(df.iloc[:, 0].str.match(r'^.*?1.*?2.*?年.*?$')|df.iloc[:, 0].str.match(r'^.*?1.*?年.*?以上.*?$'))[0])
            three_year_pos = list(np.where(df.iloc[:, 0].str.match(r'^.*?2.*?3.*?年.*?$')|df.iloc[:, 0].str.match(r'^.*?2.*?年.*?以上.*?$'))[0])
            four_year_pos = list(np.where(df.iloc[:, 0].str.match(r'^.*?3.*?4.*?年.*?$')|df.iloc[:, 0].str.match(r'^.*?3.*?年.*?以上.*?$'))[0])
            five_year_pos = list(np.where(df.iloc[:, 0].str.match(r'^.*?4.*?5.*?年.*?$')|df.iloc[:, 0].str.match(r'^.*?4.*?年.*?以上.*?$'))[0])
            over_five_pos = list(np.where(df.iloc[:, 0].str.match(r'^.*?5.*?年.*?以上.*?$'))[0])
            total_pos = list(np.where(df.iloc[:, 0].str.contains('合计'))[0])
            # balanc_pos = list(np.where(df.iloc[0, :].str.contains('期末') | df.iloc[0, :].str.contains('年末')
            #                                & df.iloc[1, :].str.contains('应收账款'))[0])
            # bad_debt_prepar_pos = list(np.where(df.iloc[0, :].str.contains('期末') | df.iloc[0, :].str.contains('年末')
            #                                         & df.iloc[1, :].str.contains('坏账准备'))[0])


            positions = [one_year_pos, two_year_pos, three_year_pos, four_year_pos,five_year_pos,over_five_pos,total_pos]
            ends_pos = [[1], [2]]
            subjects = ['one_year_balanc', 'two_year_balanc', 'three_year_balanc', \
                        'four_year_balanc', 'five_year_balanc', 'over_five_balanc', \
                        'total_balanc', 'one_year_bad_debt_prepar', 'two_year_bad_debt_prepar', \
                        'three_year_bad_debt_prepar', 'four_year_bad_debt_prepar', 'five_year_bad_debt_prepar', \
                        'over_five_bad_debt_prepar','total_bad_debt_prepar']

            ends = []
            for end_pos in ends_pos:
                for position in positions:
                    if len(position) == 0:
                        end = 0.00
                    else:
                        end = Decimal(re.sub(',', '', str(df.iloc[position[0], end_pos[0]]))) * unit_change[unit] \
                            if df.iloc[position[0], end_pos[0]] != 'nan' else 0.00
                    ends.append(end)

            all_dicts = {'end': ends}

            for item, values in all_dicts.items():
                if models.ReceivAge.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                before_end=item, subject=accounts[self.indexno], typ_rep_id='A'):
                    obj = models.ReceivAge.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                    before_end=item, subject=accounts[self.indexno], typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        setattr(obj, subject, value)
                    obj.save()
                else:
                    obj = models.ReceivAge.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       before_end=item, subject=accounts[self.indexno], typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        setattr(obj, subject, value)
                    obj.save()
        else:
            pass

        obj_end = models.ReceivAge.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                            before_end='end', subject=accounts[self.indexno], typ_rep_id='A')
        if len(obj_end)>0:
            if obj_end[0].check_logic():
                pass
            else:
                raise Exception
        else:
            pass

        if dfs.get('other') is not None:
            df = dfs['other']
            name_pos = list(np.where(df.iloc[1, :].str.contains('组合'))[0])
            balanc_pos = list(np.where(df.iloc[1, :].str.contains('应收账款')|df.iloc[1, :].str.contains('其他应收款'))[0])
            bad_debt_prepar_pos = list(np.where(df.iloc[1, :].str.contains('坏账准备'))[0])

            names = df.iloc[2:,name_pos[0]]
            balancs = df.iloc[2:,balanc_pos[0]]
            bad_debt_prepars = df.iloc[2:,bad_debt_prepar_pos[0]]
            for (name,balanc,bad_debt_prepar) in zip(names,balancs,bad_debt_prepars):
                if models.ReceivOtherCombin.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                   before_end='end', subject=accounts[self.indexno], typ_rep_id='A',name=name):
                    obj = models.ReceivOtherCombin.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       before_end='end', subject=accounts[self.indexno], typ_rep_id='A',name=name)
                    obj.balanc = Decimal(re.sub(',', '', str(balanc))) * unit_change[unit] if pattern_num.match(balanc) else 0.00

                    obj.bad_debt_prepar = Decimal(re.sub(',', '', str(bad_debt_prepar))) * unit_change[unit] if pattern_num.match(bad_debt_prepar) else 0.00
                    obj.save()
                else:
                    obj = models.ReceivOtherCombin.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        before_end='end',
                        subject=accounts[self.indexno],
                        typ_rep_id='A',
                        name=name,
                        balanc=Decimal(re.sub(',', '', str(balanc))) * unit_change[unit] if pattern_num.match(balanc) else 0.00,
                        bad_debt_prepar=Decimal(re.sub(',', '', str(bad_debt_prepar))) * unit_change[unit] if pattern_num.match(bad_debt_prepar) else 0.00,
                    )
        else:
            pass

        obj_end = models.ReceivOtherCombin.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                  before_end='end', subject=accounts[self.indexno], typ_rep_id='A',name='合计')
        if len(obj_end) > 0:
            if obj_end[0].check_logic():
                pass
            else:
                raise Exception
        else:
            pass

class WithdrawOrReturnBadDebtPrepar(HandleIndexContent):
    '''
                本年计提、收回或转回的坏账准备情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(WithdrawOrReturnBadDebtPrepar, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0b07050200','0b07090200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
        accounts={'0b07050200':'account','0b07090200':'other'}
        pattern = re.compile('^.*?计提坏账准备金额(.*\d\.{0,1}\d*?)(.*?元).*?收回或转回坏账准备金额(.*\d?\.{0,1}\d*?)(.*?元).*?$')
        if len(instructi) > 0:
            unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
            withdraw = pattern.match(instructi).groups()[0]
            unit = pattern.match(instructi).groups()[1]
            return_amount = pattern.match(instructi).groups()[2]
            if models.WithdrawOrReturnBadDebtPrepar.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,before_end='end', \
                                                                   subject=accounts[self.indexno],typ_rep_id='A'):
                obj = models.WithdrawOrReturnBadDebtPrepar.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,before_end='end', \
                                                                   subject=accounts[self.indexno],typ_rep_id='A')
                obj.withdraw = Decimal(re.sub(',', '', str(withdraw))) * unit_change[unit] \
                                    if is_num(withdraw) else 0.00
                obj.return_amount = Decimal(re.sub(',', '', str(return_amount))) * unit_change[unit] \
                    if is_num(return_amount)  else 0.00
                obj.save()
            else:
                models.WithdrawOrReturnBadDebtPrepar.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    before_end='end',
                    subject=accounts[self.indexno],
                    typ_rep_id='A',
                    withdraw=Decimal(re.sub(',', '', str(withdraw))) * unit_change[unit] \
                        if is_num(withdraw)  else 0.00,
                    return_amount=Decimal(re.sub(',', '', str(return_amount))) * unit_change[unit] \
                        if is_num(return_amount) else 0.00,
                )
        else:
            pass

        if df is not None and len(df)>1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('单位名称'))[0])
            amount_pos = list(np.where(df.iloc[0, :].str.contains('金额'))[0])
            style_pos = list(np.where(df.iloc[0, :].str.contains('方式'))[0])

            names = list(df.iloc[1:,name_pos[0]])
            amounts = list(df.iloc[1:,amount_pos[0]])
            styles = list(df.iloc[1:,style_pos[0]])

            for (name,amount,style) in zip(names,amounts,styles):
                if models.ReturnBadDebtPreparList.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                   before_end='end', subject=accounts[self.indexno], typ_rep_id='A',name=name):
                    obj = models.ReturnBadDebtPreparList.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       before_end='end', subject=accounts[self.indexno], typ_rep_id='A',name=name)
                    obj.amount = Decimal(re.sub(',', '', str(amount))) * unit_change[unit] if is_num(amount) else 0.00

                    obj.style = style
                    obj.save()
                else:
                    obj = models.ReturnBadDebtPreparList.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        before_end='end',
                        subject=accounts[self.indexno],
                        typ_rep_id='A',
                        name=name,
                        amount=Decimal(re.sub(',', '', str(amount))) * unit_change[unit] if is_num(amount)  else 0.00,
                        style=style
                    )

class WriteOffReceiv(HandleIndexContent):
    '''
                    本期实际核销的应收账款情况
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(WriteOffReceiv, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07050300','0b07090300']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0,:].str.contains('单位名称').any():
                                    df = remove_space_from_df(table)
                                    dfs['important'] = df
                                elif table.iloc[0,:].str.contains('项目').any():
                                    df = remove_space_from_df(table)
                                    dfs['sum'] = df
                                else:
                                    pass
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
        accounts = {'0b07050300':'account','0b07090300':'other'}
        dfs, unit, instructi = self.recognize()
        if dfs.get('sum') is not None and len(dfs['sum']) > 1:
            df = dfs['sum']
            unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
            writeoff = df.iloc[-1,1]

            if models.WithdrawOrReturnBadDebtPrepar.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                   before_end='end', \
                                                                   subject=accounts[self.indexno], typ_rep_id='A'):
                obj = models.WithdrawOrReturnBadDebtPrepar.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                       before_end='end', \
                                                                       subject=accounts[self.indexno], typ_rep_id='A')
                obj.writeoff = Decimal(re.sub(',', '', str(writeoff))) * unit_change[unit] \
                    if is_num(writeoff)  else 0.00
                obj.save()
            else:
                models.WithdrawOrReturnBadDebtPrepar.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    before_end='end',
                    subject=accounts[self.indexno],
                    typ_rep_id='A',
                    writeoff=Decimal(re.sub(',', '', str(writeoff))) * unit_change[unit] \
                        if is_num(writeoff) else 0.00,

                )
        else:
            pass

        if dfs.get('important') is not None and len(dfs['important']) > 1:
            df = dfs['important']
            name_pos = list(np.where(df.iloc[0, :].str.contains('单位名称'))[0])
            natur_pos = list(np.where(df.iloc[0, :].str.contains('性质'))[0])
            writeoff_pos = list(np.where(df.iloc[0, :].str.contains('金额'))[0])
            reason_pos = list(np.where(df.iloc[0, :].str.contains('原因'))[0])
            program_pos = list(np.where(df.iloc[0, :].str.contains('核销程序'))[0])
            is_related_pos = list(np.where(df.iloc[0, :].str.contains('关联交易'))[0])

            names = list(df.iloc[1:, name_pos[0]])
            naturs = list(df.iloc[1:, natur_pos[0]])
            writeoffs = list(df.iloc[1:, writeoff_pos[0]])
            reasons = list(df.iloc[1:, reason_pos[0]])
            programs = list(df.iloc[1:, program_pos[0]])
            is_relateds = list(df.iloc[1:, is_related_pos[0]])

            for (name, natur, writeoff,reason,program,is_related) in \
            zip(names, naturs, writeoffs,reasons,programs,is_relateds):
                if models.WriteOffReceiv.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                 before_end='end', subject=accounts[self.indexno], typ_rep_id='A',
                                                                 name=name):
                    obj = models.WriteOffReceiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                     before_end='end', subject=accounts[self.indexno],
                                                                     typ_rep_id='A', name=name)
                    obj.writeoff = Decimal(re.sub(',', '', str(writeoff))) * unit_change[unit] if is_num(writeoff) else 0.00

                    obj.natur = natur
                    obj.reason = reason
                    obj.program = program
                    obj.is_related = is_related
                    obj.save()
                else:
                    obj = models.WriteOffReceiv.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        before_end='end',
                        subject=accounts[self.indexno],
                        typ_rep_id='A',
                        name=name,
                        writeoff=Decimal(re.sub(',', '', str(writeoff))) * unit_change[unit] if is_num(writeoff) else 0.00,
                        natur=natur,
                        reason=reason,
                        program=program,
                        is_related=is_related,
                    )

class Top5Receiv(HandleIndexContent):
    '''
           应收款项前5名
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(Top5Receiv, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07050400','0b07060200','0b07090500']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
        accounts = {'0b07050400':'account','0b07060200':'prepay','0b07090500':'other'}
        df, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:

            name_pos = list(np.where(df.iloc[0, :].str.contains('单位名称')|df.iloc[0, :].str.contains('对象'))[0])
            natur_pos = list(np.where(df.iloc[0, :].str.contains('性质'))[0])
            balanc_pos = list(np.where((df.iloc[0, :].str.contains('金额')|df.iloc[0, :].str.contains('余额')) &
                                       (~df.iloc[0, :].str.contains('坏账准备')))[0])
            bad_debt_prepar_pos = list(np.where(df.iloc[0, :].str.contains('坏账准备'))[0])
            ratio_pos = list(np.where(df.iloc[0, :].str.contains('比例'))[0])
            age_pos = list(np.where(df.iloc[0, :].str.contains('账龄'))[0])
            related_pos = list(np.where(df.iloc[0, :].str.contains('关系'))[0])
            reason_pos = list(np.where(df.iloc[0, :].str.contains('原因'))[0])

            start_row_pos = list(np.where(df.iloc[:,ratio_pos[0]].str.match(r'.*?\d+.*?'))[0])
            data_length = len(df.iloc[start_row_pos[0]:,:])
            names = list(df.iloc[start_row_pos[0]:, name_pos[0]]) if len(name_pos)>0 else ['' for i in range(data_length)]
            naturs = list(df.iloc[start_row_pos[0]:, natur_pos[0]]) if len(natur_pos)>0 else ['' for i in range(data_length)]
            balancs = list(df.iloc[start_row_pos[0]:, balanc_pos[0]]) if len(balanc_pos)>0 else [0.00 for i in range(data_length)]
            bad_debt_prepars = list(df.iloc[start_row_pos[0]:, bad_debt_prepar_pos[0]]) if len(bad_debt_prepar_pos)>0 else [0.00 for i in range(data_length)]
            ages = list(df.iloc[start_row_pos[0]:, age_pos[0]]) if len(age_pos)>0 else ['' for i in range(data_length)]
            relateds = list(df.iloc[start_row_pos[0]:, related_pos[0]]) if len(related_pos)>0 else ['' for i in range(data_length)]
            reasons = list(df.iloc[start_row_pos[0]:, reason_pos[0]]) if len(reason_pos)>0 else ['' for i in range(data_length)]

            for (name, natur, balanc, bad_debt_prepar,age, related,reason) in \
                    zip(names, naturs, balancs, bad_debt_prepars,ages, relateds,reasons):
                if models.Top5Receiv.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                        before_end='end', subject=accounts[self.indexno], typ_rep_id='A',
                                                        name=name):
                    obj = models.Top5Receiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            before_end='end', subject=accounts[self.indexno],
                                                            typ_rep_id='A', name=name)
                    obj.balanc = Decimal(re.sub(',', '', str(balanc))) * unit_change[
                        unit] if is_num(balanc)  else 0.00
                    obj.bad_debt_prepar = Decimal(re.sub(',', '', str(bad_debt_prepar))) * unit_change[
                        unit] if is_num(bad_debt_prepar) else 0.00
                    obj.natur = natur
                    obj.age = age
                    obj.related = related
                    obj.reason = reason
                    obj.save()
                else:
                    obj = models.Top5Receiv.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        before_end='end',
                        subject=accounts[self.indexno],
                        typ_rep_id='A',
                        name=name,
                        balanc=Decimal(re.sub(',', '', str(balanc))) * unit_change[
                            unit] if is_num(balanc) else 0.00,
                        bad_debt_prepar=Decimal(re.sub(',', '', str(bad_debt_prepar))) * unit_change[
                            unit] if is_num(bad_debt_prepar) else 0.00,
                        natur=natur,
                        age=age,
                        related=related,
                        reason=reason,
                    )

class PrepayAge(HandleIndexContent):
    '''
                        预付款项按账龄列示
                    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(PrepayAge, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07060100']:
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

        if df is not None and len(df)>1:
            one_year_pos = list(np.where(df.iloc[:, 0].str.contains('1年以内'))[0])
            two_year_pos = list(np.where(
                df.iloc[:, 0].str.match(r'^.*?1.*?2.*?年.*?$') | df.iloc[:, 0].str.match(r'^.*?1.*?年.*?以上.*?$'))[0])
            three_year_pos = list(np.where(
                df.iloc[:, 0].str.match(r'^.*?2.*?3.*?年.*?$') | df.iloc[:, 0].str.match(r'^.*?2.*?年.*?以上.*?$'))[0])
            four_year_pos = list(np.where(
                df.iloc[:, 0].str.match(r'^.*?3.*?4.*?年.*?$') | df.iloc[:, 0].str.match(r'^.*?3.*?年.*?以上.*?$'))[0])
            five_year_pos = list(np.where(
                df.iloc[:, 0].str.match(r'^.*?4.*?5.*?年.*?$') | df.iloc[:, 0].str.match(r'^.*?4.*?年.*?以上.*?$'))[0])
            over_five_pos = list(np.where(df.iloc[:, 0].str.match(r'^.*?5.*?年.*?以上.*?$'))[0])
            total_pos = list(np.where(df.iloc[:, 0].str.contains('合计'))[0])

            positions = [one_year_pos, two_year_pos, three_year_pos, four_year_pos, five_year_pos, over_five_pos,
                         total_pos]
            subjects = ['one_year_balanc', 'two_year_balanc', 'three_year_balanc', \
                        'four_year_balanc', 'five_year_balanc', 'over_five_balanc', \
                        'total_balanc', 'one_year_bad_debt_prepar', 'two_year_bad_debt_prepar', \
                        'three_year_bad_debt_prepar', 'four_year_bad_debt_prepar', 'five_year_bad_debt_prepar', \
                        'over_five_bad_debt_prepar', 'total_bad_debt_prepar']

            ends = []
            befores = []
            for position in positions:
                if len(position) == 0:
                    end = 0.00
                else:
                    end = Decimal(re.sub(',', '', str(df.iloc[position[0], 1]))) * unit_change[unit] \
                        if is_num(df.iloc[position[0],1])  else 0.00
                ends.append(end)
            for position in positions:
                if len(position) == 0:
                    before = 0.00
                else:
                    before = Decimal(re.sub(',', '', str(df.iloc[position[0], 3]))) * unit_change[unit] \
                        if is_num(df.iloc[position[0],3]) else 0.00
                befores.append(before)

            all_dicts = {'end': ends,'before':befores}

            for item, values in all_dicts.items():
                if models.ReceivAge.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                   before_end=item, subject='prepay', typ_rep_id='A'):
                    obj = models.ReceivAge.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       before_end=item, subject='prepay', typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        setattr(obj, subject, value)
                    obj.save()
                else:
                    obj = models.ReceivAge.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          before_end=item, subject='prepay', typ_rep_id='A')
                    for subject, value in zip(subjects, values):
                        setattr(obj, subject, value)
                    obj.save()
        else:
            pass

        obj_end = models.ReceivAge.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                  before_end='end', subject='prepay', typ_rep_id='A')
        obj_before = models.ReceivAge.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                  before_end='before', subject='prepay', typ_rep_id='A')
        if len(obj_end) > 0:
            if obj_end[0].check_logic():
                pass
            else:
                raise Exception
        else:
            pass

        if len(obj_before) > 0:
            if obj_before[0].check_logic():
                pass
            else:
                raise Exception
        else:
            pass

class CommonBeforeAndEnd(HandleIndexContent):
    '''
        通用项目期初期末
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CommonBeforeAndEnd, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07070100','0b07080100','0b07090400','0b070d0000','0b07150000',\
                            '0b07160000','0b071d0400','0b071d0500','0b071e0000','0b071f0100','0b07200000',\
                            '0b07220000','0b07230100','0b07240100']:
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
        accounts = {'0b07070100':'interest_receiv','0b07080100':'dividend_receiv',\
                    '0b07090400':'other_receiv_natur','0b070d0000':'other_current_asset',\
                    '0b07150000':'engin_materi','0b07160000':'fix_asset_clean_up',\
                    '0b071d0400':'unconfirm_defer_incom_tax','0b071d0500':'expir_in_the_follow_year',\
                    '0b071e0000':'other_noncurr_asset','0b071f0100':'shortterm_loan',\
                    '0b07200000':'financi_liabil_measur_at_fair_valu','0b07220000':'bill_payabl',\
                    '0b07230100':'account_payabl','0b07240100':'advanc_receipt'}
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末')|df.iloc[0, :].str.contains('年末')|
                                    df.iloc[0, :].str.contains('本期') | df.iloc[0, :].str.contains('本年'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初')|df.iloc[0, :].str.contains('年初')|
                                       df.iloc[0, :].str.contains('上期') | df.iloc[0, :].str.contains('上年'))[0])
            instruct_pos = list(np.where(df.iloc[0, :].str.contains('备注') | df.iloc[0, :].str.contains('说明'))[0])
            names = list(df.iloc[1:,0])
            ends = list(df.iloc[1:,end_pos[0]])
            befores = list(df.iloc[1:,before_pos[0]])
            instructs = list(df.iloc[1:,instruct_pos[0]]) if len(instruct_pos)>0 else ['' for i in range(len(df)-1)]

            all_dicts = {'e': ends, 'b': befores}
            for item, values in all_dicts.items():
                for name, value,instruct in zip(names, values,instructs):
                    if models.CommonBeforeAndEndName.objects.filter(name=name):
                        obj_name = models.CommonBeforeAndEndName.objects.get(subject=accounts[self.indexno],name=name)
                    else:
                        obj_name = models.CommonBeforeAndEndName.objects.create(subject=accounts[self.indexno],name=name)

                    value = Decimal(re.sub(',', '', str(value))) * unit_change[unit] if is_num(value) else 0.00
                    if models.CommonBeforeAndEnd.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       before_end=item, subject=accounts[self.indexno], typ_rep_id='A',name_id=obj_name.id):
                        obj = models.CommonBeforeAndEnd.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           before_end=item, subject=accounts[self.indexno], typ_rep_id='A',name_id=obj_name.id)
                        obj.amount = value
                        obj.instruct = instruct
                        obj.save()
                    else:
                        models.CommonBeforeAndEnd.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            before_end=item,
                            subject=accounts[self.indexno],
                            typ_rep_id='A',
                            name_id=obj_name.id,
                            amount=value,
                            instruct=instruct,
                        )
        else:
            pass

        comprehens_notes = {
            '0b071f0100':'shortterm_loan',
        }

        if (self.indexno in comprehens_notes) and len(instructi) > 1:
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,typ_rep_id='A'):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,typ_rep_id='A')
                setattr(obj,comprehens_notes[self.indexno],instructi)
                obj.save()
            else:
                obj = models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                )
                setattr(obj, comprehens_notes[self.indexno], instructi)
                obj.save()
        else:
            pass

class CommonBalancImpairNet(HandleIndexContent):
    '''
            通用项目账面余额，减值准备，账面价值
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CommonBalancImpairNet, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b070a0100','0b07140100']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0,:].str.contains('余额').any():
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
        accounts = {'0b070a0100': 'inventori','0b07140100':'construct_in_progress'}
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}

        if df is not None and len(df) > 1:
            # end_pos = list(np.where(df.iloc[0, :].str.contains('期末') | df.iloc[0, :].str.contains('年末') |
            #                         df.iloc[0, :].str.contains('本期') | df.iloc[0, :].str.contains('本年'))[0])
            # before_pos = list(np.where(df.iloc[0, :].str.contains('期初') | df.iloc[0, :].str.contains('年初') |
            #                            df.iloc[0, :].str.contains('上期') | df.iloc[0, :].str.contains('上年'))[0])

            names = list(df.iloc[2:, 0])
            ends = list(zip(list(df.iloc[2:, 1]),list(df.iloc[2:, 2]),list(df.iloc[2:, 3])))
            befores = list(zip(list(df.iloc[2:, 4]),list(df.iloc[2:, 5]),list(df.iloc[2:, 6])))

            all_dicts = {'end': ends, 'before': befores}
            for item, values in all_dicts.items():
                for name, value in zip(names, values):
                    balanc,impair,net = value
                    balance = Decimal(re.sub(',', '', str(balanc))) * unit_change[unit] if is_num(balanc) else 0.00
                    impair = Decimal(re.sub(',', '', str(impair))) * unit_change[unit] if is_num(impair) else 0.00
                    net = Decimal(re.sub(',', '', str(net))) * unit_change[unit] if is_num(net) else 0.00
                    if models.CommonBalancImpairNet.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                before_end=item, subject=accounts[self.indexno],
                                                                typ_rep_id='A', name=name):
                        obj = models.CommonBalancImpairNet.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                    before_end=item, subject=accounts[self.indexno],
                                                                    typ_rep_id='A', name=name)

                        obj.balance = balance
                        obj.impair = impair
                        obj.net = net
                        obj.save()
                    else:
                        models.CommonBalancImpairNet.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            before_end=item,
                            subject=accounts[self.indexno],
                            typ_rep_id='A',
                            name=name,
                            balance=balance,
                            impair=impair,
                            net=net,
                        )
        else:
            pass

class MajorLiabilAgeOver1Year(HandleIndexContent):
    '''
            账龄超过1年的重要负债或逾期应付利息
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MajorLiabilAgeOver1Year, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07230200','0b07240200']:
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
        accounts = {'0b07230200': 'ap','0b07240200':'ar'}
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末') | df.iloc[0, :].str.contains('年末') |
                                    df.iloc[0, :].str.contains('本期') | df.iloc[0, :].str.contains('本年'))[0])
            instruct_pos = list(np.where(df.iloc[0, :].str.contains('备注') | df.iloc[0, :].str.contains('说明')|
                                         df.iloc[0, :].str.contains('原因'))[0])
            names = list(df.iloc[1:, 0])
            ends = list(df.iloc[1:, end_pos[0]])
            instructs = list(df.iloc[1:, instruct_pos[0]]) if len(instruct_pos) > 0 else ['' for i in
                                                                                          range(len(df) - 1)]

            for name, value, instruct in zip(names, ends, instructs):
                value = Decimal(re.sub(',', '', str(value))) * unit_change[unit] if is_num(value) else 0.00
                if models.MajorLiabilAgeOver1Year.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                             subject=accounts[self.indexno],
                                                            typ_rep_id='A', name=name):
                    obj = models.MajorLiabilAgeOver1Year.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                subject=accounts[self.indexno],
                                                                typ_rep_id='A', name=name)

                    obj.amount = value
                    obj.reason = instruct
                    obj.save()
                else:
                    models.MajorLiabilAgeOver1Year.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        subject=accounts[self.indexno],
                        typ_rep_id='A',
                        name=name,
                        amount=value,
                        reason=instruct,
                    )
        else:
            pass

        comprehens_notes = {

        }

        if (self.indexno in comprehens_notes) and len(instructi) > 1:
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, typ_rep_id='A'):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, typ_rep_id='A')
                setattr(obj, comprehens_notes[self.indexno], instructi)
                obj.save()
            else:
                obj = models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                )
                setattr(obj, comprehens_notes[self.indexno], instructi)
                obj.save()
        else:
            pass

class OverduInterest(HandleIndexContent):
    '''
               重要逾期利息
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OverduInterest, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07070200','0b07080200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
        accounts = {'0b07070200':'interest_receiv','0b07080200':'dividend_receiv'}
        df, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('单位') | df.iloc[0, :].str.contains('对象')
                                     | df.iloc[0, :].str.contains('项目'))[0])
            balanc_pos = list(np.where(df.iloc[0, :].str.contains('金额') | df.iloc[0, :].str.contains('余额'))[0])
            overdu_time_pos = list(np.where(df.iloc[0, :].str.contains('时间')|df.iloc[0, :].str.contains('账龄'))[0])
            reason_pos = list(np.where(df.iloc[0, :].str.contains('原因'))[0])
            impair_pos = list(np.where(df.iloc[0, :].str.contains('减值'))[0])

            start_row_pos = list(np.where(df.iloc[:, balanc_pos[0]].str.match(r'.*?\d+.*?'))[0])
            data_length = len(df.iloc[start_row_pos[0]:, :])
            names = list(df.iloc[start_row_pos[0]:, name_pos[0]]) if len(name_pos) > 0 else ['' for i in
                                                                                             range(data_length)]
            balancs = list(df.iloc[start_row_pos[0]:, balanc_pos[0]]) if len(balanc_pos) > 0 else ['' for i in
                                                                                                range(data_length)]
            overdu_times = list(df.iloc[start_row_pos[0]:, overdu_time_pos[0]]) if len(overdu_time_pos) > 0 else [0.00 for i in
                                                                                                   range(data_length)]
            reasons = list(df.iloc[start_row_pos[0]:, reason_pos[0]]) if len(
                reason_pos) > 0 else [0.00 for i in range(data_length)]
            impairs = list(df.iloc[start_row_pos[0]:, impair_pos[0]]) if len(impair_pos) > 0 else ['' for i in
                                                                                          range(data_length)]

            for (name, balanc, overdu_time, reason, impair) in \
                    zip(names, balancs, overdu_times, reasons, impairs):
                if models.OverduInterest.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                    subject=accounts[self.indexno],typ_rep_id='A',name=name):

                    obj = models.OverduInterest.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            subject=accounts[self.indexno], typ_rep_id='A', name=name)
                    obj.balanc = Decimal(re.sub(',', '', str(balanc))) * unit_change[unit] if is_num(balanc) else 0.00
                    obj.overdu_time = overdu_time
                    obj.reason = reason
                    obj.impair = impair
                    obj.save()
                else:
                    obj = models.OverduInterest.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        subject=accounts[self.indexno],
                        name=name,
                        balanc=Decimal(re.sub(',', '', str(balanc))) * unit_change[
                            unit] if is_num(balanc) else 0.00,
                        overdu_time=overdu_time,
                        reason=reason,
                        impair=impair,
                    )

class InventoriImpairPrepar(HandleIndexContent):
    '''
                   存货跌价准备
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(InventoriImpairPrepar, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b070a0200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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

            names = list(df.iloc[2:, 0])
            befores = list(df.iloc[2:, 1])
            accruals = list(df.iloc[2:, 2])
            other_increass = list(df.iloc[2:, 3])
            transferback_resels = list(df.iloc[2:, 4])
            other_cut_backs = list(df.iloc[2:, 5])
            ends = list(df.iloc[2:, 6])

            for (name, before, accrual, other_increas, transferback_resel,other_cut_back,end) in \
                    zip(names, befores, accruals, other_increass, transferback_resels,other_cut_backs,ends):
                if models.InventoriImpairPrepar.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                         typ_rep_id='A', name=name):

                    obj = models.InventoriImpairPrepar.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                             typ_rep_id='A', name=name)
                    obj.before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00
                    obj.accrual = Decimal(re.sub(',', '', str(accrual))) * unit_change[unit] if is_num(accrual) else 0.00
                    obj.other_increas = Decimal(re.sub(',', '', str(other_increas))) * unit_change[unit] if is_num(other_increas) else 0.00
                    obj.transferback_resel = Decimal(re.sub(',', '', str(transferback_resel))) * unit_change[unit] if is_num(transferback_resel) else 0.00
                    obj.other_cut_back = Decimal(re.sub(',', '', str(other_cut_back))) * unit_change[unit] if is_num(other_cut_back) else 0.00
                    obj.end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00
                    obj.save()
                else:
                    obj = models.InventoriImpairPrepar.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00,
                        accrual = Decimal(re.sub(',', '', str(accrual))) * unit_change[unit] if is_num(accrual) else 0.00,
                        other_increas = Decimal(re.sub(',', '', str(other_increas))) * unit_change[unit] if is_num(other_increas) else 0.00,
                        transferback_resel = Decimal(re.sub(',', '', str(transferback_resel))) * unit_change[unit] if is_num(transferback_resel) else 0.00,
                        other_cut_back = Decimal(re.sub(',', '', str(other_cut_back))) * unit_change[unit] if is_num(other_cut_back) else 0.00,
                        end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00,
                    )

class InventoriCapitOfBorrowCost(HandleIndexContent):
    '''
                   存货年末余额中含有借款费用资本化金额
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(InventoriCapitOfBorrowCost, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b070a0300']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
        pattern = re.compile('^.*?借款费用资本化金额.*?(\d+.*?\.{0,1}\d*?)(.*?元).*?$')
        if len(instructi) > 0 and pattern.match(instructi):
            inventori_capit_of_borrow_cost = pattern.match(instructi).groups()[0]
            unit = pattern.match(instructi).groups()[1]
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,typ_rep_id='A'):

                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,typ_rep_id='A')
                obj.inventori_capit_of_borrow_cost = Decimal(re.sub(',', '', str(inventori_capit_of_borrow_cost))) * unit_change[unit] \
                    if is_num(inventori_capit_of_borrow_cost) else 0.00
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    inventori_capit_of_borrow_cost=Decimal(re.sub(',', '', str(inventori_capit_of_borrow_cost))) * unit_change[unit] \
                        if is_num(inventori_capit_of_borrow_cost) else 0.00,

                )
        else:
            pass

class ConstructContract(HandleIndexContent):
    '''
       建造合同形成的已完工未结算资产情况、建造合同形成的已结算未完工项目情况
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ConstructContract, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b070a0400','0b07240300']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
        accounts = {'0b070a0400':'i','0b07240300':'a'}
        df, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            cost_pos = list(np.where(df.iloc[:,0].str.contains('成本'))[0])
            gross_profit_pos = list(np.where(df.iloc[:,0].str.contains('毛利'))[0])
            expect_loss_pos = list(np.where(df.iloc[:,0].str.contains('预计损失'))[0])
            project_settlement_pos = list(np.where(df.iloc[:,0].str.contains('已办理结算'))[0])
            complet_settl_pos = list(np.where(df.iloc[:,0].str.contains('建造合同'))[0])

            cost = df.iloc[cost_pos[0], 1]
            gross_profit = df.iloc[gross_profit_pos[0], 1]
            expect_loss = df.iloc[expect_loss_pos[0], 1]
            project_settlement = df.iloc[project_settlement_pos[0], 1]
            complet_settl = df.iloc[complet_settl_pos[0], 1]

            if models.ConstructContract.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           typ_rep_id='A',subject=accounts[self.indexno]):
                obj = models.ConstructContract.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                               typ_rep_id='A',subject=accounts[self.indexno])
                obj.cost = Decimal(re.sub(',', '', str(cost))) * unit_change[unit] if is_num(cost) else 0.00
                obj.gross_profit = Decimal(re.sub(',', '', str(gross_profit))) * unit_change[unit] if is_num(
                    gross_profit) else 0.00
                obj.expect_loss = Decimal(re.sub(',', '', str(expect_loss))) * unit_change[unit] if is_num(
                    expect_loss) else 0.00
                obj.project_settlement = Decimal(re.sub(',', '', str(project_settlement))) * unit_change[
                    unit] if is_num(project_settlement) else 0.00
                obj.complet_settl = Decimal(re.sub(',', '', str(complet_settl))) * unit_change[unit] if is_num(
                    complet_settl) else 0.00
                obj.save()
            else:
                obj = models.ConstructContract.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    subject=accounts[self.indexno],
                    cost=Decimal(re.sub(',', '', str(cost))) * unit_change[unit] if is_num(cost) else 0.00,
                    gross_profit=Decimal(re.sub(',', '', str(gross_profit))) * unit_change[unit] if is_num(
                        gross_profit) else 0.00,
                    expect_loss=Decimal(re.sub(',', '', str(expect_loss))) * unit_change[unit] if is_num(
                        expect_loss) else 0.00,
                    project_settlement=Decimal(re.sub(',', '', str(project_settlement))) * unit_change[
                        unit] if is_num(project_settlement) else 0.00,
                    complet_settl=Decimal(re.sub(',', '', str(complet_settl))) * unit_change[unit] if is_num(
                        complet_settl) else 0.00,
                )

class LongtermEquitiInvest(HandleIndexContent):
    '''
           长期股权投资
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(LongtermEquitiInvest, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = []
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07110000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                                dfs.append(df)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
        instructi = re.sub('其他说明','', instructi)
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if len(dfs)==3 :
            df_com = {}
            df_com['joint_ventur'] = dfs[1]
            df_com['pool'] = dfs[2]
            for key,df in df_com.items():
                df = df[~df.iloc[:,0].str.contains('小计')]
                df = df[~df.iloc[:, 0].str.contains('合计')]
                if len(df)>0:
                    names = list(df.iloc[:,0])
                    befores = list(df.iloc[:,1])
                    addit_invests = list(df.iloc[:,2])
                    reduc_invests = list(df.iloc[:,3])
                    invest_gain_and_losss = list(df.iloc[:,4])
                    other_comprehens_incs = list(df.iloc[:,5])
                    chang_in_other_equits = list(df.iloc[:,6])
                    cash_dividend_or_pros = list(df.iloc[:,7])
                    provis_for_impairs = list(df.iloc[:,8])
                    others = list(df.iloc[:,9])
                    ends = list(df.iloc[:,10])
                    impair_balancs = list(df.iloc[:,11])

                    for (name,before,addit_invest,reduc_invest,invest_gain_and_loss,other_comprehens_inc,
                            chang_in_other_equit,cash_dividend_or_pro,provis_for_impair,other,end,impair_balanc) in \
                        zip(names,befores,addit_invests,reduc_invests,invest_gain_and_losss,other_comprehens_incs,
                            chang_in_other_equits,cash_dividend_or_pros,provis_for_impairs,others,ends,impair_balancs):
                        print(key,name)
                        if models.LongtermEquitiInvest.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                   typ_rep_id='A',name=name):
                            obj = models.LongtermEquitiInvest.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                       typ_rep_id='A',name=name)
                            obj.com_type = key
                            obj.before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00
                            obj.addit_invest = Decimal(re.sub(',', '', str(addit_invest))) * unit_change[unit] if is_num(addit_invest) else 0.00
                            obj.reduc_invest = Decimal(re.sub(',', '', str(reduc_invest))) * unit_change[unit] if is_num(reduc_invest) else 0.00
                            obj.invest_gain_and_loss = Decimal(re.sub(',', '', str(invest_gain_and_loss))) * unit_change[unit] if is_num(invest_gain_and_loss) else 0.00
                            obj.other_comprehens_inc = Decimal(re.sub(',', '', str(other_comprehens_inc))) * unit_change[unit] if is_num(other_comprehens_inc) else 0.00
                            obj.chang_in_other_equit = Decimal(re.sub(',', '', str(chang_in_other_equit))) * unit_change[unit] if is_num(chang_in_other_equit) else 0.00
                            obj.cash_dividend_or_pro = Decimal(re.sub(',', '', str(cash_dividend_or_pro))) * unit_change[unit] if is_num(cash_dividend_or_pro) else 0.00
                            obj.provis_for_impair = Decimal(re.sub(',', '', str(provis_for_impair))) * unit_change[unit] if is_num(provis_for_impair) else 0.00
                            obj.other = Decimal(re.sub(',', '', str(other))) * unit_change[unit] if is_num(other) else 0.00
                            obj.end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00
                            obj.impair_balanc = Decimal(re.sub(',', '', str(impair_balanc))) * unit_change[unit] if is_num(impair_balanc) else 0.00

                            obj.save()
                        else:
                            models.LongtermEquitiInvest.objects.create(
                                stk_cd_id=self.stk_cd_id,
                                acc_per=self.acc_per,
                                typ_rep_id='A',
                                name=name,
                                com_type=key,
                                before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(
                                    before) else 0.00,
                                addit_invest = Decimal(re.sub(',', '', str(addit_invest))) * unit_change[unit] if is_num(
                                    addit_invest) else 0.00,
                                reduc_invest = Decimal(re.sub(',', '', str(reduc_invest))) * unit_change[unit] if is_num(
                                    reduc_invest) else 0.00,
                                invest_gain_and_loss = Decimal(re.sub(',', '', str(invest_gain_and_loss))) * unit_change[
                                    unit] if is_num(invest_gain_and_loss) else 0.00,
                                other_comprehens_inc = Decimal(re.sub(',', '', str(other_comprehens_inc))) * unit_change[
                                    unit] if is_num(other_comprehens_inc) else 0.00,
                                chang_in_other_equit = Decimal(re.sub(',', '', str(chang_in_other_equit))) * unit_change[
                                    unit] if is_num(chang_in_other_equit) else 0.00,
                                cash_dividend_or_pro = Decimal(re.sub(',', '', str(cash_dividend_or_pro))) * unit_change[
                                    unit] if is_num(cash_dividend_or_pro) else 0.00,
                                provis_for_impair = Decimal(re.sub(',', '', str(provis_for_impair))) * unit_change[
                                    unit] if is_num(provis_for_impair) else 0.00,
                                other = Decimal(re.sub(',', '', str(other))) * unit_change[unit] if is_num(other) else 0.00,
                                end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00,
                                impair_balanc = Decimal(re.sub(',', '', str(impair_balanc))) * unit_change[unit] if is_num(impair_balanc) else 0.00,
                            )
        else:
            pass

        if len(instructi) > 1:
            if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,typ_rep_id='A'):
                obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,typ_rep_id='A')
                obj.longterm_equiti_invest_desc = instructi
                obj.save()
            else:
                models.ComprehensNote.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    longterm_equiti_invest_desc=instructi
                )
        else:
            pass

class FixAsset(HandleIndexContent):
    '''
               固定资产、无形资产
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(FixAsset, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07130100','0b07190100']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
        asset_types = {'0b07130100':'f','0b07190100':'i'}
        df, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df)>0:
            items = list(df.iloc[0,:])
            origin_pos = list(np.where(df.iloc[:, 0].str.contains('账面原值'))[0])
            depreci_pos = list(np.where(df.iloc[:, 0].str.contains('累计折旧')|df.iloc[:, 0].str.contains('累计摊销'))[0])
            impair_pos = list(np.where(df.iloc[:, 0].str.contains('减值准备'))[0])
            value_pos = list(np.where(df.iloc[:, 0].str.contains('四、账面价值'))[0])
            df_origin = df.iloc[origin_pos[0]:depreci_pos[0],:]
            df_depreci = df.iloc[depreci_pos[0]:impair_pos[0],:]
            df_impair = df.iloc[impair_pos[0]:value_pos[0],:]
            df_value = df.iloc[value_pos[0]:,:]
            dfs = {'o':df_origin,'a':df_depreci,'i':df_impair}



            for key,item in enumerate(items):
                if key == 0:
                    continue

                if models.FixAndIntangAssetType.objects.filter(name=item):
                    obj_asset_type = models.FixAndIntangAssetType.objects.get(name=item)
                else:
                    obj_asset_type = models.FixAndIntangAssetType.objects.create(name=item)


                for valu_categori,df in dfs.items():
                    before_pos = list(np.where(df.iloc[:, 0].str.contains('期初'))[0])
                    increas_pos = list(np.where(df.iloc[:, 0].str.contains('增加'))[0])
                    cut_back_pos = list(np.where(df.iloc[:, 0].str.contains('减少'))[0])
                    end_pos = list(np.where(df.iloc[:, 0].str.contains('期末'))[0])

                    before_type = [df.iloc[before_pos[0],0]]
                    increases_types = list(df.iloc[increas_pos[0]:cut_back_pos[0],0])
                    cut_backs_types = list(df.iloc[cut_back_pos[0]:end_pos[0],0])
                    end_type = [df.iloc[end_pos[0], 0]]

                    sub_pattern = re.compile('[\.\d\(\)（）]')
                    before_type = [re.sub(sub_pattern,'',s) for s in before_type]
                    increases_types = [re.sub(sub_pattern,'',s) for s in increases_types]
                    cut_backs_types = [re.sub(sub_pattern,'',s) for s in cut_backs_types]
                    end_type = [re.sub(sub_pattern,'',s) for s in end_type]


                    before = [df.iloc[before_pos[0], key]]
                    increases = list(df.iloc[increas_pos[0]: cut_back_pos[0],key])
                    cut_backs = list(df.iloc[cut_back_pos[0]: end_pos[0], key])
                    end = [df.iloc[end_pos[0], key]]

                    all_dicts = {'b':list(zip(before_type,before)),'i':list(zip(increases_types,increases)),
                    'c':list(zip(cut_backs_types,cut_backs)),'e':list(zip(end_type,end))}
                    for attr in all_dicts:
                        for increas_cut_back_type,value in all_dicts[attr]:

                            if models.FixAndIntangChangeType.objects.filter(name=increas_cut_back_type):
                                obj_change_type = models.FixAndIntangChangeType.objects.get(name=increas_cut_back_type)
                            else:
                                obj_change_type = models.FixAndIntangChangeType.objects.create(name=increas_cut_back_type)

                            value = Decimal(re.sub(',', '', str(value))) * unit_change[unit] \
                                if is_num(value) else 0.00
                            if models.FixAsset.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                          typ_rep_id='A', asset_type=asset_types[self.indexno],valu_categori=valu_categori,
                                                              item_id=obj_asset_type.id,increas_cut_back_type_id=obj_change_type.id,amount_type=attr
                                                              ):
                                obj = models.FixAsset.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,
                                                                              typ_rep_id='A',asset_type=asset_types[self.indexno],valu_categori=valu_categori,
                                                              item_id=obj_asset_type.id,increas_cut_back_type_id=obj_change_type.id,amount_type=attr)
                                obj.amount = value
                                obj.save()
                            else:
                                models.FixAsset.objects.create(
                                    stk_cd_id=self.stk_cd_id,
                                    acc_per=self.acc_per,
                                    typ_rep_id='A',
                                    asset_type=asset_types[self.indexno],
                                    valu_categori=valu_categori,
                                    item_id=obj_asset_type.id,
                                    increas_cut_back_type_id=obj_change_type.id,
                                    amount_type=attr,
                                    amount=value,
                                )


            for key, item in enumerate(items):
                if key == 0:
                    continue

                if models.FixAndIntangAssetType.objects.filter(name=item):
                    obj_asset_type = models.FixAndIntangAssetType.objects.get(name=item)
                else:
                    obj_asset_type = models.FixAndIntangAssetType.objects.create(name=item)

                before_pos = list(np.where(df_value.iloc[:, 0].str.contains('期初')|df_value.iloc[:, 0].str.contains('年初'))[0])
                end_pos = list(np.where(df_value.iloc[:, 0].str.contains('期末')|df_value.iloc[:, 0].str.contains('年末'))[0])
                before = [df_value.iloc[before_pos[0], key]]
                end = [df_value.iloc[end_pos[0], key]]
                before_type = [df_value.iloc[before_pos[0], 0]]
                end_type = [df_value.iloc[end_pos[0], 0]]

                sub_pattern = re.compile('[\.\d\(\)（）]')
                before_type = [re.sub(sub_pattern, '', s) for s in before_type]
                end_type = [re.sub(sub_pattern, '', s) for s in end_type]

                all_dicts = {'b': list(zip(before_type, before)),'e': list(zip(end_type, end))}
                for attr in all_dicts:
                    for increas_cut_back_type, value in all_dicts[attr]:

                        if models.FixAndIntangChangeType.objects.filter(name=increas_cut_back_type):
                            obj_change_type = models.FixAndIntangChangeType.objects.get(name=increas_cut_back_type)
                        else:
                            obj_change_type = models.FixAndIntangChangeType.objects.create(name=increas_cut_back_type)

                        value = Decimal(re.sub(',', '', str(value))) * unit_change[unit] \
                            if is_num(value) else 0.00
                        if models.FixAsset.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          typ_rep_id='A', valu_categori='n', asset_type=asset_types[self.indexno],\
                                                          item_id=obj_asset_type.id, increas_cut_back_type_id=obj_change_type.id,amount_type=attr
                                                          ):
                            obj = models.FixAsset.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              typ_rep_id='A', valu_categori='n', asset_type=asset_types[self.indexno], \
                                                              item_id=obj_asset_type.id, increas_cut_back_type_id=obj_change_type.id, amount_type=attr)

                            obj.amount = value
                            obj.save()
                        else:
                            obj = models.FixAsset.objects.create(
                                stk_cd_id=self.stk_cd_id,
                                acc_per=self.acc_per,
                                typ_rep_id='A',
                                valu_categori='n',
                                asset_type=asset_types[self.indexno],
                                item_id=obj_asset_type.id,
                                increas_cut_back_type_id=obj_change_type.id,
                                amount_type=attr,
                                amount=value
                            )
        else:
            pass

        if self.indexno == '0b07190100' and len(instructi)>1:
            pattern = re.compile('^.*?内部研发形成的无形资产占无形资产余额的比例(.*?)%.*?$')
            if pattern.match(instructi):
                rd_intang_asset_per = pattern.match(instructi).groups()[0]
                if models.ComprehensNote.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,typ_rep_id='A' ):

                    obj = models.ComprehensNote.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,typ_rep_id='A' )

                    obj.rd_intang_asset_per = Decimal(re.sub(',', '', str(rd_intang_asset_per))) * \
                                                         unit_change[unit] \
                        if is_num(rd_intang_asset_per) else 0.00
                    obj.save()
                else:
                    models.ComprehensNote.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        rd_intang_asset_per=Decimal(re.sub(',', '', str(rd_intang_asset_per))) *
                                                       unit_change[unit] \
                            if is_num(rd_intang_asset_per) else 0.00,

                    )
        else:
            pass

class FixAssetStatu(HandleIndexContent):
    '''
                   固定资产状态
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(FixAssetStatu, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07130200','0b07130300','0b07130400']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
        status_dict = {'0b07130200':'i','0b07130300':'f','0b07130400':'b'}
        df, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            item_pos = list(np.where(df.iloc[0,:].str.contains('项目'))[0])
            origin_pos = list(np.where(df.iloc[0,:].str.contains('账面原值'))[0])
            depreci_pos = list(np.where(df.iloc[0,:].str.contains('累计折旧'))[0])
            impair_pos = list(np.where(df.iloc[0,:].str.contains('减值准备'))[0])
            value_pos = list(np.where(df.iloc[0,:].str.contains('账面价值'))[0])
            instruct_pos = list(np.where(df.iloc[0,:].str.contains('备注'))[0])
            print(value_pos)
            items = list(df.iloc[1:,item_pos[0]]) if len(item_pos)>0 else  ['' for i in range(len(df)-1)]
            origins = list(df.iloc[1:,origin_pos[0]]) if len(origin_pos)>0 else  [0.00 for i in range(len(df)-1)]
            deprecis = list(df.iloc[1:,depreci_pos[0]]) if len(depreci_pos)>0 else  [0.00 for i in range(len(df)-1)]
            impairs = list(df.iloc[1:,impair_pos[0]]) if len(impair_pos)>0 else  [0.00 for i in range(len(df)-1)]
            values = list(df.iloc[1:,value_pos[0]]) if len(value_pos)>0 else  [0.00 for i in range(len(df)-1)]
            instructs = list(df.iloc[1:,instruct_pos[0]]) if len(instruct_pos)>0 else  ['' for i in range(len(df)-1)]

            all_dict = {'o':origins,'a':deprecis,'i':impairs,'n':values}
            print(all_dict)
            for valu_categori,amounts in all_dict.items():
                for key, item in enumerate(items):

                    if models.FixAndIntangAssetType.objects.filter(name=item):
                        obj_asset_type = models.FixAndIntangAssetType.objects.get(name=item)
                    else:
                        obj_asset_type = models.FixAndIntangAssetType.objects.create(name=item)

                    value = amounts[key]
                    value = Decimal(re.sub(',', '', str(value))) * unit_change[unit] \
                        if is_num(value) else 0.00
                    if models.FixAssetStatu.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                      typ_rep_id='A', valu_categori=valu_categori,
                                                      item_id=obj_asset_type.id, status=status_dict[self.indexno],
                                                      ):
                        obj = models.FixAssetStatu.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          typ_rep_id='A', valu_categori=valu_categori,
                                                          item_id=obj_asset_type.id,status=status_dict[self.indexno],
                                                         )
                        obj.amount = value
                        obj.instruct = instructs[key]
                        obj.save()
                    else:
                        models.FixAssetStatu.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            typ_rep_id='A',
                            valu_categori=valu_categori,
                            item_id=obj_asset_type.id,
                            status=status_dict[self.indexno],
                            amount=value,
                            instruct=instructs[key]
                        )

class UnfinishProperti(HandleIndexContent):
    '''
                      未办妥产权状态
                  '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(UnfinishProperti, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07130500','0b07190200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
        asset_dict = {'0b07130500': 'f','0b07190200':'i'}
        df, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if df is not None and len(df) > 1:
            item_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            value_pos = list(np.where(df.iloc[0, :].str.contains('账面价值'))[0])
            reason_pos = list(np.where(df.iloc[0, :].str.contains('未办妥产权'))[0])

            items = df.iloc[1:, item_pos[0]] if len(item_pos) > 0 else ['' for i in range(len(df) - 1)]
            values = df.iloc[1:, value_pos[0]] if len(value_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            reasons = df.iloc[1:, reason_pos[0]] if len(reason_pos) > 0 else ['' for i in range(len(df) - 1)]

            for (item,value,reason) in zip(items,values,reasons):
                value = Decimal(re.sub(',', '', str(value))) * unit_change[unit] \
                    if is_num(value) else 0.00
                if models.UnfinishProperti.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       typ_rep_id='A', asset_categori=asset_dict[self.indexno],
                                                       item=item,
                                                       ):
                    obj = models.UnfinishProperti.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           typ_rep_id='A', asset_categori=asset_dict[self.indexno],
                                                           item=item
                                                           )
                    obj.amount = value
                    obj.reason = reason
                    obj.save()
                else:
                    models.UnfinishProperti.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        asset_categori=asset_dict[self.indexno],
                        item=item,
                        amount=value,
                        reason=reason
                    )

class ImportProjectChange(HandleIndexContent):
    '''
          重要在建工程项目本期变动情况
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ImportProjectChange, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07140200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            budget_pos = list(np.where(df.iloc[0, :].str.contains('预算数'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            increas_pos = list(np.where(df.iloc[0, :].str.contains('增加'))[0])
            transfer_to_fix_asset_pos = list(np.where(df.iloc[0, :].str.contains('固定资产'))[0])
            other_reduct_pos = list(np.where(df.iloc[0, :].str.contains('其他减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])
            percentag_of_budget_pos = list(np.where(df.iloc[0, :].str.contains('占预算比例'))[0])
            progress_pos = list(np.where(df.iloc[0, :].str.contains('工程进度'))[0])
            interest_capit_cumul_amount_pos = list(np.where(df.iloc[0, :].str.contains('利息资本化累计金额'))[0])
            interest_capit_current_amount_pos = list(np.where(df.iloc[0, :].str.contains('本期利息资本化金额'))[0])
            interest_capit_rate_pos = list(np.where(df.iloc[0, :].str.contains('利息资本化率'))[0])
            sourc_of_fund_pos = list(np.where(df.iloc[0, :].str.contains('资金来源'))[0])

            names = df.iloc[1:, name_pos[0]] if len(name_pos) > 0 else ['' for i in range(len(df) - 1)]
            budgets = df.iloc[1:, budget_pos[0]] if len(budget_pos) > 0 else ['' for i in range(len(df) - 1)]
            befores = df.iloc[1:, before_pos[0]] if len(before_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            increass = df.iloc[1:, increas_pos[0]] if len(increas_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            transfer_to_fix_assets = df.iloc[1:, transfer_to_fix_asset_pos[0]] if len(transfer_to_fix_asset_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            other_reducts = df.iloc[1:, other_reduct_pos[0]] if len(other_reduct_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            ends = df.iloc[1:, end_pos[0]] if len(end_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            percentag_of_budgets = df.iloc[1:, percentag_of_budget_pos[0]] if len(percentag_of_budget_pos) > 0 else ['' for i in range(len(df) - 1)]
            progresss = df.iloc[1:, progress_pos[0]] if len(progress_pos) > 0 else ['' for i in range(len(df) - 1)]
            interest_capit_cumul_amounts = df.iloc[1:, interest_capit_cumul_amount_pos[0]] if len(interest_capit_cumul_amount_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            interest_capit_current_amounts = df.iloc[1:, interest_capit_current_amount_pos[0]] if len(interest_capit_current_amount_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            interest_capit_rates = df.iloc[1:, interest_capit_rate_pos[0]] if len(interest_capit_rate_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            sourc_of_funds = df.iloc[1:, sourc_of_fund_pos[0]] if len(sourc_of_fund_pos) > 0 else ['' for i in range(len(df) - 1)]

            for (name,budget,before,increas,transfer_to_fix_asset,other_reduct,end,percentag_of_budget,progress, \
                        interest_capit_cumul_amount, interest_capit_current_amount,interest_capit_rate,sourc_of_fund) in \
                    zip(names,budgets,befores,increass,transfer_to_fix_assets,other_reducts,ends,percentag_of_budgets,progresss, \
                        interest_capit_cumul_amounts, interest_capit_current_amounts,interest_capit_rates,sourc_of_funds):

                if models.ImportProjectChange.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       typ_rep_id='A',name=name
                                                       ):
                    obj = models.ImportProjectChange.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           typ_rep_id='A', name=name
                                                           )
                    obj.name=name
                    obj.budget=budget
                    obj.before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00
                    obj.increas = Decimal(re.sub(',', '', str(increas))) * unit_change[unit] if is_num(increas) else 0.00
                    obj.transfer_to_fix_asset = Decimal(re.sub(',', '', str(transfer_to_fix_asset))) * unit_change[unit] if is_num(transfer_to_fix_asset) else 0.00
                    obj.other_reduct = Decimal(re.sub(',', '', str(other_reduct))) * unit_change[unit] if is_num(other_reduct) else 0.00
                    obj.end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00
                    obj.percentag_of_budget = percentag_of_budget
                    obj.progress = progress
                    obj.interest_capit_cumul_amount = Decimal(re.sub(',', '', str(interest_capit_cumul_amount))) * unit_change[unit] if is_num(interest_capit_cumul_amount) else 0.00
                    obj.interest_capit_current_amount = Decimal(re.sub(',', '', str(interest_capit_current_amount))) * unit_change[unit] if is_num(interest_capit_current_amount) else 0.00
                    obj.interest_capit_rate = Decimal(re.sub(',', '', str(interest_capit_rate))) * unit_change[unit] if is_num(interest_capit_rate) else 0.00
                    obj.sourc_of_fund = sourc_of_fund

                    obj.save()
                else:
                    models.ImportProjectChange.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        budget=budget,
                        before=Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00,
                        increas=Decimal(re.sub(',', '', str(increas))) * unit_change[unit] if is_num(increas) else 0.00,
                        transfer_to_fix_asset=Decimal(re.sub(',', '', str(transfer_to_fix_asset))) * unit_change[
                            unit] if is_num(transfer_to_fix_asset) else 0.00,
                        other_reduct=Decimal(re.sub(',', '', str(other_reduct))) * unit_change[unit] if is_num(
                            other_reduct) else 0.00,
                        end=Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00,
                        percentag_of_budget=percentag_of_budget,
                        progress=progress,
                        interest_capit_cumul_amount=Decimal(re.sub(',', '', str(interest_capit_cumul_amount))) *
                                                    unit_change[unit] if is_num(interest_capit_cumul_amount) else 0.00,
                        interest_capit_current_amount=Decimal(re.sub(',', '', str(interest_capit_current_amount))) *
                                                      unit_change[unit] if is_num(
                            interest_capit_current_amount) else 0.00,
                        interest_capit_rate=Decimal(re.sub(',', '', str(interest_capit_rate))) * unit_change[
                            unit] if is_num(interest_capit_rate) else 0.00,
                        sourc_of_fund=sourc_of_fund

                    )


class DevelopExpenditur(HandleIndexContent):
    '''
          开发支出
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DevelopExpenditur, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b071a0000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            increas_pos = list(np.where(df.iloc[0, :].str.contains('增加'))[0])
            cut_back_pos = list(np.where(df.iloc[0, :].str.contains('减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])
            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(np.where(df.iloc[:, end_pos[0]].str.match(pattern)|df.iloc[:, end_pos[0]].str.match(r'nan'))[0])

            names = df.iloc[start_pos[0]:, name_pos[0]] if len(name_pos) > 0 else ['' for i in range(len(df) - 1)]
            befores = df.iloc[start_pos[0]:, before_pos[0]] if len(before_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            increas_rds = df.iloc[start_pos[0]:, increas_pos[0]] if len(increas_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            increas_others = df.iloc[start_pos[0]:, increas_pos[1]]   if len(increas_pos)> 0 else [0.00 for i in range(len(df) - 1)]
            transfer_to_intang_assets = df.iloc[start_pos[0]:, cut_back_pos[0]] if len(cut_back_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            transfer_to_profits = df.iloc[start_pos[0]:, cut_back_pos[1]] if len(cut_back_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            ends = df.iloc[1:, end_pos[0]] if len(end_pos) > 0 else [0.00 for i in range(len(df) - 1)]

            for (name,before,increas_rd,increas_other,transfer_to_intang_asset,transfer_to_profit,end) in \
                    zip(names,befores,increas_rds,increas_others,transfer_to_intang_assets,transfer_to_profits,ends):

                if models.DevelopExpenditur.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       typ_rep_id='A',name=name
                                                       ):
                    obj = models.DevelopExpenditur.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           typ_rep_id='A', name=name
                                                           )
                    obj.before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00
                    obj.increas_rd = Decimal(re.sub(',', '', str(increas_rd))) * unit_change[unit] if is_num(increas_rd) else 0.00
                    obj.increas_other = Decimal(re.sub(',', '', str(increas_other))) * unit_change[unit] if is_num(increas_other) else 0.00
                    obj.transfer_to_intang_asset = Decimal(re.sub(',', '', str(transfer_to_intang_asset))) * unit_change[unit] if is_num(transfer_to_intang_asset) else 0.00
                    obj.transfer_to_profit = Decimal(re.sub(',', '', str(transfer_to_profit))) * unit_change[unit] if is_num(transfer_to_profit) else 0.00
                    obj.end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00

                    obj.save()
                else:
                    models.DevelopExpenditur.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        before=Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00,
                        increas_rd=Decimal(re.sub(',', '', str(increas_rd))) * unit_change[unit] if is_num(increas_rd) else 0.00,
                        increas_other=Decimal(re.sub(',', '', str(increas_other))) * unit_change[
                            unit] if is_num(increas_other) else 0.00,
                        transfer_to_intang_asset=Decimal(re.sub(',', '', str(transfer_to_intang_asset))) * unit_change[unit] if is_num(
                            transfer_to_intang_asset) else 0.00,
                        transfer_to_profit=Decimal(re.sub(',', '', str(transfer_to_profit))) * unit_change[unit] if is_num(transfer_to_profit) else 0.00,
                        end=Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00,

                    )

class Goodwil(HandleIndexContent):
    '''
          商誉
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(Goodwil, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b071b0100']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
            name_pos = list(np.where(df.iloc[0, :].str.contains('单位名称或形成商誉的事项'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            increas_pos = list(np.where(df.iloc[0, :].str.contains('增加'))[0])
            cut_back_pos = list(np.where(df.iloc[0, :].str.contains('减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])
            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(np.where(df.iloc[:, end_pos[0]].str.match(pattern)|df.iloc[:, end_pos[0]].str.match(r'nan'))[0])

            names = df.iloc[start_pos[0]:, name_pos[0]] if len(name_pos) > 0 else ['' for i in range(len(df) - 1)]
            befores = df.iloc[start_pos[0]:, before_pos[0]] if len(before_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            busi_mergers = df.iloc[start_pos[0]:, increas_pos[0]] if len(increas_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            other_increass = df.iloc[start_pos[0]:, increas_pos[1]]   if len(increas_pos)> 0 else [0.00 for i in range(len(df) - 1)]
            disposs = df.iloc[start_pos[0]:, cut_back_pos[0]] if len(cut_back_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            other_reducts = df.iloc[start_pos[0]:, cut_back_pos[1]] if len(cut_back_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            ends = df.iloc[1:, end_pos[0]] if len(end_pos) > 0 else [0.00 for i in range(len(df) - 1)]

            for (name,before,busi_merger,other_increas,dispos,other_reduct,end) in \
                    zip(names,befores,busi_mergers,other_increass,disposs,other_reducts,ends):

                if models.Goodwil.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       typ_rep_id='A',name=name
                                                       ):
                    obj = models.Goodwil.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           typ_rep_id='A', name=name
                                                           )
                    obj.before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00
                    obj.busi_merger = Decimal(re.sub(',', '', str(busi_merger))) * unit_change[unit] if is_num(busi_merger) else 0.00
                    obj.other_increas = Decimal(re.sub(',', '', str(other_increas))) * unit_change[unit] if is_num(other_increas) else 0.00
                    obj.dispos = Decimal(re.sub(',', '', str(dispos))) * unit_change[unit] if is_num(dispos) else 0.00
                    obj.other_reduct = Decimal(re.sub(',', '', str(other_reduct))) * unit_change[unit] if is_num(other_reduct) else 0.00
                    obj.end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00

                    obj.save()
                else:
                    models.Goodwil.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        before=Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00,
                        busi_merger=Decimal(re.sub(',', '', str(busi_merger))) * unit_change[unit] if is_num(busi_merger) else 0.00,
                        other_increas=Decimal(re.sub(',', '', str(other_increas))) * unit_change[
                            unit] if is_num(other_increas) else 0.00,
                        dispos=Decimal(re.sub(',', '', str(dispos))) * unit_change[unit] if is_num(
                            dispos) else 0.00,
                        other_reduct=Decimal(re.sub(',', '', str(other_reduct))) * unit_change[unit] if is_num(other_reduct) else 0.00,
                        end=Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00,

                    )

class LongtermPrepaidExpens(HandleIndexContent):
    '''
          长期待摊费用
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(LongtermPrepaidExpens, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b071c0000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                df = remove_space_from_df(table)
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('适用.不适用', '', item)
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
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            increas_pos = list(np.where(df.iloc[0, :].str.contains('增加'))[0])
            amort_pos = list(np.where(df.iloc[0, :].str.contains('摊销'))[0])
            other_reduct_pos = list(np.where(df.iloc[0, :].str.contains('减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])
            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(np.where(df.iloc[:, end_pos[0]].str.match(pattern)|df.iloc[:, end_pos[0]].str.match(r'nan'))[0])

            names = df.iloc[start_pos[0]:, name_pos[0]] if len(name_pos) > 0 else ['' for i in range(len(df) - 1)]
            befores = df.iloc[start_pos[0]:, before_pos[0]] if len(before_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            increass = df.iloc[start_pos[0]:, increas_pos[0]] if len(increas_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            amorts = df.iloc[start_pos[0]:, amort_pos[0]]   if len(amort_pos)> 0 else [0.00 for i in range(len(df) - 1)]
            other_reducts = df.iloc[start_pos[0]:, other_reduct_pos[0]] if len(other_reduct_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            ends = df.iloc[1:, end_pos[0]] if len(end_pos) > 0 else [0.00 for i in range(len(df) - 1)]

            for (name,before,increas,amort,other_reduct,end) in \
                    zip(names,befores,increass,amorts,other_reducts,ends):

                if models.LongtermPrepaidExpens.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       typ_rep_id='A',name=name
                                                       ):
                    obj = models.LongtermPrepaidExpens.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           typ_rep_id='A', name=name
                                                           )
                    obj.before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00
                    obj.increas = Decimal(re.sub(',', '', str(increas))) * unit_change[unit] if is_num(increas) else 0.00
                    obj.amort = Decimal(re.sub(',', '', str(amort))) * unit_change[unit] if is_num(amort) else 0.00
                    obj.other_reduct = Decimal(re.sub(',', '', str(other_reduct))) * unit_change[unit] if is_num(other_reduct) else 0.00
                    obj.end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00

                    obj.save()
                else:
                    models.LongtermPrepaidExpens.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        before=Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00,
                        increas=Decimal(re.sub(',', '', str(increas))) * unit_change[unit] if is_num(increas) else 0.00,
                        amort=Decimal(re.sub(',', '', str(amort))) * unit_change[
                            unit] if is_num(amort) else 0.00,
                        other_reduct=Decimal(re.sub(',', '', str(other_reduct))) * unit_change[unit] if is_num(other_reduct) else 0.00,
                        end=Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00,

                    )

class DeferIncomTax(HandleIndexContent):
    '''
                递延所得税资产、递延所得税负债
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DeferIncomTax, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b071d0100','0b071d0200']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('余额').any():
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
        accounts = {'0b071d0100': 'a', '0b071d0200': 'd'}
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}

        if df is not None and len(df) > 1:

            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])
            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(
                np.where(df.iloc[:, end_pos[0]].str.match(pattern) | df.iloc[:, end_pos[0]].str.match('nan'))[0])

            names = list(df.iloc[start_pos[0]:, 0])
            ends = list(zip(list(df.iloc[start_pos[0]:, 1]), list(df.iloc[start_pos[0]:, 2])))
            befores = list(zip(list(df.iloc[start_pos[0]:, 3]), list(df.iloc[start_pos[0]:, 4])))

            all_dicts = {'e': ends, 'b': befores}
            for item, values in all_dicts.items():
                for name, value in zip(names, values):

                    if models.DeferIncomTaxName.objects.filter(name=name):
                        obj_name = models.DeferIncomTaxName.objects.get(name=name)
                    else:
                        obj_name = models.DeferIncomTaxName.objects.create(name=name)


                    diff, amount = value
                    diff = Decimal(re.sub(',', '', str(diff))) * unit_change[unit] if is_num(diff) else 0.00
                    amount = Decimal(re.sub(',', '', str(amount))) * unit_change[unit] if is_num(amount) else 0.00
                    if models.DeferIncomTax.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                   before_end=item, subject=accounts[self.indexno],
                                                                   typ_rep_id='A', name_id=obj_name.id):
                        obj = models.DeferIncomTax.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                       before_end=item, subject=accounts[self.indexno],
                                                                       typ_rep_id='A', name_id=obj_name.id)

                        obj.diff = diff
                        obj.amount = amount
                        obj.save()
                    else:
                        models.DeferIncomTax.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            before_end=item,
                            subject=accounts[self.indexno],
                            typ_rep_id='A',
                            name_id=obj_name.id,
                            diff=diff,
                            amount=amount,
                        )
        else:
            pass

class PayablEmployeCompens(HandleIndexContent):
    '''
                   应付职工薪酬
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(PayablEmployeCompens, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07250100','0b07250200','0b07250300']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('余额').any():
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
        accounts = {'0b07250100':'p','0b07250200':'short','0b07250300':'set'}
        df, unit, instructi = self.recognize()
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}

        if df is not None and len(df) > 1:

            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            increase_pos = list(np.where(df.iloc[0, :].str.contains('增加'))[0])
            cut_back_pos = list(np.where(df.iloc[0, :].str.contains('减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])

            pattern = re.compile('^.*?\d.*?$')
            start_pos = list(
                np.where(df.iloc[:, end_pos[0]].str.match(pattern) | df.iloc[:, end_pos[0]].str.match('nan'))[0])

            names = list(df.iloc[start_pos[0]:, name_pos[0]])
            befores = list(df.iloc[start_pos[0]:, before_pos[0]])
            increases = list(df.iloc[start_pos[0]:, increase_pos[0]])
            cut_backs = list(df.iloc[start_pos[0]:, cut_back_pos[0]])
            ends = list(df.iloc[start_pos[0]:, end_pos[0]])

            for (name,before,increase,cut_back, end) in zip(names,befores,increases,cut_backs, ends):
                if models.PayablEmployeCompensName.objects.filter(subject=accounts[self.indexno],name=name):
                    obj_name = models.PayablEmployeCompensName.objects.get(subject=accounts[self.indexno],name=name)
                else:
                    obj_name = models.PayablEmployeCompensName.objects.create(subject=accounts[self.indexno],name=name)

                before = Decimal(re.sub(',', '', str(before))) * unit_change[unit] if is_num(before) else 0.00
                increase = Decimal(re.sub(',', '', str(increase))) * unit_change[unit] if is_num(increase) else 0.00
                cut_back = Decimal(re.sub(',', '', str(cut_back))) * unit_change[unit] if is_num(cut_back) else 0.00
                end = Decimal(re.sub(',', '', str(end))) * unit_change[unit] if is_num(end) else 0.00
                if models.PayablEmployeCompens.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       typ_rep_id='A', name_id=obj_name.id):
                    obj = models.PayablEmployeCompens.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           typ_rep_id='A', name_id=obj_name.id)

                    obj.before = before
                    obj.increase = increase
                    obj.cut_back = cut_back
                    obj.end = end
                    obj.save()
                else:
                    models.PayablEmployeCompens.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        before=before,
                        increase=increase,
                        cut_back=cut_back,
                        end=end,
                    )
        else:
            pass


