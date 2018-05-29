# _author : litufu
# date : 2018/4/20
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import re
import numpy as np

from report_data_extract import models
from collections import OrderedDict
from itertools import chain
import pandas as pd
from utils.handleindexcontent.commons import save_instructi
from utils.handleindexcontent.base import HandleIndexContent
from utils.mytools import remove_space_from_df,remove_per_from_df,num_to_decimal,combine_table_to_first
from utils.handleindexcontent.commons import save_instructi,recognize_instucti,recognize_df_and_instucti,\
    compute_start_pos,get_dfs
from utils.handleindexcontent.base import create_and_update

class BusiSituatDiscussAndAnalysi(HandleIndexContent):
    '''
    报告期内公司所从事的主要业务、经营模式及行业情况说明
    '''
    def __init__(self,stk_cd_id,acc_per ,indexno, indexcontent):
        super(BusiSituatDiscussAndAnalysi, self).__init__(stk_cd_id,acc_per,indexno,indexcontent)

    def recognize(self):
        indexnos = ['0401000000','04010000']
        pass

    def converse(self):

        pass


    def logic(self):
        pass

    def save(self):
        df,unit,instructi  = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'busi_situat_discuss')

class MajorOperConditDureTheReportPe(HandleIndexContent):
    '''
    报告期内主要经营情况
    '''
    def __init__(self,stk_cd_id,acc_per ,indexno, indexcontent):
        super(MajorOperConditDureTheReportPe, self).__init__(stk_cd_id,acc_per,indexno,indexcontent)

    def recognize(self):
        indexnos = ['0402000000']
        pass


    def converse(self):

        pass


    def logic(self):
        pass

    def save(self):
        df,unit,instructi  = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'major_oper_condit')

class RevenuAndCostAnalysi(HandleIndexContent):
    '''
    收入和成本分析
    '''
    def __init__(self,stk_cd_id,acc_per ,indexno, indexcontent):
        super(RevenuAndCostAnalysi, self).__init__(stk_cd_id,acc_per,indexno,indexcontent)

    def recognize(self):
        indexnos = ['0402010100','04020100']
        pass

    def converse(self):

        pass


    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'revenu_and_cost_anal')


class MainBusiSubIndustryProduRegion(HandleIndexContent):
    '''
            主营业务分行业，分产品，分地区情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MainBusiSubIndustryProduRegion, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        pattern = re.compile('^单位:(.*?元).*?$')
        pattern1 = re.compile('^主营业务分行业、分产品、分地区情况的说明.适用.不适用(.*?)$')
        dfs = {}
        unit = '元'
        instructi = ''
        if self.indexno in ['0402010101']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:, 0].str.contains("分行业").any():
                                    df = remove_space_from_df(table)
                                    dfs['分行业'] = df
                                elif table.iloc[:, 0].str.contains("分产品").any():
                                    df = remove_space_from_df(table)
                                    dfs['分产品'] = df
                                elif table.iloc[:, 0].str.contains("分地区").any():
                                    df = remove_space_from_df(table)
                                    dfs['分地区'] = df
                                else:
                                    pass
                        else:
                            pass
                    elif classify=='t' and len(item)>0:
                        if pattern.match(item):
                            unit = pattern.match(item).groups()[0]
                        elif pattern1.match(item):
                            instructi= pattern1.match(item).groups()[0]
                        else:
                            pass
                    else:
                        pass
        else:
            pass
        return dfs,unit,instructi

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs, unit, instructi = self.recognize()
        if len(dfs)>0:
            df_industri = dfs.get('分行业')
            df_produ = dfs.get('分产品')
            df_region = dfs.get('分地区')
            if df_industri is not None:
                df = df_industri.drop([0])
                industri = list(df.iloc[:,0])
                industri_incom = list(df.iloc[:,1])
                industri_cost = list(df.iloc[:,2])
                for industry, oprtng_incm, oprtng_cst in zip(industri, industri_incom, industri_cost):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        industry=industry,
                        oprtng_incm=num_to_decimal(oprtng_incm, unit),
                        oprtng_cst=num_to_decimal(oprtng_cst, unit)
                    )
                    create_and_update('MainBusiSubIndustry',**value_dict)
            else:
                pass

            if df_produ is not None:
                df = df_produ.drop([0])
                products = list(df.iloc[:,0])
                product_incom = list(df.iloc[:,1])
                product_cost = list(df.iloc[:,2])
                for product, oprtng_incm, oprtng_cst in zip(products, product_incom, product_cost):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        product=product,
                        oprtng_incm=num_to_decimal(oprtng_incm, unit),
                        oprtng_cst=num_to_decimal(oprtng_cst, unit)
                    )
                    create_and_update('MainBusiSubProduct',**value_dict)
            else:
                pass

            if df_region is not None:
                df = df_region.drop([0])
                regions = list(df.iloc[:,0])
                region_incom = list(df.iloc[:,1])
                region_cost = list(df.iloc[:,2])
                for region, oprtng_incm, oprtng_cst in zip(regions, region_incom, region_cost):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        region=region,
                        oprtng_incm=num_to_decimal(oprtng_incm, unit),
                        oprtng_cst=num_to_decimal(oprtng_cst, unit)
                    )
                    create_and_update('MainBusiSubRegion',**value_dict)
            else:
                pass
        else:
            pass
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'industry_product_region')


class MainBusiSubIndustryProduRegionSZ(HandleIndexContent):
    '''
            营业收入构成
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MainBusiSubIndustryProduRegionSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        pattern = re.compile('^单位:(.*?元).*?$')
        # pattern1 = re.compile('^主营业务分行业、分产品、分地区情况的说明.适用.不适用(.*?)$')
        dfs = {}
        unit = '元'
        # instructi = ''
        if self.indexno in ['04020201']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        item = combine_table_to_first(item)
                        dfs = get_dfs(('分行业', '分产品', '分地区'), item)
                        for i in dfs:
                            print(dfs[i])
                    elif classify=='t' and len(item)>0:
                        if pattern.match(item):
                            unit = pattern.match(item).groups()[0]
                        else:
                            pass
                    else:
                        pass
        else:
            pass
        return dfs,unit

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs, unit = self.recognize()
        if len(dfs)>0:
            df_industri = dfs.get('分行业')
            df_produ = dfs.get('分产品')
            df_region = dfs.get('分地区')
            if df_industri is not None:
                df = df_industri[~df_industri.iloc[:,0].str.contains('合计')]
                start_pos = compute_start_pos(df)
                industri = list(df.iloc[start_pos[0]:,0])
                industri_incom = list(df.iloc[start_pos[0]:,1])
                for industry, oprtng_incm in zip(industri, industri_incom):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        industry=industry,
                        oprtng_incm=num_to_decimal(oprtng_incm, unit),
                    )
                    create_and_update('MainBusiSubIndustry',**value_dict)
            else:
                pass

            if df_produ is not None:
                df = df_produ[~df_produ.iloc[:, 0].str.contains('合计')]
                start_pos = compute_start_pos(df)
                products = list(df.iloc[start_pos[0]:,0])
                product_incom = list(df.iloc[start_pos[0]:,1])
                for product, oprtng_incm in zip(products, product_incom):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        product=product,
                        oprtng_incm=num_to_decimal(oprtng_incm, unit)
                    )
                    create_and_update('MainBusiSubProduct',**value_dict)
            else:
                pass

            if df_region is not None:
                df = df_region[~df_region.iloc[:, 0].str.contains('合计')]
                start_pos = compute_start_pos(df)
                regions = list(df.iloc[start_pos[0]:,0])
                region_incom = list(df.iloc[start_pos[0]:,1])
                for region, oprtng_incm in zip(regions, region_incom):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        region=region,
                        oprtng_incm=num_to_decimal(oprtng_incm, unit)
                    )
                    create_and_update('MainBusiSubRegion',**value_dict)
            else:
                pass
        else:
            pass

class MainBusiSubIndustryProduRegionOvertenP(HandleIndexContent):
    '''
                占公司营业收入或营业利润 10%以上的行业、产品或地区情况
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MainBusiSubIndustryProduRegionOvertenP, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        pattern = re.compile('^单位:(.*?元).*?$')
        # pattern1 = re.compile('^主营业务分行业、分产品、分地区情况的说明.适用.不适用(.*?)$')
        dfs = {}
        unit = '元'
        # instructi = ''
        if self.indexno in ['04020202']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c':
                        item = combine_table_to_first(item)
                        dfs = get_dfs(('分行业','分产品','分地区'),item)
                    elif classify == 't' and len(item) > 0:
                        if pattern.match(item):
                            unit = pattern.match(item).groups()[0]
                        else:
                            pass
                    else:
                        pass
        else:
            pass
        return dfs, unit

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs, unit = self.recognize()
        if len(dfs) > 0:
            df_industri = dfs.get('分行业')
            df_produ = dfs.get('分产品')
            df_region = dfs.get('分地区')
            if df_industri is not None:
                df = df_industri
                pattern = re.compile('^.*?\d.*?$')
                start_pos = list(
                    np.where(df.iloc[:, 1].str.match(pattern) | df.iloc[:,1].str.match('nan'))[0])

                industri = list(df.iloc[start_pos[0]:, 0])
                industri_incom = list(df.iloc[start_pos[0]:, 1])
                industri_cost = list(df.iloc[start_pos[0]:, 2])
                for industry, oprtng_incm, oprtng_cst in zip(industri, industri_incom, industri_cost):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        industry=industry,
                        oprtng_incm=num_to_decimal(oprtng_incm, unit),
                        oprtng_cst=num_to_decimal(oprtng_cst, unit)
                    )
                    create_and_update('MainBusiSubIndustry',**value_dict)
            else:
                pass

            if df_produ is not None:
                df = df_produ
                pattern = re.compile('^.*?\d.*?$')
                start_pos = list(
                    np.where(df.iloc[:, 1].str.match(pattern) | df.iloc[:, 1].str.match('nan'))[0])
                products = list(df.iloc[start_pos[0]:, 0])
                product_incom = list(df.iloc[start_pos[0]:, 1])
                product_cost = list(df.iloc[start_pos[0]:, 2])
                for product, oprtng_incm, oprtng_cst in zip(products, product_incom, product_cost):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        product=product,
                        oprtng_incm=num_to_decimal(oprtng_incm, unit),
                        oprtng_cst=num_to_decimal(oprtng_cst, unit)
                    )
                    create_and_update('MainBusiSubProduct',**value_dict)
            else:
                pass

            if df_region is not None:
                df = df_produ
                pattern = re.compile('^.*?\d.*?$')
                start_pos = list(
                    np.where(df.iloc[:, 1].str.match(pattern) | df.iloc[:, 1].str.match('nan'))[0])
                regions = list(df.iloc[start_pos[0]:, 0])
                region_incom = list(df.iloc[start_pos[0]:, 1])
                region_cost = list(df.iloc[start_pos[0]:, 2])
                for region, oprtng_incm, oprtng_cst in zip(regions, region_incom, region_cost):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        region=region,
                        oprtng_incm=num_to_decimal(oprtng_incm, unit),
                        oprtng_cst=num_to_decimal(oprtng_cst, unit)
                    )
                    create_and_update('MainBusiSubRegion',**value_dict)
            else:
                pass
        else:
            pass

class ProductAndSale(HandleIndexContent):
    '''
                产品产销
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ProductAndSale, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        pattern0 = re.compile('^.*?单位：(.*?)$')
        pattern = re.compile('^产销量情况说明(.适用.不适用)?(.*?)$')
        df = None
        # unit = ''
        instructi = ''
        if self.indexno in ['0402010102']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        if item[0][0].iloc[0,:].str.contains("生产量").any():
                            df = remove_space_from_df(item[0][0])
                        else:
                            pass
                    elif classify == 't' and len(item) > 0:
                        if pattern.match(item):
                            instructi = pattern.match(item).groups()[1]
                        # elif pattern0.match(item):
                        #     unit  = pattern0.match(item).groups()[0]
                        else:
                            pass
                    else:
                        pass
        else:
            pass
        return df,instructi

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, instructi = self.recognize()
        if df is not None:
            product_vol_pos = list(np.where((df.iloc[0, :] == '生产量'))[0])
            sale_vol_pos = list(np.where((df.iloc[0, :] == '销售量'))[0])
            inventori_vol_pos = list(np.where((df.iloc[0, :] == '库存量'))[0])
            df = df.drop([0])
            main_products = list(df.iloc[:,0])
            product_vols = list(df.iloc[:,product_vol_pos[0]])
            sale_vols = list(df.iloc[:,sale_vol_pos[0]])
            inventori_vols = list(df.iloc[:,inventori_vol_pos[0]])

            for main_product, product_vol, sale_vol,inventori_vol in zip(main_products, product_vols, sale_vols,inventori_vols):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    main_product=main_product,
                    product_vol=product_vol,
                    sale_vol=sale_vol,
                    inventori_vol=inventori_vol,
                )
                create_and_update('ProductAndSale',**value_dict)
        else:
            pass
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'product_and_sale')

class CostAnalysi(HandleIndexContent):
    '''
                成本分析
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CostAnalysi, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        pattern0 = re.compile('^.*?单位：(.*?)$')
        pattern = re.compile('^成本分析其他情况说明(.适用.不适用)?(.*?)$')
        dfs = {}
        unit = '元'
        instructi = ''
        if self.indexno in ['0402010103']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0,:].str.contains("分行业").any():
                                    df = remove_space_from_df(table)
                                    dfs['分行业'] = df
                                elif table.iloc[0,:].str.contains("分产品").any():
                                    df = remove_space_from_df(table)
                                    dfs['分产品'] = df
                                elif table.iloc[0,:].str.contains("分地区").any():
                                    df = remove_space_from_df(table)
                                    dfs['分地区'] = df
                                else:
                                    pass
                    elif classify == 't' and len(item) > 0:
                        if pattern.match(item):
                            instructi = pattern.match(item).groups()[1]
                        elif pattern0.match(item):
                            unit  = pattern0.match(item).groups()[0]
                        else:
                            pass
                    else:
                        pass
        else:
            pass
        return dfs,unit, instructi

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs, unit, instructi = self.recognize()
        if len(dfs) > 0:
            df_industri = dfs.get('分行业')
            df_produ = dfs.get('分产品')
            df_region = dfs.get('分地区')
            if df_industri is not None:
                df = df_industri.drop([0])
                industri = list(df.iloc[:, 0])
                cost_composits = list(df.iloc[:, 1])
                current_periods = list(df.iloc[:, 2])
                last_periods = list(df.iloc[:, 4])
                for industry, cost_composit, current_period, last_period in zip(industri, cost_composits, current_periods,last_periods):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        industry=industry,
                        cost_composit=cost_composit,
                        current_period=current_period,
                        last_period=last_period
                    )
                    create_and_update('CostIndustry',**value_dict)
            else:
                pass

            if df_produ is not None:
                df = df_produ.drop([0])
                products = list(df.iloc[:, 0])
                cost_composits = list(df.iloc[:, 1])
                current_periods = list(df.iloc[:, 2])
                last_periods = list(df.iloc[:, 4])
                for product, cost_composit, current_period, last_period in zip(products, cost_composits, current_periods,last_periods):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        product=product,
                        cost_composit=cost_composit,
                        current_period=num_to_decimal(current_period, unit),
                        last_period=num_to_decimal(last_period, unit)
                    )
                    create_and_update('CostProduct',**value_dict)
            else:
                pass

            if df_region is not None:
                df = df_region.drop([0])
                regions = list(df.iloc[:, 0])
                cost_composits = list(df.iloc[:, 1])
                current_periods = list(df.iloc[:, 2])
                last_periods = list(df.iloc[:, 4])
                for region, cost_composit, current_period, last_period in zip(regions, cost_composits, current_periods,last_periods):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        region=region,
                        cost_composit=cost_composit,
                        current_period=num_to_decimal(current_period, unit),
                        last_period=num_to_decimal(last_period, unit)
                    )
                    create_and_update('CostSubRegion',**value_dict)
            else:
                pass
        else:
            pass
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'cost_analysi')

class CostAnalysiSZ(HandleIndexContent):
    '''
                成本分析
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CostAnalysiSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        pattern0 = re.compile('^.*?单位：(.*?)$')
        # pattern = re.compile('^成本分析其他情况说明(.适用.不适用)?(.*?)$')
        dfs = {}
        unit = '元'
        # instructi = ''
        if self.indexno in ['04020205']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0,:].str.contains("行业").any():
                                    df = remove_space_from_df(table)
                                    dfs['分行业'] = df
                                elif table.iloc[0,:].str.contains("产品").any():
                                    df = remove_space_from_df(table)
                                    dfs['分产品'] = df
                                elif table.iloc[0,:].str.contains("地区").any():
                                    df = remove_space_from_df(table)
                                    dfs['分地区'] = df
                                else:
                                    pass
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit  = pattern0.match(item).groups()[0]
                        else:
                            pass
                    else:
                        pass
        else:
            pass
        return dfs,unit

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs, unit = self.recognize()
        if len(dfs) > 0:
            df_industri = dfs.get('分行业')
            df_produ = dfs.get('分产品')
            df_region = dfs.get('分地区')
            if df_industri is not None:
                df = df_industri.drop([0,1])
                industri = list(df.iloc[:, 0])
                cost_composits = list(df.iloc[:, 1])
                current_periods = list(df.iloc[:, 2])
                last_periods = list(df.iloc[:, 4])
                for industry, cost_composit, current_period, last_period in zip(industri, cost_composits, current_periods,last_periods):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        industry=industry,
                        cost_composit=cost_composit,
                        current_period=num_to_decimal(current_period, unit),
                        last_period=num_to_decimal(last_period, unit)
                    )
                    create_and_update('CostIndustry',**value_dict)
            else:
                pass

            if df_produ is not None:
                df = df_produ.drop([0,1])
                products = list(df.iloc[:, 0])
                cost_composits = list(df.iloc[:, 1])
                current_periods = list(df.iloc[:, 2])
                last_periods = list(df.iloc[:, 4])
                for product, cost_composit, current_period, last_period in zip(products, cost_composits, current_periods,last_periods):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        product=product,
                        cost_composit=cost_composit,
                        current_period=num_to_decimal(current_period, unit),
                        last_period=num_to_decimal(last_period, unit)
                    )
                    create_and_update('CostProduct',**value_dict)
            else:
                pass

            if df_region is not None:
                df = df_region.drop([0,1])
                regions = list(df.iloc[:, 0])
                cost_composits = list(df.iloc[:, 1])
                current_periods = list(df.iloc[:, 2])
                last_periods = list(df.iloc[:, 4])
                for region, cost_composit, current_period, last_period in zip(regions, cost_composits, current_periods,last_periods):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        region=region,
                        cost_composit=cost_composit,
                        current_period=num_to_decimal(current_period, unit),
                        last_period=num_to_decimal(last_period, unit)
                    )
                    create_and_update('CostSubRegion',**value_dict)
            else:
                pass
        else:
            pass

class BusinesChang(HandleIndexContent):
    '''
        公司报告期内业务、产品或服务发生重大变化或调整有关情况
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BusinesChang, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['04020207']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'busi_chang')


class MajorCustomAndSupplie(HandleIndexContent):
    '''
                    前五大客户及供应商
                    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MajorCustomAndSupplie, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        # pattern0 = re.compile('^.*?单位：(.*?)$')
        pattern1 = re.compile('^.*?其他.*?说明(无)?(.适用.不适用)?(.*?)$')
        pattern_sale = re.compile('^.*?前五名客户销售额(.*\d\.{0,1}\d*?)(.*?元)，占年度销售总额(\d+\.{0,1}\d*?)%；其中前五名客户销售额中关联方销售额(.*\d\.{0,1}\d*?)(.*?元)，占年度销售总额(\d+\.{0,1}\d*?)%.*?(单位：.*?元)?$')
        pattern_buy = re.compile('^.*?前五名供应商采购额(.*\d\.{0,1}\d*?)(.*?元)，占年度采购总额(\d+\.{0,1}\d*?)%；其中前五名供应商采购额中关联方采购额(.*\d\.{0,1}\d*?)(.*?元)，占年度采购总额(\d+\.{0,1}\d*?)%.*?(单位：.*?元)?$')

        dfs = {}
        unit = {}
        table_unit = {}
        instructi = ''
        instructi_sale = {}
        instructi_suppli = {}
        if self.indexno in ['0402010104']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains("客户").any():
                                    df = remove_space_from_df(table)
                                    dfs['custom'] = df
                                elif table.iloc[0, :].str.contains("供应商").any():
                                    df = remove_space_from_df(table)
                                    dfs['suppli'] = df
                                else:
                                    pass
                    elif classify == 't' and len(item) > 0:
                        if pattern_sale.match(item):
                            instructi_sale['amount'] = pattern_sale.match(item).groups()[0]
                            unit['sale_ammount'] = pattern_sale.match(item).groups()[1]
                            instructi_sale['amount_prop'] = pattern_sale.match(item).groups()[2]
                            instructi_sale['amount_relat'] = pattern_sale.match(item).groups()[3]
                            unit['sale_ammount_relat'] = pattern_sale.match(item).groups()[4]
                            instructi_sale['amount_relat_prop'] = pattern_sale.match(item).groups()[5]
                            table_unit['sale'] = re.sub('单位：','',pattern_sale.match(item).groups()[6])
                        elif pattern_buy.match(item):
                            instructi_suppli['amount'] = pattern_buy.match(item).groups()[0]
                            unit['suppli_ammount'] = pattern_buy.match(item).groups()[1]
                            instructi_suppli['amount_prop'] = pattern_buy.match(item).groups()[2]
                            instructi_suppli['amount_relat'] = pattern_buy.match(item).groups()[3]
                            unit['suppli_ammount_relat'] = pattern_buy.match(item).groups()[4]
                            instructi_suppli['amount_relat_prop'] = pattern_buy.match(item).groups()[5]
                            table_unit['suppli'] = re.sub('单位：','',pattern_buy.match(item).groups()[6])
                        elif pattern1.match(item):
                            instructi =  pattern1.match(item).groups()[2]
                        else:
                            pass
                    else:
                        pass
        else:
            pass
        return dfs, table_unit, unit,instructi,instructi_sale,instructi_suppli

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs, table_unit, unit, instructi, instructi_sale, instructi_suppli = self.recognize()
        if len(dfs) > 0:
            df_custom = dfs.get('custom')
            df_suppli = dfs.get('suppli')
            table_unit_cunstom = table_unit.get('sale') if table_unit.get('sale') is not None else '元'
            table_unit_suppli = table_unit.get('suppli')if table_unit.get('suppli') is not None else '元'
            if df_custom is not None:
                df = df_custom.drop([0])
                names = list(df.iloc[:, 0])
                amounts = list(df.iloc[:, 1])
                amount_props = list(df.iloc[:, 2])
                for name, amount, amount_prop in zip(names, amounts, amount_props):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        major_class='custom',
                        name=name,
                        amount=num_to_decimal(amount, table_unit_cunstom),
                        amount_prop=amount_prop
                    )
                    create_and_update('MajorCustomAndSupplieDetail',**value_dict)
            else:
                pass

            if df_suppli is not None:
                df = df_suppli.drop([0])
                names = list(df.iloc[:, 0])
                amounts = list(df.iloc[:, 1])
                amount_props = list(df.iloc[:, 2])
                for name, amount, amount_prop in zip(names, amounts, amount_props):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        major_class='suppli',
                        name=name,
                        amount=num_to_decimal(amount, table_unit_suppli),
                        amount_prop=amount_prop
                    )
                    create_and_update('MajorCustomAndSupplieDetail',**value_dict)
            else:
                pass
        else:
            pass

        if len(instructi_sale)>0:
            amount = instructi_sale.get('amount')
            amount_prop = instructi_sale.get('amount_prop')
            amount_unit = unit.get('sale_ammount')
            amount_relat = instructi_sale.get('amount_relat')
            amount_relat_prop = instructi_sale.get('amount_relat_prop')
            amount_relat_unit = unit.get('sale_ammount_relat')
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                major_class='custom',
                amount=num_to_decimal(amount, amount_unit),
                amount_prop=amount_prop,
                amount_relat=num_to_decimal(amount_relat, amount_relat_unit),
                amount_relat_prop=amount_relat_prop,
            )
            create_and_update('MajorCustomAndSupplie',**value_dict)
        else:
            pass

        if len(instructi_suppli)>0:
            amount = instructi_suppli.get('amount')
            amount_prop = instructi_suppli.get('amount_prop')
            amount_unit = unit.get('suppli_ammount')
            amount_relat = instructi_suppli.get('amount_relat')
            amount_relat_prop = instructi_suppli.get('amount_relat_prop')
            amount_relat_unit = unit.get('suppli_ammount_relat')
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                major_class='suppli',
                amount=num_to_decimal(amount, amount_unit),
                amount_prop=amount_prop,
                amount_relat=num_to_decimal(amount_relat, amount_relat_unit),
                amount_relat_prop=amount_relat_prop,
            )
            create_and_update('MajorCustomAndSupplie',value_dict)
        else:
            pass
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'top_5_custom_and_supplier')

class MajorCustomAndSupplieSZ(HandleIndexContent):
    '''
                    前五大客户及供应商
                    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MajorCustomAndSupplieSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        pattern0 = re.compile('^.*?\（(.*?元)）.*?$')
        # pattern1 = re.compile('^.*?其他.*?说明(无)?(.适用.不适用)?(.*?)$')
        # pattern_sale = re.compile('^.*?前五名客户销售额(.*\d\.{0,1}\d*?)(.*?元)，占年度销售总额(\d+\.{0,1}\d*?)%；其中前五名客户销售额中关联方销售额(.*\d\.{0,1}\d*?)(.*?元)，占年度销售总额(\d+\.{0,1}\d*?)%.*?(单位：.*?元)?$')
        # pattern_buy = re.compile('^.*?前五名供应商采购额(.*\d\.{0,1}\d*?)(.*?元)，占年度采购总额(\d+\.{0,1}\d*?)%；其中前五名供应商采购额中关联方采购额(.*\d\.{0,1}\d*?)(.*?元)，占年度采购总额(\d+\.{0,1}\d*?)%.*?(单位：.*?元)?$')

        dfs = {}
        # unit = {}
        table_unit = {}
        contents = []
        # instructi_sale = {}
        # instructi_suppli = {}
        if self.indexno in ['04020208']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains("前五名客户合计销售金额").any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['custom'] = df
                                    table_unit['custom'] = (pattern0.match(table.iloc[0, 0]).groups())[0]
                                elif table.iloc[0, :].str.contains("客户名称").any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['custom_detail'] = df
                                    table_unit['custom_detail'] = pattern0.match(table.iloc[0, 2]).groups()[0]
                                elif table.iloc[0, :].str.contains("前五名供应商合计采购金额").any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['suppli'] = df
                                    table_unit['suppli'] = pattern0.match(table.iloc[0, 0]).groups()[0]
                                elif table.iloc[0, :].str.contains("供应商名称").any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    dfs['suppli_detail'] = df
                                    table_unit['suppli_detail'] = pattern0.match(table.iloc[0, 2]).groups()[0]
                                else:
                                    pass
                    elif classify == 't' and len(item) > 0:
                        content = re.sub('.适用.不适用', '', item)
                        contents.append(content)
                    else:
                        pass
        else:
            pass
        return dfs, table_unit, contents

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs, table_unit, contents = self.recognize()
        if len(dfs) > 0:
            df_custom = dfs.get('custom')
            df_custom_detail = dfs.get('custom_detail')
            df_suppli = dfs.get('suppli')
            df_suppli_detail = dfs.get('suppli_detail')
            table_unit_cunstom = table_unit.get('custom') if table_unit.get('custom') is not None else '元'
            table_unit_cunstom_detail = table_unit.get('custom_detail') if table_unit.get('custom_detail') is not None else '元'
            table_unit_suppli = table_unit.get('suppli')if table_unit.get('suppli') is not None else '元'
            table_unit_suppli_detail = table_unit.get('suppli_detail')if table_unit.get('suppli_detail') is not None else '元'
            if df_custom_detail is not None:
                df = df_custom_detail.drop([0])
                names = list(df.iloc[:, 1])
                amounts = list(df.iloc[:, 2])
                amount_props = list(df.iloc[:, 3])
                for name, amount, amount_prop in zip(names, amounts, amount_props):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        major_class='custom',
                        name=name,
                        amount=num_to_decimal(amount, table_unit_cunstom_detail),
                        amount_prop=amount_prop
                    )
                    create_and_update('MajorCustomAndSupplieDetail',**value_dict)
            else:
                pass

            if df_suppli_detail is not None:
                df = df_suppli_detail.drop([0])
                names = list(df.iloc[:, 1])
                amounts = list(df.iloc[:, 2])
                amount_props = list(df.iloc[:, 3])
                for name, amount, amount_prop in zip(names, amounts, amount_props):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        major_class='suppli',
                        name=name,
                        amount=num_to_decimal(amount, table_unit_suppli_detail),
                        amount_prop=amount_prop
                    )
                    create_and_update('MajorCustomAndSupplieDetail',**value_dict)
            else:
                pass

            if df_custom is not None and len(df_custom) > 0:
                amount = df_custom.iloc[0, 1]
                amount_prop = df_custom.iloc[1, 1]
                amount_unit = table_unit_cunstom
                # amount_relat = instructi_sale.get('amount_relat')
                amount_relat_prop = df_custom.iloc[2, 1]
                # amount_relat_unit = unit.get('sale_ammount_relat')
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    major_class='custom',
                    amount=num_to_decimal(amount, amount_unit),
                    amount_prop=amount_prop,
                    amount_relat_prop=amount_relat_prop,
                )
                create_and_update('MajorCustomAndSupplie',**value_dict)
            else:
                pass

            if df_suppli is not None and len(df_suppli) > 0:
                amount = df_suppli.iloc[0, 1]
                amount_prop = df_suppli.iloc[1, 1]
                amount_unit = table_unit_suppli
                # amount_relat = instructi_sale.get('amount_relat')
                amount_relat_prop = df_suppli.iloc[2, 1]
                # amount_relat_unit = unit.get('sale_ammount_relat')
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    major_class='suppli',
                    amount=num_to_decimal(amount, amount_unit),
                    amount_prop=amount_prop,
                    amount_relat_prop=amount_relat_prop,
                )
                create_and_update('MajorCustomAndSupplie',**value_dict)
            else:
                pass
        else:
            pass



class Expens(HandleIndexContent):
    '''
        费用
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(Expens, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0402010200','04020300']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 1:
            df = df.drop([0])
            names = list(df.iloc[:, 0])
            instructs = list(df.iloc[:, (len(df.columns)-1)])
            for name, instruct in zip(names, instructs):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    name=name,
                    change_reason=instruct
                )
                create_and_update('ExpensAnalysi',**value_dict)
            else:
                pass
        else:
            pass
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'chang_in_expense')

class RDInvest(HandleIndexContent):
    '''
            研发投入情况
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RDInvest, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0402010300']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            expens = df.iloc[list(np.where((df.iloc[:, 0] == '本期费用化研发投入'))[0])[0],1]
            capit = df.iloc[list(np.where((df.iloc[:, 0] == '本期资本化研发投入'))[0])[0],1]
            total = df.iloc[list(np.where((df.iloc[:, 0] == '研发投入合计'))[0])[0],1]
            proport_of_incom = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发投入总额占营业收入比例')))[0])[0],1]
            staff_number = df.iloc[list(np.where((df.iloc[:, 0].str.contains('公司研发人员的数量')))[0])[0],1]
            proport_of_staff = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发人员数量占公司总人数的比例')))[0])[0],1]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                expens=num_to_decimal(expens, unit),
                capit=num_to_decimal(capit, unit),
                total=num_to_decimal(total, unit),
                proport_of_incom=num_to_decimal(proport_of_incom),
                staff_number=int(float(re.sub(',', '', str(staff_number)))),
                proport_of_staff=num_to_decimal(proport_of_staff),
            )
            create_and_update('RDInvest',**value_dict)
        else:
            pass

class RDInvestSZ(HandleIndexContent):
    '''
            研发投入情况
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RDInvestSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['04020400']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_df_and_instucti(self.indexcontent)
        pattern = re.compile('^.*?研发投入金额（(.*?)）.*?$')
        if df is not None and len(df) > 0:
            unit = pattern.match(df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发投入金额')))[0])[0],0]).groups()[0]
            total = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发投入金额')))[0])[0],1]
            capit = df.iloc[list(np.where((df.iloc[:, 0].str.contains('资本化的金额')))[0])[0],1]
            # total = df.iloc[list(np.where((df.iloc[:, 0] == '研发投入合计'))[0])[0],1]
            proport_of_incom = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发投入占营业收入比例')))[0])[0],1]
            staff_number = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发人员数量')))[0])[0],1]
            proport_of_staff = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发人员数量占比')))[0])[0],1]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                capit=num_to_decimal(capit, unit),
                total=num_to_decimal(total, unit),
                proport_of_incom=num_to_decimal(proport_of_incom),
                staff_number=int(float(re.sub(',', '', str(staff_number)))),
                proport_of_staff=num_to_decimal(proport_of_staff),
            )
            create_and_update('RDInvest',**value_dict)
        else:
            pass

class CashFlow(HandleIndexContent):
    '''
            现金流变动
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CashFlow, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0402010400','04020500']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            df = df.drop([0])
            items = list(df.iloc[:,0])
            descs = list(df.iloc[:,(len(df.columns)-1)])
            for item,desc in zip(items,descs):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    item=item,
                    desc=desc
                )
                create_and_update('CashFlowAnalysi',**value_dict)
        else:
            pass
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'chang_in_cash_flow_statement')

class AssetAndLiabil(HandleIndexContent):
    '''
            资产负债变动情况说明
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AssetAndLiabil, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0402030100','04040100']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            df = df.drop([0])
            items = list(df.iloc[:,0])
            descs = list(df.iloc[:,(len(df.columns)-1)])
            for item,desc in zip(items,descs):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    item=item,
                    desc=desc
                )
                create_and_update('AssetAndLiabil',**value_dict)
        else:
            pass
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'balanc_sheet_chang')

class LimitAsset(HandleIndexContent):
    '''
            资产受限情况说明
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(LimitAsset, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0402030200']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            df = df.drop([0])
            items = list(df.iloc[:,0])
            descs = list(df.iloc[:,(len(df.columns)-1)])
            for item,desc in zip(items,descs):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    item=item,
                    desc=desc
                )
                create_and_update('LimitAsset',**value_dict)
        else:
            pass
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'restrict_asset')

class OveralInvest(HandleIndexContent):
    '''
                投资总体情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OveralInvest, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['04050100']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            pattern = re.compile('^.*?报告期投资额（(.*?)）.*?$')
            this_period = df.iloc[1,0]
            last_period = df.iloc[1, 1]
            unit = pattern.match(df.iloc[list(np.where((df.iloc[:, 0].str.contains('报告期投资额')))[0])[0], 0]).groups()[0]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                this_period=num_to_decimal(this_period, unit),
                last_period=num_to_decimal(last_period, unit)
            )
            create_and_update('OveralInvest',**value_dict)

class EquitiInvest(HandleIndexContent):
    '''
                股权投资情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(EquitiInvest, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['04050200']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            name_of_invest_compa_pos =  list(np.where((df.iloc[0, :] == '被投资公司名称'))[0])
            main_busi_pos =  list(np.where((df.iloc[0, :] == '主要业务'))[0])
            invest_method_pos =  list(np.where((df.iloc[0, :] == '投资方式'))[0])
            invest_amount_pos =  list(np.where((df.iloc[0, :] == '投资金额'))[0])
            sharehold_ratio_pos =  list(np.where((df.iloc[0, :] == '持股比例'))[0])
            sourc_of_fund_pos =  list(np.where((df.iloc[0, :] == '资金来源'))[0])
            partner_pos =  list(np.where((df.iloc[0, :] == '合作方'))[0])
            invest_period_pos =  list(np.where((df.iloc[0, :] == '投资期限'))[0])
            product_type_pos =  list(np.where((df.iloc[0, :] == '产品类型'))[0])
            progress_pos =  list(np.where((df.iloc[0, :] == '截至资产负债表日的进展情况'))[0])
            expect_revenu_pos =  list(np.where((df.iloc[0, :] == '预计收益'))[0])
            current_invest_gain_pos =  list(np.where((df.iloc[0, :] == '本期投资盈亏'))[0])
            involv_litig_pos =  list(np.where((df.iloc[0, :] == '是否涉诉'))[0])
            date_of_disclosur_pos =  list(np.where((df.iloc[0, :] == '披露日期（如有）'))[0])
            disclosur_index_pos =  list(np.where((df.iloc[0, :] == '披露索引（如有）'))[0])

            df = df.drop([0,(len(df.index)-1)])

            name_of_invest_compas = list(df.iloc[:, name_of_invest_compa_pos[0]])
            main_busis = list(df.iloc[:, main_busi_pos[0]]) if len(main_busi_pos)>0 else ['' for i in range(len(name_of_invest_compas))]
            invest_methods = list(df.iloc[:, invest_method_pos[0]]) if len(invest_method_pos)>0 else ['' for i in range(len(name_of_invest_compas))]
            invest_amounts = list(df.iloc[:, invest_amount_pos[0]]) if len(invest_amount_pos)>0 else [0.00 for i in range(len(name_of_invest_compas))]
            sharehold_ratios = list(df.iloc[:, sharehold_ratio_pos[0]]) if len(sharehold_ratio_pos)>0 else ['' for i in range(len(name_of_invest_compas))]
            sourc_of_funds = list(df.iloc[:, sourc_of_fund_pos[0]]) if len(sourc_of_fund_pos)>0 else ['' for i in range(len(name_of_invest_compas))]
            partners = list(df.iloc[:, partner_pos[0]]) if len(partner_pos)>0 else ['' for i in range(len(name_of_invest_compas))]
            invest_periods = list(df.iloc[:, invest_period_pos[0]]) if len(invest_period_pos)>0 else ['' for i in range(len(name_of_invest_compas))]
            product_types = list(df.iloc[:, product_type_pos[0]]) if len(product_type_pos)>0 else ['' for i in range(len(name_of_invest_compas))]
            progresses = list(df.iloc[:, progress_pos[0]]) if len(progress_pos)>0 else ['' for i in range(len(name_of_invest_compas))]
            expect_revenus = list(df.iloc[:, expect_revenu_pos[0]]) if len(expect_revenu_pos)>0 else [0.00 for i in range(len(name_of_invest_compas))]
            current_invest_gains = list(df.iloc[:, current_invest_gain_pos[0]]) if len(current_invest_gain_pos)>0 else [0.00 for i in range(len(name_of_invest_compas))]
            involv_litigs = list(df.iloc[:, involv_litig_pos[0]]) if len(involv_litig_pos)>0 else ['' for i in range(len(name_of_invest_compas))]
            date_of_disclosurs = list(df.iloc[:, date_of_disclosur_pos[0]]) if len(date_of_disclosur_pos)>0 else ['' for i in range(len(name_of_invest_compas))]
            disclosur_indexes = list(df.iloc[:, disclosur_index_pos[0]]) if len(disclosur_index_pos)>0 else ['' for i in range(len(name_of_invest_compas))]

            for (name_of_invest_compa, main_busi,invest_method,invest_amount ,\
                    sharehold_ratio,sourc_of_fund,partner,invest_period,product_type,progress, \
                        expect_revenu,current_invest_gain, involv_litig ,date_of_disclosur, \
                                  disclosur_index ) in zip(name_of_invest_compas, main_busis,invest_methods,invest_amounts ,\
                    sharehold_ratios,sourc_of_funds,partners,invest_periods,product_types,progresses, \
                        expect_revenus,current_invest_gains, involv_litigs ,date_of_disclosurs, \
                                  disclosur_indexes    ):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    name_of_invest_compa=name_of_invest_compa,
                    main_busi=main_busi,
                    invest_method=invest_method,
                    invest_amount=num_to_decimal(invest_amount, unit),
                    sharehold_ratio=sharehold_ratio,
                    sourc_of_fund=sourc_of_fund,
                    partner=partner,
                    invest_period=invest_period,
                    product_type=product_type,
                    progress=progress,
                    expect_revenu=num_to_decimal(expect_revenu, unit),
                    current_invest_gain=num_to_decimal(current_invest_gain, unit),
                    involv_litig=involv_litig,
                    date_of_disclosur=date_of_disclosur,
                    disclosur_index=disclosur_index
                )
                create_and_update('EquitiInvest',**value_dict)
        else:
            pass


class SellMajorAsset(HandleIndexContent):
    '''
                    出售重大资产情况,出售重大股权情况
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(SellMajorAsset, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['04060100','04060200']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, unit, instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df) > 0:
            pattern1 = re.compile('.*?交易价格（(.*?元)）.*?')
            pattern2 = re.compile('.*?本期初起至出售日该.*?为上市公司贡献的净利润（(.*?元)）.*?')

            trade_partner_pos = list(np.where((df.iloc[0, :] == '交易对方'))[0])
            asset_sold_pos = list(np.where((df.iloc[0, :].str.contains('被出售')))[0])
            sale_day_pos = list(np.where((df.iloc[0, :] == '出售日'))[0])
            trade_price_pos = list(np.where((df.iloc[0, :].str.contains('交易价格') ))[0])
            before_net_profit_pos = list(np.where((df.iloc[0, :].str.contains(r'本期初起至出售日')))[0])
            impact_of_sale_pos = list(np.where((df.iloc[0, :].str.contains('出售对公司的影响')))[0])
            proport_net_profit_pos = list(np.where((df.iloc[0, :].str.contains('出售为上市公司贡献的净利润占净利润总额的比例')))[0])
            price_principl_pos = list(np.where((df.iloc[0, :].str.contains('出售定价原则')))[0])
            relat_transa_pos = list(np.where((df.iloc[0, :] == '是否为关联交易'))[0])
            connect_relat_pos = list(np.where((df.iloc[0, :].str.contains('与交易对方的关联关系')))[0])
            transfer_of_titl_pos = list(np.where((df.iloc[0, :].str.contains('是否已全部过户')))[0])
            debt_transf_pos = list(np.where((df.iloc[0, :] == '所涉及的债权债务是否已全部转移'))[0])
            is_on_schedul_pos = list(np.where((df.iloc[0, :].str.contains('是否按计划如期实施')))[0])
            date_of_disclosur_pos = list(np.where((df.iloc[0, :] == '披露日期'))[0])
            disclosur_index_pos = list(np.where((df.iloc[0, :] == '披露索引'))[0])
            if self.indexno == '04060100':
                trade_class = 'asset'
            elif self.indexno =='04060200':
                trade_class = 'equiti'
            else:
                raise Exception
            unit1 = pattern1.match(df.iloc[0,trade_price_pos[0]]).groups()[0]
            unit2 = pattern2.match(df.iloc[0,before_net_profit_pos[0]]).groups()[0]
            df = df.drop([0])

            trade_partners = list(df.iloc[:, trade_partner_pos[0]])
            asset_solds = list(df.iloc[:, asset_sold_pos[0]])
            sale_days = list(df.iloc[:, sale_day_pos[0]])
            trade_prices = list(df.iloc[:, trade_price_pos[0]])
            before_net_profits = list(df.iloc[:, before_net_profit_pos[0]])
            impact_of_sales = list(df.iloc[:, impact_of_sale_pos[0]])
            proport_net_profits = list(df.iloc[:, proport_net_profit_pos[0]])
            price_principls = list(df.iloc[:, price_principl_pos[0]])
            relat_transas = list(df.iloc[:, relat_transa_pos[0]])
            connect_relats = list(df.iloc[:, connect_relat_pos[0]])
            transfer_of_titls = list(df.iloc[:, transfer_of_titl_pos[0]])
            if debt_transf_pos is not None and len(debt_transf_pos)>0:
                debt_transfs= list(df.iloc[:, debt_transf_pos[0]])
            else:
                debt_transfs = ['' for i in range(len(transfer_of_titls))]
            is_on_scheduls = list(df.iloc[:, is_on_schedul_pos[0]])
            date_of_disclosurs = list(df.iloc[:, date_of_disclosur_pos[0]])
            disclosur_indexes = list(df.iloc[:, disclosur_index_pos[0]])

            for (trade_partner,asset_sold,sale_day,trade_price, \
                                         before_net_profit,impact_of_sale,proport_net_profit, price_principl,\
                                         relat_transa,connect_relat,transfer_of_titl, \
                                         debt_transf,is_on_schedul,date_of_disclosur,disclosur_index) \
                    in zip(trade_partners,asset_solds,sale_days,trade_prices, \
                                         before_net_profits,impact_of_sales,proport_net_profits, price_principls,\
                                         relat_transas,connect_relats,transfer_of_titls, \
                                         debt_transfs,is_on_scheduls,date_of_disclosurs,disclosur_indexes):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    trade_class=trade_class,
                    trade_partner=trade_partner,
                    asset_sold=asset_sold,
                    sale_day=sale_day,
                    trade_price=num_to_decimal(trade_price, unit1),
                    before_net_profit=num_to_decimal(before_net_profit, unit2),
                    impact_of_sale=impact_of_sale,
                    proport_net_profit=proport_net_profit,
                    price_principl=price_principl,
                    relat_transa=relat_transa,
                    connect_relat=connect_relat,
                    transfer_of_titl=transfer_of_titl,
                    debt_transf=debt_transf,
                    is_on_schedul=is_on_schedul,
                    date_of_disclosur=date_of_disclosur,
                    disclosur_index=disclosur_index,
                )
                create_and_update('SellMajorAsset',**value_dict)
        else:
            pass

class IndustriOperInformAnalysi(HandleIndexContent):
    '''
            行业经营性信息分析
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(IndustriOperInformAnalysi, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos =  ['0402040000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'industri_busi_inform')

class MajorHoldCompaniAnalysiSZ(HandleIndexContent):
    '''
            主要参股公司分析
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MajorHoldCompaniAnalysiSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['04070000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains("主要业务").any():
                                    df = remove_space_from_df(table)
                                    dfs['joint_stock'] = df
                                elif table.iloc[0, :].str.contains("报告期内取得和处置子公司方式 ").any():
                                    df = remove_space_from_df(table)
                                    dfs['acquisit_and_dispos'] = df
                                else:
                                    pass
                    elif classify == 't' and len(item) > 0 :
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            ret = re.sub('.*?.适用.不适用','',item)
                            if ret != '':
                                instructi.append(ret)
                    else:
                        pass
        else:
            pass

        return dfs,unit,''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs,unit,instructi = self.recognize()
        if len(dfs) > 0:
            if dfs.get('joint_stock') is not None:
                df = dfs.get('joint_stock')

                company_name_pos = list(np.where((df.iloc[0, :] == '公司名称'))[0])
                company_type_pos = list(np.where((df.iloc[0, :].str.contains('公司类型')))[0])
                main_bussi_pos = list(np.where((df.iloc[0, :] == '主要业务'))[0])
                regist_capit_pos = list(np.where((df.iloc[0, :].str.contains('注册资本') ))[0])
                total_asset_pos = list(np.where((df.iloc[0, :].str.contains('总资产')))[0])
                net_asset_pos = list(np.where((df.iloc[0, :].str.contains('净资产')))[0])
                oprtng_incm_pos = list(np.where((df.iloc[0, :].str.contains('营业收入')))[0])
                oprtng_prft_pos = list(np.where((df.iloc[0, :].str.contains('营业利润')))[0])
                net_profit_pos = list(np.where((df.iloc[0, :] == '净利润'))[0])

                df = df.drop([0])

                company_names = list(df.iloc[:, company_name_pos[0]])
                company_types = list(df.iloc[:, company_type_pos[0]])
                main_bussis = list(df.iloc[:, main_bussi_pos[0]])
                regist_capits = list(df.iloc[:, regist_capit_pos[0]])
                total_assets = list(df.iloc[:, total_asset_pos[0]])
                net_assets = list(df.iloc[:, net_asset_pos[0]])
                oprtng_incms = list(df.iloc[:, oprtng_incm_pos[0]])
                oprtng_prfts = list(df.iloc[:, oprtng_prft_pos[0]])
                net_profits = list(df.iloc[:, net_profit_pos[0]])


                for (company_name,company_type,main_bussi,regist_capit,total_asset,net_asset,oprtng_incm,
                     oprtng_prft,net_profit ) \
                        in zip(company_names,company_types,main_bussis,regist_capits,total_assets,net_assets,oprtng_incms,
                               oprtng_prfts,net_profits ):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        company_name=company_name,
                        company_type=company_type,
                        main_bussi=main_bussi,
                        regist_capit=regist_capit,
                        total_asset=num_to_decimal(total_asset, unit),
                        net_asset=num_to_decimal(net_asset, unit),
                        oprtng_incm=num_to_decimal(oprtng_incm, unit),
                        oprtng_prft=num_to_decimal(oprtng_prft, unit),
                        np=num_to_decimal(net_profit, unit),
                    )
                    create_and_update('MajorHoldCompani',**value_dict)
            else:
                pass
            if dfs.get('acquisit_and_dispos') is not None:
                df = dfs.get('acquisit_and_dispos')
                company_name_pos = list(np.where((df.iloc[0, :] == '公司名称'))[0])
                acquisit_and_dispos_pos = list(np.where((df.iloc[0, :].str.contains('报告期内取得和处置子公司方式')))[0])
                impact_on_production_pos = list(np.where((df.iloc[0, :] == '对整体生产经营和业绩的影响 '))[0])

                df = df.drop([0])

                company_names = list(df.iloc[:, company_name_pos[0]])
                acquisit_and_disposes = list(df.iloc[:, acquisit_and_dispos_pos[0]])
                impact_on_productions = list(df.iloc[:, impact_on_production_pos[0]])

                for (company_name,acquisit_and_dispos,impact_on_production) \
                        in zip(company_names,acquisit_and_disposes,impact_on_productions):
                    value_dict = dict(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        company_name=company_name,
                        acquisit_and_dispos=acquisit_and_dispos,
                        impact_on_production=impact_on_production,
                    )
                    create_and_update('AcquisitAndDisposCom',**value_dict)

        save_instructi(instructi,models.BusiSituatDiscussAndAnalysi,self.stk_cd_id,self.acc_per,'main_sharehold_compani_analysi')

class MajorHoldCompaniAnalysi(HandleIndexContent):
    '''
            主要参股公司分析
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MajorHoldCompaniAnalysi, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0402070000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'main_sharehold_compani_analysi')


class IndustriStructurAndTrend(HandleIndexContent):
    '''
            行业结构和趋势分析
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(IndustriStructurAndTrend, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0403010000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'industri_structur_and_trend')

class CompaniDevelopStrategi(HandleIndexContent):
    '''
            公司发展战略
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CompaniDevelopStrategi, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0403020000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'comp_develop_strategi')


class BussiPlan(HandleIndexContent):
    '''
            公司经营计划
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BussiPlan, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0403030000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'bussi_plan')


class PossiblRisk(HandleIndexContent):
    '''
            可能面临的风险
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(PossiblRisk, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0403040000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'possibl_risk')


class ProspectFuture(HandleIndexContent):
    '''
            公司未来发展的展望
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ProspectFuture, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['04090000']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi, models.BusiSituatDiscussAndAnalysi, self.stk_cd_id, self.acc_per,
                       'prospect_future')
