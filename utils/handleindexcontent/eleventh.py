# _author : litufu
# date : 2018/5/1

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import re
import numpy as np
import logging
from config.fs import manage_config
import jieba
from collections import OrderedDict
from itertools import chain
import pandas as pd
from log.logs import setup_logging
from utils.handleindexcontent.commons import save_combine_instructi,save_instructi,recognize_instucti,\
    get_values,compute_start_pos,recognize_df_and_instucti,get_dfs
from utils.handleindexcontent.base import HandleIndexContent,get_subject_obj,create_and_update
from utils.mytools import remove_space_from_df,remove_per_from_df,similar,get_item_in_df_pos,\
num_to_decimal,cnToEn,combine_table_to_first
from report_data_extract import models

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
        value_dict = dict(
            stk_cd_id=self.stk_cd_id,
            acc_per=self.acc_per,
            type_of_opinion=type_of_opinion,
            date=date,
            report_num=report_num,
            full_text=instructi,
            opinion=opinion,
        )
        create_and_update("AuditReport",**value_dict)

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
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    audit_report_id=obj.id,
                    title=title,
                    matter_descript=matter_descript,
                    audit_respons=audit_respons,
                )
                create_and_update('KeySegment',**value_dict)

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

                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        audit_report_id=obj.id,
                        title=title,
                        matter_descript=matter_descript,
                        audit_respons=audit_respons,
                    )
                    create_and_update("KeySegment",**value_dict)

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
                                    if get_item_in_df_pos('中国注册会计师',table) is None:
                                        df = remove_per_from_df(remove_space_from_df(table))
                                        dfs.append(df)
                                    instructi.append(table.to_string())
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
        dfs,instructi,audit_df = self.recognize()
        instructi = re.sub('\s+','',instructi)
        opinions = []
        patt2 = re.compile('^.*?(....年.{1,2}月.{1,3}日).*?$')
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
        if patt2.match(instructi) and len(patt2.match(instructi).groups())==1:
            date = patt2.match(instructi).groups()[0]
        else:
            if audit_df is not None:
                date_pos = list(np.where(audit_df.iloc[:,0].str.contains('审计报告签署日期'))[0])
                date = audit_df.iloc[date_pos[0],1]
            else:
                raise Exception


        if patt3.match(instructi) and len(patt3.match(instructi).groups())==1:
            report_num = patt3.match(instructi).groups()[0]
        else:
            if audit_df is not None:
                report_num_pos = list(np.where(audit_df.iloc[:,0].str.contains('审计报告文号'))[0])
                report_num = audit_df.iloc[report_num_pos[0],1]
            else:
                raise Exception
        value_dict = dict(
            stk_cd_id=self.stk_cd_id,
            acc_per=self.acc_per,
            type_of_opinion=type_of_opinion,
            date=date,
            report_num=report_num,
            full_text=instructi,
            opinion=opinion,
        )
        create_and_update('AuditReport',**value_dict)

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

                title = None
                if pattern0.match(desc):
                    title = re.sub(pattern3,'', pattern0.match(desc).groups()[0])
                elif pattern1.match(desc):
                    title = re.sub(pattern3,'', pattern1.match(desc).groups()[0])
                else:
                    pass

                if title is not None:
                    matter_descripts.append(matter_descript)
                    audit_responses.append(audit_respons)
                    titles.append(title)

            report_obj = models.AuditReport.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,report_num=report_num)
            for (title, matter_descript, audit_respons) \
                    in zip(titles, matter_descripts, audit_responses):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    audit_report_id=report_obj.id,
                    title=title,
                    matter_descript=matter_descript,
                    audit_respons=audit_respons,
                )
                create_and_update('KeySegment',**value_dict)
        else:
            pattern4 = re.compile('.*?关键审计事项(.*?)[四五六七]、.*?')
            if pattern4.match(instructi) is not None:
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
                        value_dict = dict(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            audit_report_id=obj.id,
                            title=title,
                            matter_descript=matter_descript,
                            audit_respons=audit_respons,
                        )
                        create_and_update('KeySegment',**value_dict)

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
        pattern0 = re.compile('^.*?公司.*?单位：(.{0,2}元).*?$')
        pattern1= re.compile('^.*?单位：(.{0,2}元).*?$')
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
                        begin = num_to_decimal(df.iloc[i, begin_pos[0]],unit)
                        end = num_to_decimal(df.iloc[i, end_pos[0]],unit)
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
                                begin = num_to_decimal(df.iloc[i, begin_pos[0]],unit)
                                end = num_to_decimal(df.iloc[i, end_pos[0]],unit)
                                field = pp_df_dict[new_subject]
                                begins[field] = begin
                                ends[field] = end
                            else:
                                print('{}科目没有在配置表中'.format(subject))
                        elif patt2.match(subject) and patt2.match(subject).groups()[0] != '':
                            new_subject = patt2.match(subject).groups()[0]
                            if new_subject in pp_df_dict:
                                begin = num_to_decimal(df.iloc[i, begin_pos[0]],unit)
                                end = num_to_decimal(df.iloc[i, end_pos[0]],unit)
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
                obj_begin.check_logic()

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
                obj_end.check_logic()

class CompaniOverview(HandleIndexContent):
    '''
        公司概况
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CompaniOverview, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos=('0b03010000','0b030000')
        pass

    def converse(self):
        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.CompaniBasicSituat, self.stk_cd_id, self.acc_per,'compani_overview')

class ScopeOfMerger(HandleIndexContent):
    '''
            合并范围
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ScopeOfMerger, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ('0b03020000')
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.CompaniBasicSituat, self.stk_cd_id, self.acc_per, 'scope_of_merger')

class SignificAmount(HandleIndexContent):
    '''
        单项金额重大并单独计提坏账准备的应收款项
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(SignificAmount, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b050b0100','0b050b01']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            signific_amount_judgement = df.iloc[0,1]
            signific_amount_withdraw =  df.iloc[1,1]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                signific_amount_judgement=signific_amount_judgement,
                signific_amount_withdraw=signific_amount_withdraw
            )
            create_and_update('CompaniBasicSituat',**value_dict)
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
        logger = logging.getLogger(__name__)
        setup_logging()
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
                        m2 = int(patt_m3.match(k).groups()[0])
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
                        logger.warning('{}账龄分析：{},未匹配,百分比是{}'.format(self.indexno,k,v))

                all_dict[item] = per_dict
                per_dict = {}

        for item in all_dict:
            if models.AgeAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,name=item):
                obj = models.AgeAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,name=item)
                for k,v in all_dict[item].items():
                    setattr(obj,std_dict[k],v)
                obj.save()
            else:
                obj  = models.AgeAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    name=item,
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
        indexnos = ['0b050b0300','0b050b03']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            no_signific_amount_judgement = df.iloc[0,1]
            no_signific_amount_withdraw =  df.iloc[1,1]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                no_signific_amount_judgement=no_signific_amount_judgement,
                no_signific_amount_withdraw=no_signific_amount_withdraw
            )
            create_and_update('CompaniBasicSituat',**value_dict)
        else:
            pass

class DepreciOfFixAssetMethod(HandleIndexContent):
    '''
        固定资产折旧方法
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DepreciOfFixAssetMethod, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b05100200','0b051002']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
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
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    asset_type=asset_type,
                    method=method,
                    years=years,
                    residu_rate=residu_rate,
                    annual_depreci_rate=annual_depreci_rate,
                )
                create_and_update('DepreciOfFixAssetMethod',**value_dict)
        else:
            pass

class RDExpenseAccountPolici(HandleIndexContent):
    '''
                内部研发支出会计政策
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RDExpenseAccountPolici, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ('0b05150200','0b051502')
        pass

    def converse(self):
        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.CompaniBasicSituat, self.stk_cd_id, self.acc_per, 'rd_expense_account_polici')

class IncomeAccountPolici(HandleIndexContent):
    '''
                收入会计政策
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(IncomeAccountPolici, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ('0b051c0000','0b051c00')
        pass

    def converse(self):
        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.CompaniBasicSituat, self.stk_cd_id, self.acc_per, 'income_account_polici')

class ChangInAccountEstim(HandleIndexContent):
    '''
                    会计估计变更
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInAccountEstim, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ('0b05210200','0b052102')
        pass

    def converse(self):
        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.CompaniBasicSituat, self.stk_cd_id, self.acc_per, 'chang_in_account_estim')

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
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    tax_type=tax_type,
                    basi=basi,
                    rate=rate
                )
                create_and_update('MainTaxAndTaxRate',**value_dict)
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
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        name=name,
                        rate=rate
                    )
                    create_and_update('IncomTaxRate',**value_dict)
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
        indexnos = ['0b06020000','0b060200']
        pass

    def converse(self):
        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.CompaniBasicSituat, self.stk_cd_id, self.acc_per,'tax_incent')

class MoneyFund(HandleIndexContent):
    '''
        货币资金
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MoneyFund, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07010000','0b070100']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
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
                    begin =  num_to_decimal(df.iloc[position[0], begin_pos[0]],unit)
                    end = num_to_decimal(df.iloc[position[0], end_pos[0]],unit)
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
        indexnos = ['0b07040100','0b070401']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
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
                    begin = num_to_decimal(df.iloc[position[0], begin_pos[0]],unit)
                    end = num_to_decimal(df.iloc[position[0], end_pos[0]],unit)
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
        indexnos = ['0b07040200','0b070402']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
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
                    end = num_to_decimal(df.iloc[position[0], end_pos[0]],unit)
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
        indexnos = ['0b07040300','0b070403']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
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

                    recognition = num_to_decimal(df.iloc[position[0], recognition_pos[0]],unit)
                    derecognition = num_to_decimal(df.iloc[position[0], derecognition_pos[0]],unit)
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
        indexnos = ['0b07040400','0b070404']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
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
                    end = num_to_decimal(df.iloc[position[0], end_pos[0]],unit)
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
        if self.indexno in ['0b07050100','0b07090100','0b11010100','0b11020100','0b070501',
                            '0b070901','0b110101','0b110201']:
            for k,content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        print(item)
                        for tables in item:
                            for table in tables:
                                if isinstance(table,str):
                                    continue
                                if table.iloc[:,0].str.contains('类别').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['summari'] = df
                                elif table.iloc[:,0].str.contains('账龄').any() or table.iloc[:,0].str.contains('年以内').any():
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
        accounts = {'0b07050100':('A','account'),'0b07090100':('A','other'),
                    '0b11010100':('B','account'),'0b11020100':('B','other'),
                    '0b070501':('A','account'),'0b070901':('A','other'),
                    '0b110101':('B','account'),'0b110201':('B','other')}
        pattern_num = re.compile('^.*?\d+.*?$')
        dfs, unit, instructi = self.recognize()
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
                        before = num_to_decimal(df.iloc[position[0], before_pos[0]],unit)
                    befores.append(before)
                for end_pos in ends_pos:
                    if len(position) == 0:
                        end = 0.00
                    else:
                        end = num_to_decimal(df.iloc[position[0], end_pos[0]],unit)
                    ends.append(end)

            all_dicts = {'end': ends,'before':befores}
            for item, values in all_dicts.items():
                if models.Receiv.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                    before_end=item,subject=accounts[self.indexno][1], typ_rep_id=accounts[self.indexno][0]):
                    obj = models.Receiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                        before_end=item,subject=accounts[self.indexno][1], typ_rep_id=accounts[self.indexno][0])
                    for subject, value in zip(subjects, values):
                        setattr(obj, subject, value)
                    obj.save()
                else:
                    obj = models.Receiv.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           before_end=item, subject=accounts[self.indexno][1],typ_rep_id=accounts[self.indexno][0])
                    for subject, value in zip(subjects, values):
                        setattr(obj, subject, value)
                    obj.save()

            obj_before = models.Receiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                   before_end='before', subject=accounts[self.indexno][1],
                                                   typ_rep_id=accounts[self.indexno][0])
            if obj_before.check_logic():
                pass
            else:
                raise Exception

            obj_end = models.Receiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                before_end='end', subject=accounts[self.indexno][1],
                                                typ_rep_id=accounts[self.indexno][0])
            if obj_end.check_logic():
                pass
            else:
                raise Exception

        else:
            pass

        if dfs.get('signi') is not None and len(dfs['signi'])>1:
            df = dfs['signi']
            name_pos = list(np.where(df.iloc[1, :].str.contains('按单位'))[0])
            balanc_pos = list(np.where((df.iloc[1, :]=='应收账款')|(df.iloc[1, :]=='其他应收款'))[0])
            bad_debt_prepar_pos = list(np.where(df.iloc[1, :].str.contains('坏账准备'))[0])
            reason_pos = list(np.where(df.iloc[1, :].str.contains('计提理由'))[0])

            names = list(df.iloc[2:,name_pos[0]])
            balancs = list(df.iloc[2:,balanc_pos[0]])
            bad_debt_prepars = list(df.iloc[2:,bad_debt_prepar_pos[0]])
            reasons = list(df.iloc[2:,reason_pos[0]])

            for (name,balanc,bad_debt_prepar,reason) in zip(names,balancs,bad_debt_prepars,reasons):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    before_end='end',
                    subject=accounts[self.indexno][1],
                    typ_rep_id=accounts[self.indexno][0],
                    company_name=name,
                    balanc=num_to_decimal(balanc, unit),
                    bad_debt_prepar=num_to_decimal(bad_debt_prepar, unit),
                    reason=reason,
                )
                create_and_update('SignificReceiv',**value_dict)
            obj_end = models.SignificReceiv.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           before_end='end', subject=accounts[self.indexno][1],
                                                           typ_rep_id=accounts[self.indexno][0])
            if len(obj_end) > 0:
                if obj_end[0].check_logic():
                    pass
                else:
                    pass
            else:
                pass
        else:
            pass


        if dfs.get('age') is not None and len(dfs['age'])>=1:
            if len(dfs['age']) == 1:
                df = dfs['age'][0]
            elif len(dfs['age'])>1:
                df = pd.concat(dfs['age'],ignore_index=True)
            else:
                pass
            one_year_pos = list(np.where(df.iloc[:, 0].str.contains('1年以内小计'))[0])
            one_year_pos = one_year_pos if len(one_year_pos)!=0 else list(np.where(df.iloc[:, 0].str.match(r'^.*?1.*?年.*?以内.*?$'))[0])
            print('one_year_pos',one_year_pos)
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
                        end = num_to_decimal(df.iloc[position[-1], end_pos[0]],unit)
                    ends.append(end)

            all_dicts = {'end': ends}

            for item, values in all_dicts.items():
                if models.ReceivAge.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                before_end=item, subject=accounts[self.indexno][1], typ_rep_id=accounts[self.indexno][0]):
                    obj = models.ReceivAge.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                    before_end=item, subject=accounts[self.indexno][1], typ_rep_id=accounts[self.indexno][0])
                    for subject, value in zip(subjects, values):
                        setattr(obj, subject, value)
                    obj.save()
                else:
                    obj = models.ReceivAge.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       before_end=item, subject=accounts[self.indexno][1], typ_rep_id=accounts[self.indexno][0])
                    for subject, value in zip(subjects, values):
                        setattr(obj, subject, value)
                    obj.save()

            obj_end = models.ReceivAge.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                      before_end='end', subject=accounts[self.indexno][1],
                                                      typ_rep_id=accounts[self.indexno][0])
            if len(obj_end) > 0:
                obj_end[0].check_logic()
        else:
            pass



        if dfs.get('other') is not None:
            df = dfs['other']
            # name_pos = list(np.where(df.iloc[1, :].str.contains('组合'))[0])
            # balanc_pos = list(np.where(df.iloc[1, :].str.contains('应收账款')|df.iloc[1, :].str.contains('其他应收款'))[0])
            bad_debt_prepar_pos = [get_item_in_df_pos('坏账准备',df)[1]] if (get_item_in_df_pos('坏账准备',df) is not None) else []

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = df.iloc[start_pos[0]:,0]
                balancs = df.iloc[start_pos[0]:,1]
                bad_debt_prepars = df.iloc[start_pos[0]:,2]
                for (name,balanc,bad_debt_prepar) in zip(names,balancs,bad_debt_prepars):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        before_end='end',
                        subject=accounts[self.indexno][1],
                        typ_rep_id=accounts[self.indexno][0],
                        name=name,
                        balanc=num_to_decimal(balanc, unit),
                        bad_debt_prepar=num_to_decimal(bad_debt_prepar, unit)
                    )
                    create_and_update('ReceivOtherCombin',**value_dict)

            obj_end = models.ReceivOtherCombin.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              before_end='end', subject=accounts[self.indexno][1],
                                                              typ_rep_id=accounts[self.indexno][0], name='合计')
            if len(obj_end) > 0:
                if obj_end[0].check_logic():
                    pass
                else:
                    raise Exception
            else:
                pass

        else:
            pass

class WithdrawOrReturnBadDebtPrepar(HandleIndexContent):
    '''
                本年计提、收回或转回的坏账准备情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(WithdrawOrReturnBadDebtPrepar, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07050200','0b07090200','0b11010200','0b070502',
                            '0b070902','0b110102','0b110202']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        accounts={'0b07050200':('A','account'),'0b07090200':('A','other'),
                  '0b11010200':('B','account'),'0b11020200':('B','other'),
                  '0b070502':('A','account'),'0b070902':('A','other'),
                  '0b110102':('B','account'),'0b110202':('B','other')}
        pattern = re.compile('^.*?计提坏账准备金额([\d\.,]*?)(\D*?元).*?收回或转回坏账准备金额([\d\.,]*?)(\D*?元).*?$')
        if len(instructi) > 0 and pattern.match(instructi):
            withdraw = pattern.match(instructi).groups()[0]
            unit = pattern.match(instructi).groups()[1]
            return_amount = pattern.match(instructi).groups()[2]
            value_dict  = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                before_end='end',
                subject=accounts[self.indexno][1],
                typ_rep_id=accounts[self.indexno][0],
                withdraw=num_to_decimal(withdraw, unit),
                return_amount=num_to_decimal(return_amount, unit),
            )
            create_and_update('WithdrawOrReturnBadDebtPrepar',**value_dict)
        else:
            pass

        if df is not None and len(df)>1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('单位名称'))[0])
            amount_pos = list(np.where(df.iloc[0, :].str.contains('金额'))[0])
            style_pos = list(np.where(df.iloc[0, :].str.contains('方式'))[0])
            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                amounts = get_values(df,start_pos,amount_pos,'d')
                styles = get_values(df,start_pos,style_pos,'t')

                for (name,amount,style) in zip(names,amounts,styles):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        before_end='end',
                        subject=accounts[self.indexno][1],
                        typ_rep_id=accounts[self.indexno][0],
                        company_name=name,
                        return_amount=num_to_decimal(amount, unit),
                        style=style
                    )
                    create_and_update('ReturnBadDebtPreparList',**value_dict)

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
        if self.indexno in ['0b07050300','0b07090300','0b11010300','0b11020300','0b070503',
                            '0b070903','0b110103','0b110203']:
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
        accounts = {'0b07050300':('A','account'),'0b07090300':('A','other'),
                    '0b11010300':('B','account'),'0b11020300':('B','other'),
                    '0b070503':('A','account'),'0b070903':('A','other'),
                    '0b110103':('B','account'),'0b110203':('B','other')}
        dfs, unit, instructi = self.recognize()
        if dfs.get('sum') is not None and len(dfs['sum']) > 1:
            df = dfs['sum']
            writeoff = df.iloc[-1,1]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                before_end='end',
                subject=accounts[self.indexno][1],
                typ_rep_id=accounts[self.indexno][0],
                writeoff=num_to_decimal(writeoff, unit)
            )
            create_and_update('WithdrawOrReturnBadDebtPrepar',**value_dict)
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


            names = list(df.iloc[1:, name_pos[0]]) if len(name_pos)>0 else []
            naturs = list(df.iloc[1:, natur_pos[0]])
            writeoffs = list(df.iloc[1:, writeoff_pos[0]])
            reasons = list(df.iloc[1:, reason_pos[0]])
            programs = list(df.iloc[1:, program_pos[0]])
            is_relateds = list(df.iloc[1:, is_related_pos[0]])

            for (name, natur, writeoff,reason,program,is_related) in \
            zip(names, naturs, writeoffs,reasons,programs,is_relateds):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    before_end='end',
                    subject=accounts[self.indexno][1],
                    typ_rep_id=accounts[self.indexno][0],
                    company_name=name,
                    writeoff=num_to_decimal(writeoff, unit),
                    natur_of_payment=natur,
                    reason=reason,
                    program=program,
                    is_related=is_related,
                )
                create_and_update('WriteOffReceiv',**value_dict)

class Top5Receiv(HandleIndexContent):
    '''
           应收款项前5名
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(Top5Receiv, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07050400','0b07060200','0b07090500','0b11010400','0b11020500','0b070504',\
                            '0b070602','0b070905','0b110104','0b110205']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        accounts = {'0b07050400':('A','account'),'0b07060200':('A','prepay'),
                    '0b07090500':('A','other'),'0b11010400':('B','account'),
                    '0b11020500':('B','other'),'0b070504':('A','account'),
                    '0b070602':('A','prepay'),'0b070905':('A','other'),
                    '0b110104':('B','account'),'0b110205':('B','other')}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:

            name_pos = list(np.where(df.iloc[0, :].str.contains('单位名称')|df.iloc[0, :].str.contains('对象'))[0])
            natur_pos = list(np.where(df.iloc[0, :].str.contains('性质'))[0])
            balanc_pos = list(np.where((df.iloc[0, :].str.contains('金额')|df.iloc[0, :].str.contains('余额')) &
                                       (~df.iloc[0, :].str.contains('坏账准备')))[0])
            bad_debt_prepar_pos = [get_item_in_df_pos('坏账准备',df)[1]] if (get_item_in_df_pos('坏账准备',df) is not None) else []
            ratio_pos = [get_item_in_df_pos('比例',df)[1]] if (get_item_in_df_pos('比例',df) is not None) else []
            age_pos = list(np.where(df.iloc[0, :].str.contains('账龄')|df.iloc[0, :].str.contains('年限'))[0])
            related_pos = list(np.where(df.iloc[0, :].str.contains('关系'))[0])
            reason_pos = list(np.where(df.iloc[0, :].str.contains('原因'))[0])

            if len(balanc_pos)>0:
                balanc_pos = balanc_pos
            else:
                if get_item_in_df_pos('金额',df,similar=False) is not None:
                    balanc_pos = [get_item_in_df_pos('金额',df,similar=False)[1]]
                elif get_item_in_df_pos('余额',df) is not None:
                    balanc_pos = [get_item_in_df_pos('余额',df)[1]]
                else:
                    pass

            start_row_pos = list(np.where(df.iloc[:,balanc_pos[0]].str.match(r'^[^年]*?\d+[^年]*?$'))[0])
            if len(start_row_pos)>0:
                data_length = len(df.iloc[start_row_pos[0]:,:])
                names = list(df.iloc[start_row_pos[0]:, name_pos[0]]) if len(name_pos)>0 else ['合计' for i in range(data_length)]
                naturs = list(df.iloc[start_row_pos[0]:, natur_pos[0]]) if len(natur_pos)>0 else ['' for i in range(data_length)]
                balancs = list(df.iloc[start_row_pos[0]:, balanc_pos[0]]) if len(balanc_pos)>0 else [0.00 for i in range(data_length)]
                bad_debt_prepars = list(df.iloc[start_row_pos[0]:, bad_debt_prepar_pos[0]]) if len(bad_debt_prepar_pos)>0 else [0.00 for i in range(data_length)]
                ages = list(df.iloc[start_row_pos[0]:, age_pos[0]]) if len(age_pos)>0 else ['' for i in range(data_length)]
                relateds = list(df.iloc[start_row_pos[0]:, related_pos[0]]) if len(related_pos)>0 else ['' for i in range(data_length)]
                reasons = list(df.iloc[start_row_pos[0]:, reason_pos[0]]) if len(reason_pos)>0 else ['' for i in range(data_length)]
                for (name, natur, balanc, bad_debt_prepar,age, related,reason) in \
                        zip(names, naturs, balancs, bad_debt_prepars,ages, relateds,reasons):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        before_end='end',
                        subject=accounts[self.indexno][1],
                        typ_rep_id=accounts[self.indexno][0],
                        company_name=name,
                        balanc=num_to_decimal(balanc, unit),
                        bad_debt_prepar=num_to_decimal(bad_debt_prepar, unit),
                        natur_of_payment=natur,
                        age=age,
                        relationship=related,
                        reason=reason,
                    )
                    create_and_update('Top5Receiv',**value_dict)

class PrepayAge(HandleIndexContent):
    '''
                        预付款项按账龄列示
                    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(PrepayAge, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07060100','0b070601']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
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
                    end = num_to_decimal(df.iloc[position[0], 1],unit)
                ends.append(end)
            for position in positions:
                if len(position) == 0:
                    before = 0.00
                else:
                    before = num_to_decimal(df.iloc[position[0], 3],unit)
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
        if self.indexno in ['0b07070100','0b07080100','0b07090400','0b070d0000','0b07150000',
                            '0b07160000','0b071d0400','0b071d0500','0b071e0000','0b071f0100','0b07200000',
                            '0b07220000','0b07230100','0b07240100','0b07260000','0b07290100','0b072b0000',
                            '0b072e0100','0b073c0000','0b073e0000','0b073f0000','0b07400000','0b07410000',
                            '0b07420000','0b07430000','0b07440000','0b07470100','0b07480100','0b07480200',
                            '0b07480300','0b07480400','0b07480500','0b07480600','0b07490100','0b07490400',
                            '0b11020400','0b070701','0b070800','0b070904','0b070c00','0b070c0000','0b070d00',
                            '0b071500','0b071600','0b071d04','0b071d05','0b071e00','0b071f01','0b072000',
                            '0b072200','0b072301','0b072401','0b072600','0b072901','0b072a00','0b072a0000'
                            '0b072b00','0b072d01','0b072e01','0b072f01','0b072f0100','0b07320000','0b073200',
                            '0b073400','0b073c00','0b073e00','0b073f00','0b074000','0b074100','0b074200'
                            '0b074300','0b074400','0b074500','0b074600','0b074901','0b074b01','0b074b02',
                            '0b074b03','0b074b04','0b074b05','0b074b06','0b074c01','0b074c04','0b074e00',
                            '0b110204',
                                    ]:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0,:].str.contains('期初').any() or table.iloc[0,:].str.contains('上期').any() \
                                    or table.iloc[0,:].str.contains('上年').any() or table.iloc[0,:].str.contains('年初').any():
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
        parent_company = ['0b11020400','0b110204']
        if self.indexno in parent_company:
            typ_rep_id = 'B'
        else:
            typ_rep_id = 'A'

        accounts = {'0b07070100':'interest_receiv','0b07080100':'dividend_receiv',\
                    '0b07090400':'other_receiv_natur','0b070d0000':'other_current_asset',\
                    '0b07150000':'engin_materi','0b07160000':'fix_asset_clean_up',\
                    '0b071d0400':'unconfirm_defer_incom_tax','0b071d0500':'expir_in_the_follow_year',\
                    '0b071e0000':'other_noncurr_asset','0b071f0100':'shortterm_loan',\
                    '0b07200000':'financi_liabil_measur_at_fair_valu','0b07220000':'bill_payabl',\
                    '0b07230100':'account_payabl','0b07240100':'advanc_receipt',\
                    '0b07260000':'tax_payabl','0b07290100':'other_payabl',\
                    '0b072b0000':'noncurr_liabil_due_within_one_year','0b072e0100':'bond_payabl',\
                    '0b073c0000':'undistributed_profit','0b073e0000':'tax_and_surcharg',\
                    '0b073f0000':'sale_expens','0b07400000':'manag_cost',\
                    '0b07410000':'financi_expens','0b07420000':'asset_impair_loss',\
                    '0b07430000':'chang_in_fair_valu','0b07440000':'invest_incom',\
                    '0b07470100':'incom_tax_expens','0b07480100':'receipt_other_busi',\
                    '0b07480200':'payment_other_busi','0b07480300':'receipt_other_invest',\
                    '0b07480400':'payment_other_invest','0b07480500':'receipt_other_financ',\
                    '0b07480600':'payment_other_financ','0b07490100':'addit_materi',\
                    '0b07490400':'composit_of_cash_and_cash_equival','0b11020400':'other_receiv_natur',
                    '0b070701':'interest_receiv','0b070800':'dividend_receiv',
                    '0b070904':'other_receiv_natur','0b070c00':'noncurr_asset_due_within_one_year',
                    '0b070c0000':'noncurr_asset_due_within_one_year','0b070d00':'other_current_asset',
                    '0b071500':'engin_materi','0b071600':'fix_asset_clean_up',
                    '0b071d04':'unconfirm_defer_incom_tax','0b071d05':'expir_in_the_follow_year',
                    '0b071e00':'other_noncurr_asset','0b071f01':'shortterm_loan',
                    '0b072000':'financi_liabil_measur_at_fair_valu','0b072200':'bill_payabl',
                    '0b072301':'account_payabl','0b072401':'advanc_receipt',
                    '0b072600':'tax_payabl','0b072901':'other_payabl',
                    '0b072a00':'liabil_held_for_sale','0b072a0000':'liabil_held_for_sale',
                    '0b072b00':'noncurr_liabil_due_within_one_year','0b072d01':'long_term_loan',
                    '0b072e01':'bond_payabl','0b072f01':'longterm_payabl','0b072f0100':'longterm_payabl',
                    '0b073200':'estim_liabil','0b07320000':'estim_liabil','0b073400':"other_noncurr_liabi",
                    '0b073c00':'undistributed_profit','0b073e00':'tax_and_surcharg',
                    '0b073f00':'sale_expens','0b074000':'manag_cost','0b074100':'financi_expens',
                    '0b074200':'asset_impair_loss','0b074300':'chang_in_fair_valu',
                    '0b074400':'invest_incom','0b074500':'asset_dispos_incom',
                    '0b074600':'other_incom','0b074901':'incom_tax_expens',
                    '0b074b01':'receipt_other_busi','0b074b02':'payment_other_busi',
                    '0b074b03':'receipt_other_invest','0b074b04':'payment_other_invest',
                    '0b074b05':'receipt_other_financ','0b074b06':'payment_other_financ',
                    '0b074c01':'addit_materi','0b074c04':'composit_of_cash_and_cash_equival',
                    '0b074e00':'asset_with_limit_ownership','0b110204':'other_receiv_natur'


        }
        if df is not None and len(df) > 1:
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末')|df.iloc[0, :].str.contains('年末')|
                                    df.iloc[0, :].str.contains('本期') | df.iloc[0, :].str.contains('本年'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初')|df.iloc[0, :].str.contains('年初')|
                                       df.iloc[0, :].str.contains('上期') | df.iloc[0, :].str.contains('上年'))[0])
            instruct_pos = list(np.where(df.iloc[0, :].str.contains('备注') | df.iloc[0, :].str.contains('说明')|
                                         df.iloc[0, :].str.contains('原因'))[0])
            names = list(df.iloc[1:,0])
            ends = list(df.iloc[1:,end_pos[0]])
            befores = list(df.iloc[1:,before_pos[0]])
            instructs = list(df.iloc[1:,instruct_pos[0]]) if len(instruct_pos)>0 else ['' for i in range(len(df)-1)]

            all_dicts = {'e': ends, 'b': befores}
            for item, values in all_dicts.items():
                for name, value,instruct in zip(names, values,instructs):
                    if models.CommonBeforeAndEndName.objects.filter(subject=accounts[self.indexno],name=name):
                        obj_name = models.CommonBeforeAndEndName.objects.get(subject=accounts[self.indexno],name=name)
                    else:
                        obj_name = models.CommonBeforeAndEndName.objects.create(subject=accounts[self.indexno],name=name)

                    value = num_to_decimal(value,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        before_end=item,
                        typ_rep_id=typ_rep_id,
                        name_id=obj_name.id,
                        amount=value,
                        instruct=instruct,
                    )
                    create_and_update('CommonBeforeAndEnd',**value_dict)
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
        indexnos = ['0b070a0100','0b07140100','0b11030000','0b070a01','0b070e01',
                            '0b070e0100','0b070f01','0b070f0100','0b071001','0b07100100',
                            '0b071401','0b110300']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        accounts = {'0b070a0100': ('A','inventori'),'0b07140100':('A','construct_in_progress'),
                    '0b11030000':('B','longterm_equiti_invest'),'0b070a01':('A','inventori'),
                    '0b070e01':('A','avail_for_sale_financi_asset'),'0b070e0100':('A','avail_for_sale_financi_asset'),
                    '0b070f01':('A','held_to_matur_invest'),'0b070f0100':('A','held_to_matur_invest'),
                    '0b071001':('A','longterm_receiv'),'0b07100100':('A','longterm_receiv'),
                    '0b071401':('A','construct_in_progress'),'0b110300':('B','longterm_equiti_invest')}

        if df is not None and len(df) > 1:
            # end_pos = list(np.where(df.iloc[0, :].str.contains('期末') | df.iloc[0, :].str.contains('年末') |
            #                         df.iloc[0, :].str.contains('本期') | df.iloc[0, :].str.contains('本年'))[0])
            # before_pos = list(np.where(df.iloc[0, :].str.contains('期初') | df.iloc[0, :].str.contains('年初') |
            #                            df.iloc[0, :].str.contains('上期') | df.iloc[0, :].str.contains('上年'))[0])
            start_pos = compute_start_pos(df)
            if len(start_pos) > 0:
                names = list(df.iloc[2:, 0])
                ends = list(zip(list(df.iloc[2:, 1]),list(df.iloc[2:, 2]),list(df.iloc[2:, 3])))
                befores = list(zip(list(df.iloc[2:, 4]),list(df.iloc[2:, 5]),list(df.iloc[2:, 6])))

                all_dicts = {'end': ends, 'before': befores}
                for item, values in all_dicts.items():
                    for name, value in zip(names, values):
                        balanc,impair,net = value
                        balance = num_to_decimal(balanc,unit)
                        impair = num_to_decimal(impair,unit)
                        net = num_to_decimal(net,unit)
                        value_dict = dict(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            before_end=item,
                            subject=accounts[self.indexno][1],
                            typ_rep_id=accounts[self.indexno][0],
                            name=name,
                            balance=balance,
                            impair=impair,
                            net=net,
                        )
                        create_and_update('CommonBalancImpairNet',**value_dict)
        else:
            pass

class AvailForSaleFinanciAssetFair(HandleIndexContent):
    '''
                   按公允价值计量的可供出售金融资产
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AvailForSaleFinanciAssetFair, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b070e02','0b070e0200']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 4:
            df = df.T
            name_pos = list(np.where(df.iloc[0, :].str.contains('分类'))[0])
            cost_pos = list(np.where(df.iloc[0, :].str.contains('成本'))[0])
            fair_value_pos = list(np.where(df.iloc[0, :]=='公允价值')[0])
            accumul_into_other_comprehens_incom_pos = list(np.where(df.iloc[0, :].str.contains('累计计入其他综合收益'))[0])
            impair_pos = list(np.where(df.iloc[0, :].str.contains('减值'))[0])

            start_row_pos = list(np.where(df.iloc[:, cost_pos[0]].str.match(r'^[^年]*?\d+[^年]*?$'))[0])
            if len(start_row_pos)>0:

                data_length = len(df.iloc[start_row_pos[0]:, :])
                names = list(df.iloc[start_row_pos[0]:, name_pos[0]]) if len(name_pos) > 0 else ['' for i in
                                                                                                 range(data_length)]
                costs = list(df.iloc[start_row_pos[0]:, cost_pos[0]]) if len(cost_pos) > 0 else [0.00 for i in
                                                                                                       range(data_length)]
                fair_values = list(df.iloc[start_row_pos[0]:, fair_value_pos[0]]) if len(fair_value_pos) > 0 else [0.00 for i in range(data_length)]
                accumul_into_other_comprehens_incoms = list(df.iloc[start_row_pos[0]:, accumul_into_other_comprehens_incom_pos[0]]) if len(
                    accumul_into_other_comprehens_incom_pos) > 0 else [0.00 for i in range(data_length)]
                impairs = list(df.iloc[start_row_pos[0]:, impair_pos[0]]) if len(impair_pos) > 0 else ['' for i in
                                                                                                       range(data_length)]

                for (name, cost, fair_value, accumul_into_other_comprehens_incom, impair) in \
                        zip(names, costs, fair_values, accumul_into_other_comprehens_incoms, impairs):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        cost=num_to_decimal(cost, unit),
                        fair_value=num_to_decimal(fair_value, unit),
                        accumul_into_other_comprehens_incom=num_to_decimal(accumul_into_other_comprehens_incom, unit),
                        impair=num_to_decimal(impair, unit),
                    )
                    create_and_update('AvailForSaleFinanciAssetFair',**value_dict)

class AvailForSaleFinanciAssetCost(HandleIndexContent):
    '''
                       按成本计量的可供出售金融资产
                   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AvailForSaleFinanciAssetCost, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b070e03','0b070e0300']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('被投资单位'))[0])
            b_book_balance_pos = list(np.where(df.iloc[0, :].str.contains('账面余额') & df.iloc[1, :].str.contains('初'))[0])
            i_book_balance_pos = list(np.where(df.iloc[0, :].str.contains('账面余额') & df.iloc[1, :].str.contains('增加'))[0])
            c_book_balance_pos = list(np.where(df.iloc[0, :].str.contains('账面余额') & df.iloc[1, :].str.contains('减少'))[0])
            e_book_balance_pos = list(np.where(df.iloc[0, :].str.contains('账面余额') & df.iloc[1, :].str.contains('末'))[0])
            b_impair_pos = list(np.where(df.iloc[0, :].str.contains('减值准备') & df.iloc[1, :].str.contains('初'))[0])
            i_impair_pos = list(np.where(df.iloc[0, :].str.contains('减值准备') & df.iloc[1, :].str.contains('增加'))[0])
            c_impair_pos = list(np.where(df.iloc[0, :].str.contains('减值准备') & df.iloc[1, :].str.contains('减少'))[0])
            e_impair_pos = list(np.where(df.iloc[0, :].str.contains('减值准备') & df.iloc[1, :].str.contains('末'))[0])

            proport_of_share_held_pos = list(np.where(df.iloc[0, :].str.contains('比例'))[0])
            cash_bonu_pos = list(np.where(df.iloc[0, :].str.contains('现金红利'))[0])

            # start_row_pos = list(np.where(df.iloc[:, b_book_balance_pos[0]].str.match(r'^[^年]*?\d+[^年]*?$'))[0])
            start_row_pos = compute_start_pos(df)
            if len(start_row_pos)>0:
                data_length = len(df.iloc[start_row_pos[0]:, :])
                names = list(df.iloc[start_row_pos[0]:, name_pos[0]]) if len(name_pos) > 0 else ['' for i in range(data_length)]

                b_book_balances = list(df.iloc[start_row_pos[0]:, b_book_balance_pos[0]]) if len(b_book_balance_pos) > 0 else [0.00 for i in range(data_length)]
                i_book_balances = list(df.iloc[start_row_pos[0]:, i_book_balance_pos[0]]) if len(i_book_balance_pos) > 0 else [0.00 for i in range(data_length)]
                c_book_balances = list(df.iloc[start_row_pos[0]:, c_book_balance_pos[0]]) if len(c_book_balance_pos) > 0 else [0.00 for i in range(data_length)]
                e_book_balances = list(df.iloc[start_row_pos[0]:, e_book_balance_pos[0]]) if len(e_book_balance_pos) > 0 else [0.00 for i in range(data_length)]
                b_impairs = list(df.iloc[start_row_pos[0]:, b_impair_pos[0]]) if len(b_impair_pos) > 0 else [0.00 for i in range(data_length)]
                i_impairs = list(df.iloc[start_row_pos[0]:, i_impair_pos[0]]) if len(i_impair_pos) > 0 else [0.00 for i in range(data_length)]
                c_impairs = list(df.iloc[start_row_pos[0]:, c_impair_pos[0]]) if len(c_impair_pos) > 0 else [0.00 for i in range(data_length)]
                e_impairs = list(df.iloc[start_row_pos[0]:, e_impair_pos[0]]) if len(e_impair_pos) > 0 else [0.00 for i in range(data_length)]
                proport_of_share_helds = list(df.iloc[start_row_pos[0]:, proport_of_share_held_pos[0]]) if len(proport_of_share_held_pos) > 0 else [0.00 for i in range(data_length)]
                cash_bonus = list(df.iloc[start_row_pos[0]:, cash_bonu_pos[0]]) if len(cash_bonu_pos) > 0 else [0.00 for i in range(data_length)]

                for (name, b_book_balance, i_book_balance, c_book_balance, e_book_balance,
                            b_impair,i_impair,c_impair,e_impair,proport_of_share_held,cash_bonu) in \
                        zip(names, b_book_balances, i_book_balances, c_book_balances, e_book_balances,
                            b_impairs,i_impairs,c_impairs,e_impairs,proport_of_share_helds,cash_bonus):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        b_book_balance=num_to_decimal(b_book_balance, unit),
                        i_book_balance=num_to_decimal(i_book_balance, unit),
                        c_book_balance=num_to_decimal(c_book_balance, unit),
                        e_book_balance=num_to_decimal(e_book_balance, unit),
                        b_impair=num_to_decimal(b_impair, unit),
                        i_impair=num_to_decimal(i_impair, unit),
                        c_impair=num_to_decimal(c_impair, unit),
                        e_impair=num_to_decimal(e_impair, unit),
                        proport_of_share_held=num_to_decimal(proport_of_share_held, unit),
                        cash_bonu=num_to_decimal(cash_bonu, unit),
                    )
                    create_and_update('AvailForSaleFinanciAssetCost',**value_dict)

class AvailForSaleFinanciAssetImpair(HandleIndexContent):
    '''
                   可供出售金融资产减值的变动情况
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AvailForSaleFinanciAssetImpair, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b070e04','0b070e0400']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 6:
            df = df.T
            name_pos = list(np.where(df.iloc[0, :].str.contains('分类'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('初已计提减值余额'))[0])
            accrual_pos = list(np.where(df.iloc[0, :]=='计提')[0])
            transfer_from_other_comprehens_incomm_pos = list(np.where(df.iloc[0, :].str.contains('从其他综合收益转入'))[0])
            cut_back_pos = list(np.where(df.iloc[0, :].str.contains('本年减少'))[0])
            fair_valu_rebound_pos = list(np.where(df.iloc[0, :].str.contains('公允价值回升'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('末已计提减值余额'))[0])

            start_row_pos = list(np.where(df.iloc[:, before_pos[0]].str.match(r'^[^年]*?\d+[^年]*?$'))[0])
            if len(start_row_pos)>0:
                data_length = len(df.iloc[start_row_pos[0]:, :])
                names = list(df.iloc[start_row_pos[0]:, name_pos[0]]) if len(name_pos) > 0 else ['' for i in range(data_length)]
                befores = list(df.iloc[start_row_pos[0]:, before_pos[0]]) if len(before_pos) > 0 else ['' for i in range(data_length)]
                accruals = list(df.iloc[start_row_pos[0]:, accrual_pos[0]]) if len(accrual_pos) > 0 else ['' for i in range(data_length)]
                transfer_from_other_comprehens_incomms = list(df.iloc[start_row_pos[0]:, transfer_from_other_comprehens_incomm_pos[0]]) if len(transfer_from_other_comprehens_incomm_pos) > 0 else ['' for i in range(data_length)]
                cut_backs = list(df.iloc[start_row_pos[0]:, cut_back_pos[0]]) if len(cut_back_pos) > 0 else ['' for i in range(data_length)]
                fair_valu_rebounds = list(df.iloc[start_row_pos[0]:, fair_valu_rebound_pos[0]]) if len(fair_valu_rebound_pos) > 0 else ['' for i in range(data_length)]
                ends = list(df.iloc[start_row_pos[0]:, end_pos[0]]) if len(end_pos) > 0 else ['' for i in range(data_length)]



                for (name, before, accrual, transfer_from_other_comprehens_incomm, cut_back,fair_valu_rebound,end) in \
                        zip(names, befores, accruals, transfer_from_other_comprehens_incomms, cut_backs,fair_valu_rebounds,ends):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        before=num_to_decimal(before, unit),
                        accrual=num_to_decimal(accrual, unit),
                        transfer_from_other_comprehens_incomm=num_to_decimal(transfer_from_other_comprehens_incomm,
                                                                             unit),
                        cut_back=num_to_decimal(cut_back, unit),
                        fair_valu_rebound=num_to_decimal(fair_valu_rebound, unit),
                        end=num_to_decimal(end, unit),
                    )
                    create_and_update('AvailForSaleFinanciAssetImpair',**value_dict)

class AvailForSaleFinanciAssetNoImpairDesc(HandleIndexContent):
    '''
                           可供出售权益工具年末公允价值严重下跌或非暂时性下跌但未计提减值准备相关说明
                       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AvailForSaleFinanciAssetNoImpairDesc, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b070e05','0b070e0500']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            cost_pos = list(np.where(df.iloc[0, :].str.contains('投资成本'))[0])
            fair_value_pos = list(np.where(df.iloc[0, :].str.contains('年末公允价值'))[0])
            fall_rate_pos = list(np.where(df.iloc[0, :].str.contains('下跌幅度'))[0])
            continu_fall_time_pos = list(np.where(df.iloc[0, :].str.contains('下跌时间'))[0])
            impair_pos = list(np.where(df.iloc[0, :].str.contains('已计提减值金额'))[0])
            reason_pos = list(np.where(df.iloc[0, :].str.contains('未计提减值准备原因'))[0])

            start_row_pos = list(np.where(df.iloc[:, cost_pos[0]].str.match(r'^[^年]*?\d+[^年]*?$'))[0])
            if len(start_row_pos)>0:
                data_length = len(df.iloc[start_row_pos[0]:, :])
                names = list(df.iloc[start_row_pos[0]:, name_pos[0]]) if len(name_pos) > 0 else ['' for i in range(data_length)]
                costs = list(df.iloc[start_row_pos[0]:, cost_pos[0]]) if len(cost_pos) > 0 else ['' for i in range(data_length)]
                fair_values = list(df.iloc[start_row_pos[0]:, fair_value_pos[0]]) if len(fair_value_pos) > 0 else ['' for i in range(data_length)]
                fall_rates = list(df.iloc[start_row_pos[0]:, fall_rate_pos[0]]) if len(fall_rate_pos) > 0 else ['' for i in range(data_length)]
                continu_fall_times = list(df.iloc[start_row_pos[0]:, continu_fall_time_pos[0]]) if len(continu_fall_time_pos) > 0 else ['' for i in range(data_length)]
                impairs = list(df.iloc[start_row_pos[0]:, impair_pos[0]]) if len(impair_pos) > 0 else ['' for i in range(data_length)]
                reasons = list(df.iloc[start_row_pos[0]:, reason_pos[0]]) if len(reason_pos) > 0 else ['' for i in range(data_length)]

                for (name, cost, fair_value, fall_rate, continu_fall_time,impair,reason) in \
                        zip(names, costs, fair_values, fall_rates, continu_fall_times,impairs,reasons):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        cost=num_to_decimal(cost, unit),
                        fair_value=num_to_decimal(fair_value, unit),
                        fall_rate=num_to_decimal(fall_rate, unit),
                        continu_fall_time=num_to_decimal(continu_fall_time, unit),
                        impair=num_to_decimal(impair, unit),
                        reason=reason
                    )
                    create_and_update('AvailForSaleFinanciAssetNoImpairDesc',**value_dict)
            else:
                pass

class SignificHeldToMaturInvest(HandleIndexContent):
    '''
       年末重要的持有至到期投资
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(SignificHeldToMaturInvest, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b070f02', '0b070f0200']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            book_value_pos = list(np.where(df.iloc[0, :].str.contains('面值'))[0])
            book_rate_pos = list(np.where(df.iloc[0, :].str.contains('票面利率'))[0])
            real_rate_pos = list(np.where(df.iloc[0, :].str.contains('实际利率'))[0])
            expiri_date_pos = list(np.where(df.iloc[0, :].str.contains('到期日'))[0])

            start_row_pos = list(np.where(df.iloc[:, book_value_pos[0]].str.match(r'^[^年]*?\d+[^年]*?$'))[0])
            if len(start_row_pos)>0:
                data_length = len(df.iloc[start_row_pos[0]:, :])
                names = list(df.iloc[start_row_pos[0]:, name_pos[0]]) if len(name_pos) > 0 else ['' for i in range(data_length)]
                book_values = list(df.iloc[start_row_pos[0]:, book_value_pos[0]]) if len(book_value_pos) > 0 else [0.00 for i in range(data_length)]
                book_rates = list(df.iloc[start_row_pos[0]:, book_rate_pos[0]]) if len(book_rate_pos) > 0 else [0.00 for i in range(data_length)]
                real_rates = list(df.iloc[start_row_pos[0]:, real_rate_pos[0]]) if len(real_rate_pos) > 0 else [0.00 for i in range(data_length)]
                expiri_dates = list(df.iloc[start_row_pos[0]:, expiri_date_pos[0]]) if len(expiri_date_pos) > 0 else ['' for i in range(data_length)]

                for (name, book_value, book_rate, real_rate, expiri_date) in \
                        zip(names, book_values, book_rates, real_rates, expiri_dates):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        face_valu=num_to_decimal(book_value, unit),
                        book_rate=num_to_decimal(book_rate, unit),
                        real_rate=num_to_decimal(real_rate, unit),
                        expiri_date=expiri_date
                    )
                    create_and_update('SignificHeldToMaturInvest',**value_dict)

class MajorLiabilAgeOver1Year(HandleIndexContent):
    '''
            账龄超过1年的重要负债或逾期应付利息
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MajorLiabilAgeOver1Year, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07230200','0b07240200','0b07270000','0b07290200',
                           '0b072302','0b072402','0b072902']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent )
        accounts = {'0b07230200': 'ap','0b07240200':'ar','0b07270000':'ip','0b07290200':'op',
                   '0b072302':'ap','0b072402':'ar' ,'0b072902':'op'}
        if df is not None and len(df) > 1:
            end_pos = list(np.where(df.iloc[0, :].str.contains('金额') | df.iloc[0, :].str.contains('余额'))[0])
            instruct_pos = list(np.where(df.iloc[0, :].str.contains('备注') | df.iloc[0, :].str.contains('说明')|
                                         df.iloc[0, :].str.contains('原因'))[0])
            names = list(df.iloc[1:, 0])
            ends = list(df.iloc[1:, end_pos[0]])
            instructs = list(df.iloc[1:, instruct_pos[0]]) if len(instruct_pos) > 0 else ['' for i in
                                                                                          range(len(df) - 1)]

            for name, value, instruct in zip(names, ends, instructs):
                value = num_to_decimal(value,unit)
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    subject=accounts[self.indexno],
                    typ_rep_id='A',
                    name=name,
                    amount=value,
                    reason=instruct,
                )
                create_and_update("MajorLiabilAgeOver1Year",**value_dict)
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

class OverduShorttermBorrow(HandleIndexContent):
    '''
                已逾期未偿还的短期借款情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OverduShorttermBorrow, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b071f02']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('借款单位') )[0])
            amount_pos = list(np.where(df.iloc[0, :].str.contains('余额') )[0])
            rate_pos = list(np.where(df.iloc[0, :].str.contains('借款利率') )[0])
            overdu_rate_pos = list(np.where(df.iloc[0, :].str.contains('逾期利率') )[0])
            overdu_time_pos = list(np.where(df.iloc[0, :].str.contains('逾期时间') )[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                amounts = get_values(df,start_pos,amount_pos,'d')
                rates = get_values(df,start_pos,rate_pos,'d')
                overdu_rates = get_values(df,start_pos,overdu_rate_pos,'d')
                overdu_times = get_values(df,start_pos,overdu_time_pos,'t')

                for ( name, amount, rate,overdu_rate,overdu_time) in \
                        zip(names, amounts, rates,overdu_rates,overdu_times):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        amount=num_to_decimal(amount, unit),
                        rate=num_to_decimal(rate, unit),
                        overdu_rate=num_to_decimal(overdu_rate, unit),
                        overdu_time=overdu_time,
                    )
                    create_and_update('OverduShorttermBorrow',**value_dict)
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
        indexnos = ['0b07070200','0b07080200','0b070702','0b070802']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        accounts = {'0b07070200':'interest_receiv','0b07080200':'dividend_receiv',
                    '0b070702':'interest_receiv','0b070802':'dividend_receiv'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('单位') | df.iloc[0, :].str.contains('对象')
                                     | df.iloc[0, :].str.contains('项目'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('金额') | df.iloc[0, :].str.contains('余额'))[0])
            overdu_time_pos = list(np.where(df.iloc[0, :].str.contains('时间')|df.iloc[0, :].str.contains('账龄'))[0])
            reason_pos = list(np.where(df.iloc[0, :].str.contains('原因'))[0])
            impair_pos = list(np.where(df.iloc[0, :].str.contains('减值'))[0])
            if df.iloc[:, end_pos[0]].str.match(r'.*?\d+.*?').any():
                start_row_pos = list(np.where(df.iloc[:, end_pos[0]].str.match(r'.*?\d+.*?'))[0])
                if len(start_row_pos)>0:
                    data_length = len(df.iloc[start_row_pos[0]:, :])
                    names = list(df.iloc[start_row_pos[0]:, name_pos[0]]) if len(name_pos) > 0 else ['' for i in
                                                                                                     range(data_length)]
                    ends = list(df.iloc[start_row_pos[0]:, end_pos[0]]) if len(end_pos) > 0 else ['' for i in
                                                                                                        range(data_length)]
                    overdu_times = list(df.iloc[start_row_pos[0]:, overdu_time_pos[0]]) if len(overdu_time_pos) > 0 else [0.00 for i in
                                                                                                           range(data_length)]
                    reasons = list(df.iloc[start_row_pos[0]:, reason_pos[0]]) if len(
                        reason_pos) > 0 else [0.00 for i in range(data_length)]
                    impairs = list(df.iloc[start_row_pos[0]:, impair_pos[0]]) if len(impair_pos) > 0 else ['' for i in
                                                                                                  range(data_length)]

                    for (name, end, overdu_time, reason, impair) in \
                            zip(names, ends, overdu_times, reasons, impairs):
                        value_dict = dict(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            typ_rep_id='A',
                            subject=accounts[self.indexno],
                            company_name=name,
                            end=num_to_decimal(end, unit),
                            overdu_time=overdu_time,
                            reason=reason,
                            impair=impair,
                        )
                        create_and_update('OverduInterest',**value_dict)
            else:
                pass

class InventoriImpairPrepar(HandleIndexContent):
    '''
                   存货跌价准备
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(InventoriImpairPrepar, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b070a0200','0b070a02']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            start_pos = compute_start_pos(df)
            if len(start_pos) > 0:
                names = list(df.iloc[start_pos[0]:, 0])
                befores = list(df.iloc[start_pos[0]:, 1])
                accruals = list(df.iloc[start_pos[0]:, 2])
                other_increass = list(df.iloc[start_pos[0]:, 3])
                transferback_resels = list(df.iloc[start_pos[0]:, 4])
                other_reducts = list(df.iloc[start_pos[0]:, 5])
                ends = list(df.iloc[start_pos[0]:, 6])

                for (name, before, accrual, other_increas, transferback_resel,other_reduct,end) in \
                        zip(names, befores, accruals, other_increass, transferback_resels,other_reducts,ends):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        before=num_to_decimal(before, unit),
                        accrual=num_to_decimal(accrual, unit),
                        other_increas=num_to_decimal(other_increas, unit),
                        transferback_resel=num_to_decimal(transferback_resel, unit),
                        other_reduct=num_to_decimal(other_reduct, unit),
                        end=num_to_decimal(end, unit),
                    )
                    create_and_update('InventoriImpairPrepar',**value_dict)

class InventoriCapitOfBorrowCost(HandleIndexContent):
    '''
                   存货年末余额中含有借款费用资本化金额
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(InventoriCapitOfBorrowCost, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b070a0300','0b070a03']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        pattern = re.compile('^.*?借款费用资本化金额.*?(\d+.*?\.{0,1}\d*?)(.*?元).*?$')
        if len(instructi) > 0 and pattern.match(instructi):
            inventori_capit_of_borrow_cost = pattern.match(instructi).groups()[0]
            unit = pattern.match(instructi).groups()[1]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                typ_rep_id='A',
                inventori_capit_of_borrow_cost=num_to_decimal(inventori_capit_of_borrow_cost, unit),
            )
            create_and_update('ComprehensNote',**value_dict)
        else:
            pass

class ConstructContract(HandleIndexContent):
    '''
       建造合同形成的已完工未结算资产情况、建造合同形成的已结算未完工项目情况
   '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ConstructContract, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b070a0400','0b07240300','0b070a04','0b072403']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        accounts = {'0b070a0400':'i','0b07240300':'a',
                    '0b070a04':'i','0b072403':'a'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 4:
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
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                typ_rep_id='A',
                subject=accounts[self.indexno],
                cost=num_to_decimal(cost, unit),
                gross_profit=num_to_decimal(gross_profit, unit),
                expect_loss=num_to_decimal(expect_loss, unit),
                project_settlement=num_to_decimal(project_settlement, unit),
                complet_settl=num_to_decimal(complet_settl, unit),
            )
            create_and_update('ConstructContract',**value_dict)

class AssetHeldForSale(HandleIndexContent):
    '''
                 持有待售资产
             '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AssetHeldForSale, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b070b00','0b070b0000' ]
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('单位') | df.iloc[0, :].str.contains('对象')
                                     | df.iloc[0, :].str.contains('项目'))[0])
            book_value_pos = list(np.where(df.iloc[0, :].str.contains('账面价值'))[0])
            fair_value_pos = list(np.where(df.iloc[0, :].str.contains('公允价值'))[0])
            estim_dispos_cost_pos = list(np.where(df.iloc[0, :].str.contains('预计处置费用'))[0])
            estim_dispos_time_pos = list(np.where(df.iloc[0, :].str.contains('预计处置时间'))[0])

            start_row_pos = list(np.where(df.iloc[:, book_value_pos[0]].str.match(r'.*?\d+.*?'))[0])
            if len(start_row_pos)==0:
                pass
            else:
                data_length = len(df.iloc[start_row_pos[0]:, :])
                names = list(df.iloc[start_row_pos[0]:, name_pos[0]]) if len(name_pos) > 0 else ['' for i in
                                                                                                 range(data_length)]
                book_values = list(df.iloc[start_row_pos[0]:, book_value_pos[0]]) if len(book_value_pos) > 0 else [0.00 for i in range(data_length)]
                fair_values = list(df.iloc[start_row_pos[0]:, fair_value_pos[0]]) if len(fair_value_pos) > 0 else [0.00 for i in range(data_length)]
                estim_dispos_costs = list(df.iloc[start_row_pos[0]:, estim_dispos_cost_pos[0]]) if len(estim_dispos_cost_pos) > 0 else [0.00 for i in range(data_length)]
                estim_dispos_times = list(df.iloc[start_row_pos[0]:, estim_dispos_time_pos[0]]) if len(estim_dispos_time_pos) > 0 else ['' for i in range(data_length)]

                for (name, book_value, fair_value, estim_dispos_cost, estim_dispos_time) in \
                        zip(names, book_values, fair_values, estim_dispos_costs, estim_dispos_times):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        book_value=num_to_decimal(book_value, unit),
                        fair_value=num_to_decimal(fair_value, unit),
                        estim_dispos_cost=num_to_decimal(estim_dispos_cost, unit),
                        estim_dispos_time=estim_dispos_time,
                    )
                    create_and_update('AssetHeldForSale',**value_dict)

class LongtermEquitiInvest(HandleIndexContent):
    '''
           长期股权投资
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(LongtermEquitiInvest, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07110000','0b071100']:
            for key,content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        item = combine_table_to_first(item)
                        dfs = get_dfs(('合营企业','联营企业'),item)
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
        df_com = {}
        if dfs.get('合营企业') is not None:
            df_com['joint_ventur'] = dfs['合营企业']
        if dfs.get('联营企业') is not None:
            df_com['pool'] = dfs['联营企业']
        if len(df_com)>=1 :
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
                        value_dict = dict(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            typ_rep_id='A',
                            company_name=name,
                            company_type=key,
                            before=num_to_decimal(before, unit),
                            addit_invest=num_to_decimal(addit_invest, unit),
                            reduc_invest=num_to_decimal(reduc_invest, unit),
                            invest_gain_and_loss=num_to_decimal(invest_gain_and_loss, unit),
                            other_comprehens_inc=num_to_decimal(other_comprehens_inc, unit),
                            chang_in_other_equit=num_to_decimal(chang_in_other_equit, unit),
                            cash_dividend_or_pro=num_to_decimal(cash_dividend_or_pro, unit),
                            provis_for_impair=num_to_decimal(provis_for_impair, unit),
                            other=num_to_decimal(other, unit),
                            end=num_to_decimal(end, unit),
                            impair_balanc=num_to_decimal(impair_balanc, unit),
                        )
                        create_and_update('LongtermEquitiInvest',**value_dict)
        else:
            pass

        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A', 'longterm_equiti_invest_desc')

class FixAsset(HandleIndexContent):
    '''
               固定资产、无形资产
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(FixAsset, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07130100','0b07190100','0b071301','0b071901']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        asset_types = {'0b07130100':'f','0b07190100':'i','0b071301':'f','0b071901':'i'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
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

                            value = num_to_decimal(value,unit)
                            value_dict = dict(
                                stk_cd_id=self.stk_cd_id,
                                acc_per=self.acc_per,
                                typ_rep_id='A',
                                asset_categori=asset_types[self.indexno],
                                valu_categori=valu_categori,
                                item_id=obj_asset_type.id,
                                increas_cut_back_type_id=obj_change_type.id,
                                amount_type=attr,
                                amount=value,
                            )
                            create_and_update('FixAsset',**value_dict)

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

                        value = num_to_decimal(value,unit)
                        value_dict = dict(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            typ_rep_id='A',
                            valu_categori='n',
                            asset_categori=asset_types[self.indexno],
                            item_id=obj_asset_type.id,
                            increas_cut_back_type_id=obj_change_type.id,
                            amount_type=attr,
                            amount=value
                        )
                        create_and_update('FixAsset',**value_dict)
        else:
            pass

        if self.indexno == '0b07190100' and len(instructi)>1:
            pattern = re.compile('^.*?内部研发形成的无形资产占无形资产余额的比例(.*?)%.*?$')
            if pattern.match(instructi):
                rd_intang_asset_per = pattern.match(instructi).groups()[0]
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    rd_intang_asset_per=num_to_decimal(rd_intang_asset_per, unit)
                )
                create_and_update('ComprehensNote',**value_dict)
        else:
            pass

class FixAssetStatu(HandleIndexContent):
    '''
                   固定资产状态
               '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(FixAssetStatu, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07130200','0b07130300','0b07130400','0b071302','0b071303','0b071304']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        status_dict = {'0b07130200':'i','0b07130300':'f','0b07130400':'b',
                       '0b071302':'i','0b071303':'f','0b071304':'b'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            item_pos = list(np.where(df.iloc[0,:].str.contains('项目'))[0])
            origin_pos = list(np.where(df.iloc[0,:].str.contains('账面原值'))[0])
            depreci_pos = list(np.where(df.iloc[0,:].str.contains('累计折旧'))[0])
            impair_pos = list(np.where(df.iloc[0,:].str.contains('减值准备'))[0])
            value_pos = list(np.where(df.iloc[0,:].str.contains('账面价值'))[0])
            instruct_pos = list(np.where(df.iloc[0,:].str.contains('备注'))[0])

            items = list(df.iloc[1:,item_pos[0]]) if len(item_pos)>0 else  ['' for i in range(len(df)-1)]
            origins = list(df.iloc[1:,origin_pos[0]]) if len(origin_pos)>0 else  [0.00 for i in range(len(df)-1)]
            deprecis = list(df.iloc[1:,depreci_pos[0]]) if len(depreci_pos)>0 else  [0.00 for i in range(len(df)-1)]
            impairs = list(df.iloc[1:,impair_pos[0]]) if len(impair_pos)>0 else  [0.00 for i in range(len(df)-1)]
            values = list(df.iloc[1:,value_pos[0]]) if len(value_pos)>0 else  [0.00 for i in range(len(df)-1)]
            instructs = list(df.iloc[1:,instruct_pos[0]]) if len(instruct_pos)>0 else  ['' for i in range(len(df)-1)]

            all_dict = {'o':origins,'a':deprecis,'i':impairs,'n':values}
            for valu_categori,amounts in all_dict.items():
                for key, item in enumerate(items):

                    if models.FixAndIntangAssetType.objects.filter(name=item):
                        obj_asset_type = models.FixAndIntangAssetType.objects.get(name=item)
                    else:
                        obj_asset_type = models.FixAndIntangAssetType.objects.create(name=item)

                    value = amounts[key]
                    value = num_to_decimal(value,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        valu_categori=valu_categori,
                        item_id=obj_asset_type.id,
                        status=status_dict[self.indexno],
                        amount=value,
                        instruct=instructs[key]
                    )
                    create_and_update('FixAssetStatu',**value_dict)

class UnfinishProperti(HandleIndexContent):
    '''
                      未办妥产权状态
                  '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(UnfinishProperti, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07130500','0b07190200','0b071305','0b071902']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        asset_dict = {'0b07130500': 'f','0b07190200':'i','0b071305':'f','0b071902':'i'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            item_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            value_pos = list(np.where(df.iloc[0, :].str.contains('账面价值'))[0])
            reason_pos = list(np.where(df.iloc[0, :].str.contains('未办妥产权'))[0])

            items = df.iloc[1:, item_pos[0]] if len(item_pos) > 0 else ['' for i in range(len(df) - 1)]
            values = df.iloc[1:, value_pos[0]] if len(value_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            reasons = df.iloc[1:, reason_pos[0]] if len(reason_pos) > 0 else ['' for i in range(len(df) - 1)]

            for (item,value,reason) in zip(items,values,reasons):
                value = num_to_decimal(value,unit)
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    asset_categori=asset_dict[self.indexno],
                    item=item,
                    amount=value,
                    reason=reason
                )
                create_and_update('UnfinishProperti',**value_dict)

class ImportProjectChange(HandleIndexContent):
    '''
          重要在建工程项目本期变动情况
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ImportProjectChange, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07140200','0b071402']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
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
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    name=name,
                    budget=budget,
                    before=num_to_decimal(before, unit),
                    increas=num_to_decimal(increas, unit),
                    transfer_to_fix_asset=num_to_decimal(transfer_to_fix_asset, unit),
                    other_reduct=num_to_decimal(other_reduct, unit),
                    end=num_to_decimal(end, unit),
                    progress=progress,
                    interest_capit_cumul_amount=num_to_decimal(interest_capit_cumul_amount, unit),
                    interest_capit_current_amount=num_to_decimal(interest_capit_current_amount, unit),
                    interest_capit_rate=num_to_decimal(interest_capit_rate, unit),
                    sourc_of_fund=sourc_of_fund
                )
                create_and_update('ImportProjectChange',**value_dict)

class DevelopExpenditur(HandleIndexContent):
    '''
          开发支出
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DevelopExpenditur, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b071a0000','0b071a00']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            increas_pos = list(np.where(df.iloc[0, :].str.contains('增加'))[0])
            cut_back_pos = list(np.where(df.iloc[0, :].str.contains('减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                befores = get_values(df,start_pos,before_pos,'d')
                increas_rds = get_values(df,start_pos,increas_pos[0],'d')
                other_increass = get_values(df,start_pos,increas_pos[1],'d')
                transfer_to_intang_assets = get_values(df,start_pos,cut_back_pos[0],'d')
                transfer_to_profits = get_values(df,start_pos,cut_back_pos[1],'d')
                ends = get_values(df,start_pos,end_pos,'d')

                for (name,before,increas_rd,other_increas,transfer_to_intang_asset,transfer_to_profit,end) in \
                        zip(names,befores,increas_rds,other_increass,transfer_to_intang_assets,transfer_to_profits,ends):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        before=num_to_decimal(before, unit),
                        increas_rd=num_to_decimal(increas_rd, unit),
                        other_increas=num_to_decimal(other_increas, unit),
                        transfer_to_intang_asset=num_to_decimal(transfer_to_intang_asset, unit),
                        transfer_to_profit=num_to_decimal(transfer_to_profit, unit),
                        end=num_to_decimal(end, unit),
                    )
                    create_and_update('DevelopExpenditur',**value_dict)

class Goodwil(HandleIndexContent):
    '''
          商誉
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(Goodwil, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b071b0100','0b071b01']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('单位名称或形成商誉的事项'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            increas_pos = list(np.where(df.iloc[0, :].str.contains('增加'))[0])
            cut_back_pos = list(np.where(df.iloc[0, :].str.contains('减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])

            start_pos = compute_start_pos(df)

            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                befores = get_values(df,start_pos,before_pos,'d')
                busi_mergers = get_values(df,start_pos,increas_pos[0],'d')
                other_increass = get_values(df,start_pos,increas_pos[1],'d')
                disposs = get_values(df,start_pos,cut_back_pos[0],'d')
                other_reducts = get_values(df,start_pos,cut_back_pos[1],'d')
                ends = get_values(df,start_pos,end_pos,'d')

                for (name,before,busi_merger,other_increas,dispos,other_reduct,end) in \
                        zip(names,befores,busi_mergers,other_increass,disposs,other_reducts,ends):

                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        before=num_to_decimal(before, unit),
                        busi_merger=num_to_decimal(busi_merger, unit),
                        other_increas=num_to_decimal(other_increas, unit),
                        dispos=num_to_decimal(dispos, unit),
                        other_reduct=num_to_decimal(other_reduct, unit),
                        end=num_to_decimal(end, unit),
                    )
                    create_and_update('Goodwil',**value_dict)

class LongtermPrepaidExpens(HandleIndexContent):
    '''
          长期待摊费用
      '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(LongtermPrepaidExpens, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b071c0000','0b071c00']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            increas_pos = list(np.where(df.iloc[0, :].str.contains('增加'))[0])
            amort_pos = list(np.where(df.iloc[0, :].str.contains('摊销'))[0])
            other_reduct_pos = list(np.where(df.iloc[0, :].str.contains('减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                befores = get_values(df,start_pos,before_pos,'d')
                increass = get_values(df,start_pos,increas_pos,'d')
                amorts = get_values(df,start_pos,amort_pos,'d')
                other_reducts = get_values(df,start_pos,other_reduct_pos,'d')
                ends = get_values(df,start_pos,end_pos,'d')

                for (name,before,increas,amort,other_reduct,end) in \
                        zip(names,befores,increass,amorts,other_reducts,ends):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        before=num_to_decimal(before, unit),
                        increas=num_to_decimal(increas, unit),
                        amort=num_to_decimal(amort, unit),
                        other_reduct=num_to_decimal(other_reduct, unit),
                        end=num_to_decimal(end, unit),
                    )
                    create_and_update('LongtermPrepaidExpens',**value_dict)

class DeferIncomTax(HandleIndexContent):
    '''
                递延所得税资产、递延所得税负债
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DeferIncomTax, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b071d0100','0b071d0200','0b071d01','0b071d02']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        accounts = {'0b071d0100': 'a', '0b071d0200': 'd','0b071d01':'a','0b071d02':'d'}

        if df is not None and len(df) > 2:

            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])
            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
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
                        diff = num_to_decimal(diff,unit)
                        amount = num_to_decimal(amount,unit)
                        value_dict = dict(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            before_end=item,
                            subject=accounts[self.indexno],
                            typ_rep_id='A',
                            name_id=obj_name.id,
                            diff=diff,
                            amount=amount,
                        )
                        create_and_update('DeferIncomTax',**value_dict)
        else:
            pass

class PayablEmployeCompens(HandleIndexContent):
    '''
                   应付职工薪酬
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(PayablEmployeCompens, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07250100','0b07250200','0b07250300','0b072501','0b072502','0b072503']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        accounts = {'0b07250100':'p','0b07250200':'short','0b07250300':'set',
                    '0b072501':'p','0b072502':'short','0b072503':'set'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:

            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            increase_pos = list(np.where(df.iloc[0, :].str.contains('增加'))[0])
            cut_back_pos = list(np.where(df.iloc[0, :].str.contains('减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                befores = get_values(df,start_pos,before_pos,'d')
                increases = get_values(df,start_pos,increase_pos,'d')
                cut_backs = get_values(df,start_pos,cut_back_pos,'d')
                ends = get_values(df,start_pos,end_pos,'d')

                for (name,before,increase,cut_back, end) in zip(names,befores,increases,cut_backs, ends):
                    if models.PayablEmployeCompensName.objects.filter(subject=accounts[self.indexno],name=name):
                        obj_name = models.PayablEmployeCompensName.objects.get(subject=accounts[self.indexno],name=name)
                    else:
                        obj_name = models.PayablEmployeCompensName.objects.create(subject=accounts[self.indexno],name=name)

                    before = num_to_decimal(before,unit)
                    increase = num_to_decimal(increase,unit)
                    cut_back = num_to_decimal(cut_back,unit)
                    end = num_to_decimal(end,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        before=before,
                        increase=increase,
                        cut_back=cut_back,
                        end=end,
                    )
                    create_and_update('PayablEmployeCompens',**value_dict)
        else:
            pass

class InterestPayabl(HandleIndexContent):
    '''
        应付利息
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(InterestPayabl, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b07270000','0b072700']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0,:].str.contains('期初').any() or table.iloc[0,:].str.contains('上期').any() \
                                    or table.iloc[0,:].str.contains('上年').any() or table.iloc[0,:].str.contains('年初').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['ip'] = df
                                elif table.iloc[0,:].str.contains('原因').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['reason'] = df
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
        accounts = {'0b07270000':'interest_payabl','0b072700':'interest_payabl'}
        if dfs.get('ip') is not None :
            df = dfs['ip']
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
                    if models.CommonBeforeAndEndName.objects.filter(subject=accounts[self.indexno],name=name):
                        obj_name = models.CommonBeforeAndEndName.objects.get(subject=accounts[self.indexno],name=name)
                    else:
                        obj_name = models.CommonBeforeAndEndName.objects.create(subject=accounts[self.indexno],name=name)

                    value = num_to_decimal(value,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        before_end=item,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        amount=value,
                        instruct=instruct,
                    )
                    create_and_update('CommonBeforeAndEnd',**value_dict)
        else:
            pass

        if dfs.get('reason') is not None:
            df = dfs['reason']
            end_pos = list(np.where(df.iloc[0, :].str.contains('金额') | df.iloc[0, :].str.contains('余额'))[0])
            instruct_pos = list(np.where(df.iloc[0, :].str.contains('备注') | df.iloc[0, :].str.contains('说明') |
                                         df.iloc[0, :].str.contains('原因'))[0])
            names = list(df.iloc[1:, 0])
            ends = list(df.iloc[1:, end_pos[0]])
            instructs = list(df.iloc[1:, instruct_pos[0]]) if len(instruct_pos) > 0 else ['' for i in
                                                                                          range(len(df) - 1)]

            for name, value, instruct in zip(names, ends, instructs):
                value = num_to_decimal(value,unit)
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    subject=accounts[self.indexno],
                    typ_rep_id='A',
                    name=name,
                    amount=value,
                    reason=instruct,
                )
                create_and_update('MajorLiabilAgeOver1Year',**value_dict)
        else:
            pass

class ChangInBondPayabl(HandleIndexContent):
    '''
            应付债券增减变动
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ChangInBondPayabl, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b072e0200','0b072e02']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df)>1:
            bond_name_pos = list(np.where(df.iloc[0, :].str.contains('债券名称') )[0])
            face_valu_pos = list(np.where(df.iloc[0, :].str.contains('面值') )[0])
            date_pos = list(np.where(df.iloc[0, :].str.contains('发行日期') )[0])
            term_pos = list(np.where(df.iloc[0, :].str.contains('债券期限') )[0])
            amount_pos = list(np.where(df.iloc[0, :].str.contains('发行金额') )[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初余额') )[0])
            issu_pos = list(np.where(df.iloc[0, :].str.contains('本期发行') )[0])
            interest_pos = list(np.where(df.iloc[0, :].str.contains('按面值计提利息') )[0])
            discount_amort_pos = list(np.where(df.iloc[0, :].str.contains('溢折价摊销') )[0])
            repay_pos = list(np.where(df.iloc[0, :].str.contains('本期偿还') )[0])
            other_reduct_pos = list(np.where(df.iloc[0, :].str.contains('其他减少') )[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末余额') )[0])

            bond_names = list(df.iloc[1:, bond_name_pos[0]]) if len(bond_name_pos) > 0 else ['' for i in range(len(df) - 1)]
            face_valus = list(df.iloc[1:, face_valu_pos[0]]) if len(face_valu_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            dates = list(df.iloc[1:, date_pos[0]]) if len(date_pos) > 0 else ['' for i in range(len(df) - 1)]
            terms = list(df.iloc[1:, term_pos[0]]) if len(term_pos) > 0 else ['' for i in range(len(df) - 1)]
            amounts = list(df.iloc[1:, amount_pos[0]]) if len(amount_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            befores = list(df.iloc[1:, before_pos[0]]) if len(before_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            issus = list(df.iloc[1:, issu_pos[0]]) if len(issu_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            interests = list(df.iloc[1:, interest_pos[0]]) if len(interest_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            discount_amorts = list(df.iloc[1:, discount_amort_pos[0]]) if len(discount_amort_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            repays = list(df.iloc[1:, repay_pos[0]]) if len(repay_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            other_reducts = list(df.iloc[1:, other_reduct_pos[0]]) if len(other_reduct_pos) > 0 else [0.00 for i in range(len(df) - 1)]
            ends = list(df.iloc[1:, end_pos[0]]) if len(end_pos) > 0 else [0.00 for i in range(len(df) - 1)]

            for (bond_name, face_valu, date,term,amount,before,issu,interest,discount_amort,repay, \
                        other_reduct,end) in \
                    zip(bond_names, face_valus, dates,terms,amounts,befores,issus,interests,discount_amorts,repays, \
                        other_reducts,ends):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    typ_rep_id='A',
                    bond_name=bond_name,
                    face_valu=num_to_decimal(face_valu, unit),
                    date=date,
                    term=term,
                    amount=num_to_decimal(amount, unit),
                    before=num_to_decimal(before, unit),
                    issu=num_to_decimal(issu, unit),
                    interest=num_to_decimal(interest, unit),
                    discount_amort=num_to_decimal(discount_amort, unit),
                    repay=num_to_decimal(repay, unit),
                    other_reduct=num_to_decimal(other_reduct, unit),
                    end=num_to_decimal(end, unit),
                )
                create_and_update('ChangInBondPayabl',**value_dict)
        else:
            pass

class CommonBICE(HandleIndexContent):
    '''
                   通用期初增减期末
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CommonBICE, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07370000','0b073b0000','0b071b02','0b071b0200','0b073100',
                            '0b07310000','0b073300','0b073700','0b073800','0b07380000',
                            '0b073a00','0b073a0000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        accounts = {'0b07370000':'cptl_rsrv','0b073b0000':'surplu_reserv',
                    '0b071b02':'goodwil_impair','0b071b0200':'goodwil_impair',
                    '0b073100':'special_payabl','0b07310000':'special_payabl',
                    '0b073700':'cptl_rsrv','0b073800':'stock','0b07380000':'stock',
                    '0b073a00':'special_reserv','0b073a0000':'special_reserv',
                    '0b073b00':'surplu_reserv'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目')|df.iloc[0, :].str.contains('单位名称'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            increase_pos = list(np.where(df.iloc[0, :].str.contains('增加'))[0])
            cut_back_pos = list(np.where(df.iloc[0, :].str.contains('减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])
            instruct_pos = list(np.where(df.iloc[0, :].str.contains('原因')|df.iloc[0, :].str.contains('说明'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                befores = get_values(df,start_pos,before_pos,'d')
                increases = get_values(df,start_pos,increase_pos,'d')
                cut_backs = get_values(df,start_pos,cut_back_pos,'d')
                ends = get_values(df,start_pos,end_pos,'d')
                instructs = get_values(df,start_pos,instruct_pos,'t')

                for (name,before,increase,cut_back, end,instruct) in zip(names,befores,increases,cut_backs, ends,instructs):
                    if models.CommonBICEName.objects.filter(subject=accounts[self.indexno],name=name):
                        obj_name = models.CommonBICEName.objects.get(subject=accounts[self.indexno],name=name)
                    else:
                        obj_name = models.CommonBICEName.objects.create(subject=accounts[self.indexno],name=name)

                    before = num_to_decimal(before,unit)
                    increase = num_to_decimal(increase,unit)
                    cut_back = num_to_decimal(cut_back,unit)
                    end = num_to_decimal(end,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        before=before,
                        increase=increase,
                        cut_back=cut_back,
                        end=end,
                        instruct=instruct,
                    )
                    create_and_update('CommonBICE',**value_dict)
        else:
            pass

        comprehens_notes = {
            '0b07370000': 'cptl_rsrv',
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

class DeferIncom(HandleIndexContent):
    '''
                       递延收益
                    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(DeferIncom, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位[：:](.*?元).*?$')
        if self.indexno in ['0b07330000','0b073300']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('形成原因').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['di']=df
                                elif table.iloc[0, :].str.contains('与资产相关').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['gs'] = df
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
        accounts = {'0b07330000': 'defer_incom','0b073300':'defer_incom' }
        dfs, unit, instructi = self.recognize()
        if dfs.get('di') is not None:
            df = dfs['di']
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            increase_pos = list(np.where(df.iloc[0, :].str.contains('增加'))[0])
            cut_back_pos = list(np.where(df.iloc[0, :].str.contains('减少'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])
            instruct_pos = list(np.where(df.iloc[0, :].str.contains('原因') | df.iloc[0, :].str.contains('说明'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df, start_pos, name_pos, 't')
                befores = get_values(df, start_pos, before_pos, 'd')
                increases = get_values(df, start_pos, increase_pos, 'd')
                cut_backs = get_values(df, start_pos, cut_back_pos, 'd')
                ends = get_values(df, start_pos, end_pos, 'd')
                instructs = get_values(df, start_pos, instruct_pos, 't')

                for (name, before, increase, cut_back, end, instruct) in zip(names, befores, increases, cut_backs, ends,
                                                                             instructs):
                    if models.CommonBICEName.objects.filter(subject=accounts[self.indexno], name=name):
                        obj_name = models.CommonBICEName.objects.get(subject=accounts[self.indexno], name=name)
                    else:
                        obj_name = models.CommonBICEName.objects.create(subject=accounts[self.indexno], name=name)

                    before = num_to_decimal(before,unit)
                    increase = num_to_decimal(increase,unit)
                    cut_back = num_to_decimal(cut_back,unit)
                    end = num_to_decimal(end,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        before=before,
                        increase=increase,
                        cut_back=cut_back,
                        end=end,
                        instruct=instruct,
                    )
                    create_and_update('CommonBICE',**value_dict)
        else:
            pass

        if dfs.get('gs') is not None:
            df = dfs['gs']
            if df is not None and len(df) > 1:
                name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
                before_pos = list(np.where(df.iloc[0, :].str.contains('期初余额'))[0])
                new_pos = list(np.where(df.iloc[0, :].str.contains('新增补助'))[0])
                includ_nonoper_incom_pos = list(np.where(df.iloc[0, :].str.contains('本期计入营业外收入金额'))[0])
                other_reduct_pos = list(np.where(df.iloc[0, :].str.contains('其他减少'))[0])
                end_pos = list(np.where(df.iloc[0, :].str.contains('期末余额'))[0])
                relat_pos = list(np.where(df.iloc[0, :].str.contains('与资产相关'))[0])

                relat_dict = {'与资产相关':'a','与收益相关':'e'}

                names = list(df.iloc[1:, name_pos[0]]) if len(name_pos) > 0 else ['' for i in range(len(df) - 1)]
                befores = list(df.iloc[1:, before_pos[0]]) if len(before_pos) > 0 else [0.00 for i in range(len(df) - 1)]
                news = list(df.iloc[1:, new_pos[0]]) if len(new_pos) > 0 else [0.00 for i in range(len(df) - 1)]
                includ_nonoper_incoms = list(df.iloc[1:, includ_nonoper_incom_pos[0]]) if len(includ_nonoper_incom_pos) > 0 else [0.00 for i in
                                                                                              range(len(df) - 1)]
                other_reducts = list(df.iloc[1:, other_reduct_pos[0]]) if len(other_reduct_pos) > 0 else [0.00 for i in range(len(df) - 1)]
                ends = list(df.iloc[1:, end_pos[0]]) if len(end_pos) > 0 else [0.00 for i in range(len(df) - 1)]
                relats = list(df.iloc[1:, relat_pos[0]]) if len(relat_pos) > 0 else [0.00 for i in range(len(df) - 1)]

                for (name, before,new, includ_nonoper_incom,other_reduct,end,relat) in \
                        zip(names, befores,news, includ_nonoper_incoms,other_reducts,ends,relats):

                    if models.CommonBeforeAndEndName.objects.filter(subject='govern_subsidi',name=name):
                        obj_name = models.CommonBeforeAndEndName.objects.get(subject='govern_subsidi',name=name)
                    else:
                        obj_name = models.CommonBeforeAndEndName.objects.create(subject='govern_subsidi',name=name)

                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        new=num_to_decimal(new, unit),
                        includ_nonoper_incom=num_to_decimal(includ_nonoper_incom, unit),
                        other_reduct=num_to_decimal(other_reduct, unit),
                        end=num_to_decimal(end, unit),
                        relat=relat_dict[relat] if relat_dict.get(relat) else '',
                    )
                    create_and_update('GovernSubsidi',**value_dict)

class OtherComprehensIncom(HandleIndexContent):
    '''
       其他综合收益
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OtherComprehensIncom, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07390000','0b073900']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        accounts = {'0b07390000':'other_comprehens_incom','0b073900':'other_comprehens_incom'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df)>1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            before_pos = list(np.where(df.iloc[0, :].str.contains('期初'))[0])
            amount_before_tax_pos = list(np.where(df.iloc[0, :].str.contains('所得税前发生额'))[0])
            less_transfer_to_profit_pos = list(np.where(df.iloc[0, :].str.contains('转入损益'))[0])
            less_income_tax_pos = list(np.where(df.iloc[0, :].str.contains('所得税费用'))[0])
            posttax_attribut_to_parent_compan_pos = list(np.where(df.iloc[0, :].str.contains('母公司'))[0])
            posttax_attribut_to_minor_share_pos = list(np.where(df.iloc[0, :].str.contains('少数股东'))[0])
            end_pos = list(np.where(df.iloc[0, :].str.contains('期末'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                befores = get_values(df,start_pos,before_pos,'d')
                amount_before_taxs = get_values(df,start_pos,amount_before_tax_pos,'d')
                less_transfer_to_profits = get_values(df,start_pos,less_transfer_to_profit_pos,'d')
                less_income_taxs = get_values(df,start_pos,less_income_tax_pos,'d')
                posttax_attribut_to_parent_compans = get_values(df,start_pos,posttax_attribut_to_parent_compan_pos,'d')
                posttax_attribut_to_minor_shares = get_values(df,start_pos,posttax_attribut_to_minor_share_pos,'d')
                ends = get_values(df,start_pos,end_pos,'d')

                for (name, before, amount_before_tax, less_transfer_to_profit, less_income_tax,
                            posttax_attribut_to_parent_compan,posttax_attribut_to_minor_share,end) in \
                        zip(names, befores, amount_before_taxs, less_transfer_to_profits, less_income_taxs,
                            posttax_attribut_to_parent_compans,posttax_attribut_to_minor_shares,ends):
                    if models.CommonBICEName.objects.filter(subject=accounts[self.indexno], name=name):
                        obj_name = models.CommonBICEName.objects.get(subject=accounts[self.indexno], name=name)
                    else:
                        obj_name = models.CommonBICEName.objects.create(subject=accounts[self.indexno], name=name)

                    before = num_to_decimal(before,unit)
                    amount_before_tax = num_to_decimal(amount_before_tax,unit)
                    less_transfer_to_profit = num_to_decimal(less_transfer_to_profit,unit)
                    less_income_tax = num_to_decimal(less_income_tax,unit)
                    posttax_attribut_to_parent_compan = num_to_decimal(posttax_attribut_to_parent_compan,unit)
                    posttax_attribut_to_minor_share = num_to_decimal(posttax_attribut_to_minor_share,unit)
                    end = num_to_decimal(end,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        before=before,
                        amount_before_tax=amount_before_tax,
                        less_transfer_to_profit=less_transfer_to_profit,
                        less_income_tax=less_income_tax,
                        posttax_attribut_to_parent_compan=posttax_attribut_to_parent_compan,
                        posttax_attribut_to_minor_share=posttax_attribut_to_minor_share,
                        end=end,
                    )
                    create_and_update('OtherComprehensIncom',**value_dict)
        else:
            pass

class OperIncomAndOperCost(HandleIndexContent):
    '''
           营业收入及营业成本
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OperIncomAndOperCost, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b073d0000','0b11040000','0b073d00','0b110400']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        typ_rep_dict = {'0b073d0000':'A','0b11040000':'B','0b073d00':'A','0b110400':'B'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            df = df.set_index([0])
            df = df.T
            df = df.set_index(['项目'])
            all_dict = df.to_dict()
            items = {'主营业务':'m','其他业务':'o','合计':'t','本期发生额':'e','上期发生额':'b','收入':'i','成本':'c'}
            for servic_categori in all_dict:
                for categorie in all_dict[servic_categori]:
                    before_end, subject = categorie
                    value = all_dict[servic_categori][categorie]
                    value = num_to_decimal(value,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        servic_categori=items[servic_categori],
                        before_end=items[before_end],
                        typ_rep_id=typ_rep_dict[self.indexno],
                        subject=items[subject],
                        amount=value,
                    )
                    create_and_update('OperIncomAndOperCost',**value_dict)
        else:
            pass

class NonoperIncomExpens(HandleIndexContent):
    '''
                       营业外收支
                    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(NonoperIncomExpens, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b07450000', '0b07460000','0b074700','0b074800']:
            for k, content in enumerate(self.indexcontent):
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('非经常性损益').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['sum'] = df
                                elif table.iloc[0, :].str.contains('与资产相关').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['gs'] = df
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
        accounts = {'0b07450000': 'nonoper_incom', '0b07460000': 'nonoper_expens',
                    '0b074700':'nonoper_incom','0b074800':'nonoper_expens'}
        dfs, unit, instructi = self.recognize()
        if dfs.get('sum') is not None :
            df = dfs['sum']
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            last_period_pos = list(np.where(df.iloc[0, :].str.contains('上期'))[0])
            current_period_pos = list(np.where(df.iloc[0, :].str.contains('本期'))[0])
            nonrecur_gain_amount_pos = list(np.where(df.iloc[0, :].str.contains('非经常性损益'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                last_periods = get_values(df,start_pos,last_period_pos,'d')
                nonrecur_gain_amounts = get_values(df,start_pos,nonrecur_gain_amount_pos,'d')
                current_periods =  get_values(df,start_pos,current_period_pos,'d')

                for (name, last_period, current_period, nonrecur_gain_amount) in zip(names, last_periods, current_periods, nonrecur_gain_amounts):
                    if models.CommonBeforeAndEndName.objects.filter(subject=accounts[self.indexno], name=name):
                        obj_name = models.CommonBeforeAndEndName.objects.get(subject=accounts[self.indexno], name=name)
                    else:
                        obj_name = models.CommonBeforeAndEndName.objects.create(subject=accounts[self.indexno], name=name)

                        last_period = num_to_decimal(last_period,unit)
                    current_period = num_to_decimal(current_period,unit)
                    nonrecur_gain_amount = num_to_decimal(nonrecur_gain_amount,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        last_period=last_period,
                        current_period=current_period,
                        nonrecur_gain_amount=nonrecur_gain_amount,
                    )
                    create_and_update('NonoperIncomExpens',**value_dict)
        else:
            pass

        if dfs.get('gs') is not None :
            df = dfs['gs']
            relat_dict = {'与资产相关':'a','与收益相关':'e'}
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            issu_subject_pos = list(np.where(df.iloc[0, :].str.contains('发放主体'))[0])
            issu_reason_pos = list(np.where(df.iloc[0, :].str.contains('发放原因'))[0])
            natur_type_pos = list(np.where(df.iloc[0, :].str.contains('性质类型'))[0])
            doe_it_affect_profit_pos = list(np.where(df.iloc[0, :].str.contains('补贴是否影响当年盈亏'))[0])
            is_special_pos = list(np.where(df.iloc[0, :].str.contains('是否特殊补贴'))[0])
            last_period_pos = list(np.where(df.iloc[0, :].str.contains('上期'))[0])
            current_period_pos = list(np.where(df.iloc[0, :].str.contains('本期'))[0])
            relat_pos = list(np.where(df.iloc[0, :].str.contains('与资产相关'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                issu_subjects = get_values(df,start_pos,issu_subject_pos,'t')
                issu_reasons = get_values(df,start_pos,issu_reason_pos,'t')
                natur_types = get_values(df,start_pos,natur_type_pos,'t')
                doe_it_affect_profits = get_values(df,start_pos,doe_it_affect_profit_pos,'t')
                is_specials = get_values(df,start_pos,is_special_pos,'t')
                last_periods =  get_values(df,start_pos,last_period_pos,'d')
                current_periods = get_values(df,start_pos,current_period_pos,'d')
                relats = get_values(df,start_pos,relat_pos,'t')

                for (name, issu_subject,issu_reason,natur_type,doe_it_affect_profit,is_special,last_period, current_period, relat) in \
                        zip(names, issu_subjects,issu_reasons,natur_types,doe_it_affect_profits,is_specials,last_periods,current_periods,relats):

                    last_period = num_to_decimal(last_period,unit)
                    current_period = num_to_decimal(current_period,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name=name,
                        issu_subject=issu_subject,
                        issu_reason=issu_reason,
                        natur_type=natur_type,
                        doe_it_affect_profit=doe_it_affect_profit,
                        is_special=is_special,
                        last_period=last_period,
                        current_period=current_period,
                        relat=relat_dict[relat] if (relat_dict.get(relat) is not None) else ''
                    )
                    create_and_update('GovernSubsidiIncludInCurrentProfit',**value_dict)
        else:
            pass

class ItemAmountReason(HandleIndexContent):
    '''
       项目金额说明
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ItemAmountReason, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b07470200','0b074b0000','0b12010000','0b071403','0b07140300',
                            '0b074902','0b120100']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        accounts = {'0b07470200': 'profit_to_incometax','0b074b0000':'asset_with_limit_ownership',
                    '0b12010000':'nonrecur_gain_and_loss','0b071403':'construct_in_progres',
                    '0b07140300':'construct_in_progres','0b074902':'profit_to_incometax',
                    '0b120100':'nonrecur_gain_and_loss'}
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df)>1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            amount_pos = list(np.where(df.iloc[0, :].str.contains('本期')|df.iloc[0, :].str.contains('期末')
                                       | df.iloc[0, :].str.contains('金额'))[0])
            instruct_pos = list(np.where(df.iloc[0, :].str.contains('说明')|df.iloc[0, :].str.contains('原因'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                amounts = get_values(df,start_pos,amount_pos,'d')
                instructs = get_values(df,start_pos,instruct_pos,'t')

                for (name, amount, instruct) in zip(names, amounts, instructs):
                    if models.CommonBeforeAndEndName.objects.filter(subject=accounts[self.indexno], name=name):
                        obj_name = models.CommonBeforeAndEndName.objects.get(subject=accounts[self.indexno], name=name)
                    else:
                        obj_name = models.CommonBeforeAndEndName.objects.create(subject=accounts[self.indexno], name=name)

                    amount = num_to_decimal(amount,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        amount=amount,
                        instruct=instruct
                    )
                    create_and_update('ItemAmountReason',**value_dict)
        else:
            pass

class ForeignCurrencItem(HandleIndexContent):
    '''
          外币货币性项目
       '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ForeignCurrencItem, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0b074c0100','0b074f01','0b074f02']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        instructi = re.sub('其他说明：','',instructi)
        if df is not None and len(df) > 1:
            df_length = len(df)
            among_pos = list(np.where(df.iloc[:, 0].str.contains('其中'))[0])
            subject_pos = [i-1 for i in among_pos]
            for i in range(len(subject_pos)):
                subject = df.iloc[subject_pos[i],0]

                subject_name = get_subject_obj(subject)

                if i+1 < len(subject_pos):
                    currencs = df.iloc[(subject_pos[i]+1):subject_pos[i+1],0]
                    values = [tuple(list(df.iloc[i,1:])) for i in range((subject_pos[i]+1),subject_pos[i+1])]
                else:
                    currencs = df.iloc[(subject_pos[i] + 1):df_length, 0]
                    values = [tuple(list(df.iloc[i, 1:])) for i in range((subject_pos[i] + 1), df_length)]
                for currenc,value in zip(currencs,values):
                    currenc = re.sub('其中[：:]','',currenc)
                    if models.CurrencName.objects.filter(name=currenc):
                        currenc_name = models.CurrencName.objects.get(name=currenc)
                    else:
                        currenc_name = models.CurrencName.objects.create(name=currenc)

                    foreign_bala,exchang_rate,rmb_bala = value
                    foreign_bala = num_to_decimal(foreign_bala,unit)
                    exchang_rate = num_to_decimal(exchang_rate,unit)
                    rmb_bala = num_to_decimal(rmb_bala,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        subject_id=subject_name.id,
                        currenc_id=currenc_name.id,
                        foreign_bala=foreign_bala,
                        exchang_rate=exchang_rate,
                        rmb_bala=rmb_bala,
                    )
                    create_and_update('ForeignCurrencItem',**value_dict)
        else:
            pass

        save_combine_instructi(instructi, models.ComprehensNote, self.stk_cd_id, self.acc_per,'A', 'foreign_busi_entiti_desc')

class AllGovernSubsidi(HandleIndexContent):
    '''
              所有的政府补助项目
           '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AllGovernSubsidi, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?元).*?$')
        if self.indexno in ['0b074e0000']:
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
        relat_dict = {'与资产相关': 'a', '与收益相关': 'e'}
        if df is not None and len(df) > 1:
            name_pos = list(np.where(df.iloc[0, :].str.contains('项目'))[0])
            amount_pos = list(np.where(df.iloc[0, :] == '金额')[0])
            relat_pos = list(np.where(df.iloc[0, :].str.contains('种类'))[0])
            includ_profit_pos = list(np.where(df.iloc[0, :].str.contains('计入当期损益'))[0])

            start_pos = compute_start_pos(df)
            if len(start_pos)>0:
                names = get_values(df,start_pos,name_pos,'t')
                amounts = get_values(df,start_pos,amount_pos,'d')
                includ_profits = get_values(df,start_pos,includ_profit_pos,'t')
                relats = get_values(df,start_pos,relat_pos,'t')

                for (relat, amount,name, includ_profit) in zip(relats, amounts,names, includ_profits):
                    if models.CommonBeforeAndEndName.objects.filter(subject='govern_subsidi', name=name):
                        obj_name = models.CommonBeforeAndEndName.objects.get(subject='govern_subsidi', name=name)
                    else:
                        obj_name = models.CommonBeforeAndEndName.objects.create(subject='govern_subsidi', name=name)

                    relat = relat_dict[relat] if relat in relat_dict else ''
                    amount = num_to_decimal(amount,unit)
                    includ_profit =  num_to_decimal(includ_profit,unit)
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        typ_rep_id='A',
                        name_id=obj_name.id,
                        relat=relat,
                        amount=amount,
                        includ_profit=includ_profit
                    )
                    create_and_update('AllGovernSubsidi',**value_dict)
        else:
            pass







