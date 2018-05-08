# _author : litufu
# date : 2018/4/20
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


class BusiSituatDiscussAndAnalysi(HandleIndexContent):
    '''
    报告期内公司所从事的主要业务、经营模式及行业情况说明
    '''
    def __init__(self,stk_cd_id,acc_per ,indexno, indexcontent):
        super(BusiSituatDiscussAndAnalysi, self).__init__(stk_cd_id,acc_per,indexno,indexcontent)

    def recognize(self):
        contents = []
        if self.indexno in ['0401000000','04010000']:
            for content in self.indexcontent:
                for classify,item in content.items():
                    if classify == 't' and len(item)>0:
                        #逻辑检验：含有公司的中文名称
                        content = re.sub('.适用.不适用','',item)
                        contents.append(content)
                    elif classify == 'c' and len(item)>0:
                        content = remove_space_from_df(item[0][0]).to_string()
                        contents.append(content)
                    else:
                        pass
        else:
            pass
        return ''.join(contents)

    def converse(self):

        pass


    def logic(self):
        pass

    def save(self):
        busi_situat_discuss  = self.recognize()

        if len(busi_situat_discuss)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.busi_situat_discuss = busi_situat_discuss
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    busi_situat_discuss=busi_situat_discuss
                   )
        else:
            pass

class MajorOperConditDureTheReportPe(HandleIndexContent):
    '''
    报告期内主要经营情况
    '''
    def __init__(self,stk_cd_id,acc_per ,indexno, indexcontent):
        super(MajorOperConditDureTheReportPe, self).__init__(stk_cd_id,acc_per,indexno,indexcontent)

    def recognize(self):
        contents = []
        if self.indexno in ['0402000000']:
            for content in self.indexcontent:
                for classify,item in content.items():
                    if classify == 't' and len(item)>0:
                        #逻辑检验：含有公司的中文名称
                        content = re.sub('.适用.不适用','',item)
                        contents.append(content)
                    elif classify == 'c' and len(item)>0:
                        content = remove_space_from_df(item[0][0]).to_string()
                        contents.append(content)
                    else:
                        pass
        else:
            pass
        return ''.join(contents)

    def converse(self):

        pass


    def logic(self):
        pass

    def save(self):
        major_oper_condit  = self.recognize()

        if len(major_oper_condit)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.major_oper_condit = major_oper_condit
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    major_oper_condit=major_oper_condit
                   )
        else:
            pass

class RevenuAndCostAnalysi(HandleIndexContent):
    '''
    收入和成本分析
    '''
    def __init__(self,stk_cd_id,acc_per ,indexno, indexcontent):
        super(RevenuAndCostAnalysi, self).__init__(stk_cd_id,acc_per,indexno,indexcontent)

    def recognize(self):
        contents = []
        if self.indexno in ['0402010100','04020100']:
            for content in self.indexcontent:
                for classify,item in content.items():
                    if classify == 't' and len(item)>0:
                        #逻辑检验：含有公司的中文名称
                        content = re.sub('.适用.不适用','',item)
                        contents.append(content)
                    # elif classify == 'c' and len(item)>0:
                    #     content = remove_space_from_df(item[0]).to_string()
                    #     contents.append(content)
                    else:
                        pass
        else:
            pass
        return ''.join(contents)

    def converse(self):

        pass


    def logic(self):
        pass

    def save(self):
        revenu_and_cost_anal  = self.recognize()

        if len(revenu_and_cost_anal)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.revenu_and_cost_anal = revenu_and_cost_anal
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    revenu_and_cost_anal=revenu_and_cost_anal
                   )
        else:
            pass

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
        unit_change = {'元':1,'千元':1000,'万元':10000,'百万元':1000000,'亿元':100000000}
        if len(dfs)>0:
            df_industri = dfs.get('分行业')
            df_produ = dfs.get('分产品')
            df_region = dfs.get('分地区')
            if df_industri is not None:
                df = df_industri.drop([0])
                industri = list(df.iloc[:,0])
                industri_incom = list(df.iloc[:,1])
                industri_cost = list(df.iloc[:,2])
                for industry, income, cost in zip(industri, industri_incom, industri_cost):
                    if models.MainBusiSubIndustry.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                 industry=industry):
                        obj = models.MainBusiSubIndustry.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                     industry=industry)
                        obj.industry = industry
                        obj.income = Decimal(re.sub(',','',str(income)))*unit_change[unit]
                        obj.cost = Decimal(re.sub(',','',str(cost)))*unit_change[unit]
                        obj.save()
                    else:
                        print(income)
                        print(unit)
                        models.MainBusiSubIndustry.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            industry=industry,
                            income=Decimal(re.sub(',','',str(income)))*unit_change[unit],
                            cost=Decimal(re.sub(',','',str(cost)))*unit_change[unit])
            else:
                pass

            if df_produ is not None:
                df = df_produ.drop([0])
                products = list(df.iloc[:,0])
                product_incom = list(df.iloc[:,1])
                product_cost = list(df.iloc[:,2])
                for product, income, cost in zip(products, product_incom, product_cost):
                    if models.MainBusiSubProduct.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                product=product):
                        obj = models.MainBusiSubProduct.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                    product=product)
                        obj.product = product
                        obj.income = Decimal(str(income))*unit_change[unit]
                        obj.cost = Decimal(str(cost))*unit_change[unit]
                        obj.save()
                    else:
                        models.MainBusiSubProduct.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            product=product,
                            income=Decimal(str(income))*unit_change[unit],
                            cost=Decimal(str(cost))*unit_change[unit])
            else:
                pass

            if df_region is not None:
                df = df_region.drop([0])
                regions = list(df.iloc[:,0])
                region_incom = list(df.iloc[:,1])
                region_cost = list(df.iloc[:,2])
                for region, income, cost in zip(regions, region_incom, region_cost):
                    if models.MainBusiSubRegion.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                region=region):
                        obj = models.MainBusiSubRegion.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                    region=region)
                        obj.region = region
                        obj.income = Decimal(re.sub(',','',str(income)))*unit_change[unit]
                        obj.cost = Decimal(re.sub(',','',str(cost)))*unit_change[unit]
                        obj.save()
                    else:
                        models.MainBusiSubRegion.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            region=region,
                            income=Decimal(re.sub(',','',str(income)))*unit_change[unit],
                            cost=Decimal(re.sub(',','',str(cost)))*unit_change[unit])
            else:
                pass
        else:
            pass

        if len(instructi) > 0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.ipr_instructi = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    ipr_instructi=instructi
                   )
        else:
            pass

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
                        dfs['分行业'] = remove_space_from_df(item[1][0])
                        dfs['分产品'] = remove_space_from_df(item[2][0])
                        dfs['分地区'] = remove_space_from_df(item[3][0])
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
        unit_change = {'元':1,'千元':1000,'万元':10000,'百万元':1000000,'亿元':100000000}
        if len(dfs)>0:
            df_industri = dfs.get('分行业')
            df_produ = dfs.get('分产品')
            df_region = dfs.get('分地区')
            if df_industri is not None:
                df = df_industri
                industri = list(df.iloc[:,0])
                industri_incom = list(df.iloc[:,1])
                for industry, income in zip(industri, industri_incom):
                    if models.MainBusiSubIndustry.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                 industry=industry):
                        obj = models.MainBusiSubIndustry.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                     industry=industry)
                        obj.industry = industry
                        obj.income = Decimal(re.sub(',','',str(income)))*unit_change[unit]
                        obj.save()
                    else:
                        models.MainBusiSubIndustry.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            industry=industry,
                            income=Decimal(re.sub(',','',str(income)))*unit_change[unit],
                        )
            else:
                pass

            if df_produ is not None:
                df = df_produ
                products = list(df.iloc[:,0])
                product_incom = list(df.iloc[:,1])
                for product, income in zip(products, product_incom):
                    if models.MainBusiSubProduct.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                product=product):
                        obj = models.MainBusiSubProduct.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                    product=product)
                        obj.product = product
                        obj.income = Decimal(str(income))*unit_change[unit]
                        obj.save()
                    else:
                        models.MainBusiSubProduct.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            product=product,
                            income=Decimal(str(income))*unit_change[unit])
            else:
                pass

            if df_region is not None:
                df = df_region
                regions = list(df.iloc[:,0])
                region_incom = list(df.iloc[:,1])
                for region, income in zip(regions, region_incom):
                    if models.MainBusiSubRegion.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                region=region):
                        obj = models.MainBusiSubRegion.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                    region=region)
                        obj.region = region
                        obj.income = Decimal(re.sub(',','',str(income)))*unit_change[unit]
                        obj.save()
                    else:
                        models.MainBusiSubRegion.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            region=region,
                            income=Decimal(re.sub(',','',str(income)))*unit_change[unit]
                        )
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
                    if classify == 'c' and len(item) > 0:
                        dfs['分行业'] = remove_space_from_df(item[1][0])
                        dfs['分产品'] = remove_space_from_df(item[2][0])
                        dfs['分地区'] = remove_space_from_df(item[3][0])
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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if len(dfs) > 0:
            df_industri = dfs.get('分行业')
            df_produ = dfs.get('分产品')
            df_region = dfs.get('分地区')
            if df_industri is not None:
                df = df_industri.drop([0])
                industri = list(df.iloc[:, 0])
                industri_incom = list(df.iloc[:, 1])
                industri_cost = list(df.iloc[:, 2])
                for industry, income, cost in zip(industri, industri_incom, industri_cost):
                    if models.MainBusiSubIndustry.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                 industry=industry):
                        obj = models.MainBusiSubIndustry.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                     industry=industry)
                        obj.industry = industry
                        obj.income = Decimal(re.sub(',', '', str(income))) * unit_change[unit]
                        obj.cost = Decimal(re.sub(',', '', str(cost))) * unit_change[unit]
                        obj.save()
                    else:
                        models.MainBusiSubIndustry.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            industry=industry,
                            income=Decimal(re.sub(',', '', str(income))) * unit_change[unit],
                            cost=Decimal(re.sub(',', '', str(cost))) * unit_change[unit])
            else:
                pass

            if df_produ is not None:
                df = df_produ.drop([0])
                products = list(df.iloc[:, 0])
                product_incom = list(df.iloc[:, 1])
                product_cost = list(df.iloc[:, 2])
                for product, income, cost in zip(products, product_incom, product_cost):
                    if models.MainBusiSubProduct.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                product=product):
                        obj = models.MainBusiSubProduct.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                    product=product)
                        obj.product = product
                        obj.income = Decimal(str(income)) * unit_change[unit]
                        obj.cost = Decimal(str(cost)) * unit_change[unit]
                        obj.save()
                    else:
                        models.MainBusiSubProduct.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            product=product,
                            income=Decimal(str(income)) * unit_change[unit],
                            cost=Decimal(str(cost)) * unit_change[unit])
            else:
                pass

            if df_region is not None:
                df = df_region.drop([0])
                regions = list(df.iloc[:, 0])
                region_incom = list(df.iloc[:, 1])
                region_cost = list(df.iloc[:, 2])
                for region, income, cost in zip(regions, region_incom, region_cost):
                    if models.MainBusiSubRegion.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                               region=region):
                        obj = models.MainBusiSubRegion.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                   region=region)
                        obj.region = region
                        obj.income = Decimal(re.sub(',', '', str(income))) * unit_change[unit]
                        obj.cost = Decimal(re.sub(',', '', str(cost))) * unit_change[unit]
                        obj.save()
                    else:
                        models.MainBusiSubRegion.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            region=region,
                            income=Decimal(re.sub(',', '', str(income))) * unit_change[unit],
                            cost=Decimal(re.sub(',', '', str(cost))) * unit_change[unit])
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
                if models.ProductAndSale.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                             main_product=main_product,product_vol=product_vol,
                                                             sale_vol=sale_vol,inventori_vol=inventori_vol):
                    obj = models.ProductAndSale.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                             main_product=main_product,product_vol=product_vol,
                                                             sale_vol=sale_vol,inventori_vol=inventori_vol)
                    obj.main_product = main_product
                    obj.product_vol = product_vol
                    obj.sale_vol = sale_vol
                    obj.inventori_vol = inventori_vol
                    # obj.unit = unit
                    obj.save()
                else:
                    models.ProductAndSale.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        main_product=main_product,
                        product_vol=product_vol,
                        sale_vol=sale_vol,
                        inventori_vol=inventori_vol,
                        # unit=unit,
                    )
        else:
            pass

        if len(instructi) > 0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.psi_instructi = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    psi_instructi=instructi
                   )
        else:
            pass

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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if len(dfs) > 0:
            df_industri = dfs.get('分行业')
            df_produ = dfs.get('分产品')
            df_region = dfs.get('分地区')
            if df_industri is not None:
                df = df_industri.drop([0])
                industri = list(df.iloc[:, 0])
                cost_composits = list(df.iloc[:, 1])
                thiperiods = list(df.iloc[:, 2])
                lastperiods = list(df.iloc[:, 4])
                for industry, cost_composit, thiperiod, lastperiod in zip(industri, cost_composits, thiperiods,lastperiods):
                    if models.CostIndustry.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                 industry=industry,cost_composit=cost_composit):
                        obj = models.CostIndustry.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                     industry=industry,cost_composit=cost_composit)
                        obj.industry = industry
                        obj.cost_composit = cost_composit
                        obj.thiperiod = thiperiod
                        obj.lastperiod = lastperiod
                        obj.save()
                    else:
                        models.CostIndustry.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            industry=industry,
                            cost_composit=cost_composit,
                            thiperiod=thiperiod,
                            lastperiod=lastperiod)
            else:
                pass

            if df_produ is not None:
                df = df_produ.drop([0])
                products = list(df.iloc[:, 0])
                cost_composits = list(df.iloc[:, 1])
                thiperiods = list(df.iloc[:, 2])
                lastperiods = list(df.iloc[:, 4])
                for product, cost_composit, thiperiod, lastperiod in zip(products, cost_composits, thiperiods,lastperiods):
                    if models.CostProduct.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          product=product,cost_composit=cost_composit):
                        obj = models.CostProduct.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              product=product,cost_composit=cost_composit)
                        obj.product = product
                        obj.cost_composit = cost_composit

                        obj.thiperiod = Decimal(str(thiperiod)) * unit_change[unit]
                        obj.lastperiod = Decimal(str(lastperiod)) * unit_change[unit]
                        obj.save()
                    else:
                        models.CostProduct.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            product=product,
                            cost_composit=cost_composit,
                            thiperiod=Decimal(str(thiperiod)) * unit_change[unit],
                            lastperiod=Decimal(str(lastperiod)) * unit_change[unit])
            else:
                pass

            if df_region is not None:
                df = df_region.drop([0])
                regions = list(df.iloc[:, 0])
                cost_composits = list(df.iloc[:, 1])
                thiperiods = list(df.iloc[:, 2])
                lastperiods = list(df.iloc[:, 4])
                for region, cost_composit, thiperiod, lastperiod in zip(regions, cost_composits, thiperiods,lastperiods):
                    if models.CostSubRegion.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           region=region,cost_composit=cost_composit):
                        obj = models.CostSubRegion.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              region=region,cost_composit=cost_composit)
                        obj.region = region
                        obj.cost_composit = cost_composit
                        obj.thiperiod = Decimal(str(thiperiod)) * unit_change[unit]
                        obj.lastperiod = Decimal(str(lastperiod)) * unit_change[unit]
                        obj.save()
                    else:
                        models.CostSubRegion.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            region=region,
                            cost_composit=cost_composit,
                            thiperiod=Decimal(str(thiperiod)) * unit_change[unit],
                            lastperiod=Decimal(str(lastperiod)) * unit_change[unit])
            else:
                pass
        else:
            pass

        if len(instructi) > 0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.psi_instructi = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    psi_instructi=instructi
                   )
        else:
            pass

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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
        if len(dfs) > 0:
            df_industri = dfs.get('分行业')
            df_produ = dfs.get('分产品')
            df_region = dfs.get('分地区')
            if df_industri is not None:
                df = df_industri.drop([0,1])
                industri = list(df.iloc[:, 0])
                cost_composits = list(df.iloc[:, 1])
                thiperiods = list(df.iloc[:, 2])
                lastperiods = list(df.iloc[:, 4])
                for industry, cost_composit, thiperiod, lastperiod in zip(industri, cost_composits, thiperiods,lastperiods):
                    if models.CostIndustry.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                 industry=industry,cost_composit=cost_composit):
                        obj = models.CostIndustry.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                     industry=industry,cost_composit=cost_composit)
                        obj.industry = industry
                        obj.cost_composit = cost_composit
                        obj.thiperiod = Decimal(str(thiperiod)) * unit_change[unit]
                        obj.lastperiod = Decimal(str(lastperiod)) * unit_change[unit]
                        obj.save()
                    else:
                        models.CostIndustry.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            industry=industry,
                            cost_composit=cost_composit,
                            thiperiod=Decimal(str(thiperiod)) * unit_change[unit],
                            lastperiod=Decimal(str(lastperiod)) * unit_change[unit]
                        )
            else:
                pass

            if df_produ is not None:
                df = df_produ.drop([0,1])
                products = list(df.iloc[:, 0])
                cost_composits = list(df.iloc[:, 1])
                thiperiods = list(df.iloc[:, 2])
                lastperiods = list(df.iloc[:, 4])
                for product, cost_composit, thiperiod, lastperiod in zip(products, cost_composits, thiperiods,lastperiods):
                    if models.CostProduct.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          product=product,cost_composit=cost_composit):
                        obj = models.CostProduct.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              product=product,cost_composit=cost_composit)
                        obj.product = product
                        obj.cost_composit = cost_composit
                        obj.thiperiod = Decimal(str(thiperiod)) * unit_change[unit]
                        obj.lastperiod = Decimal(str(lastperiod)) * unit_change[unit]
                        obj.save()
                    else:
                        models.CostProduct.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            product=product,
                            cost_composit=cost_composit,
                            thiperiod=Decimal(str(thiperiod)) * unit_change[unit],
                            lastperiod=Decimal(str(lastperiod)) * unit_change[unit])
            else:
                pass

            if df_region is not None:
                df = df_region.drop([0,1])
                regions = list(df.iloc[:, 0])
                cost_composits = list(df.iloc[:, 1])
                thiperiods = list(df.iloc[:, 2])
                lastperiods = list(df.iloc[:, 4])
                for region, cost_composit, thiperiod, lastperiod in zip(regions, cost_composits, thiperiods,lastperiods):
                    if models.CostSubRegion.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                           region=region,cost_composit=cost_composit):
                        obj = models.CostSubRegion.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              region=region,cost_composit=cost_composit)
                        obj.region = region
                        obj.cost_composit = cost_composit
                        obj.thiperiod = Decimal(str(thiperiod)) * unit_change[unit]
                        obj.lastperiod = Decimal(str(lastperiod)) * unit_change[unit]
                        obj.save()
                    else:
                        models.CostSubRegion.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            region=region,
                            cost_composit=cost_composit,
                            thiperiod=Decimal(str(thiperiod)) * unit_change[unit],
                            lastperiod=Decimal(str(lastperiod)) * unit_change[unit])
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
        contents = []
        if self.indexno in ['04020207']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 't' and len(item) > 0:
                        # 逻辑检验：含有公司的中文名称
                        content = re.sub('.适用.不适用', '', item)
                        contents.append(content)
                    elif classify == 'c' and len(item) > 0:
                        content = remove_space_from_df(item[0][0]).to_string()
                        contents.append(content)
                    else:
                        pass
        else:
            pass
        return ''.join(contents)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        busi_chang = self.recognize()

        if len(busi_chang) > 0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.busi_chang = busi_chang
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    busi_chang=busi_chang
                )
        else:
            pass

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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
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
                    if models.MajorCustomAndSupplieDetail.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          major_class='custom',name=name):
                        obj = models.MajorCustomAndSupplieDetail.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              major_class='custom',name=name)
                        obj.major_class = 'custom'
                        obj.name = name
                        obj.amount = Decimal(re.sub(',','',str(amount)))*unit_change[table_unit_cunstom]
                        obj.amount_prop = amount_prop
                        obj.save()
                    else:
                        models.MajorCustomAndSupplieDetail.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            major_class='custom',
                            name=name,
                            amount=Decimal(re.sub(',','',str(amount)))*unit_change[table_unit_cunstom],
                            amount_prop=amount_prop
                           )
            else:
                pass

            if df_suppli is not None:
                df = df_suppli.drop([0])
                names = list(df.iloc[:, 0])
                amounts = list(df.iloc[:, 1])
                amount_props = list(df.iloc[:, 2])
                for name, amount, amount_prop in zip(names, amounts, amount_props):
                    if models.MajorCustomAndSupplieDetail.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          major_class='suppli',name=name):
                        obj = models.MajorCustomAndSupplieDetail.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              major_class='suppli',name=name)
                        obj.major_class = 'suppli'
                        obj.name = name
                        obj.amount = Decimal(re.sub(',','',str(amount)))*unit_change[table_unit_suppli]
                        obj.amount_prop = amount_prop
                        obj.save()
                    else:
                        models.MajorCustomAndSupplieDetail.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            major_class='suppli',
                            name=name,
                            amount=Decimal(re.sub(',','',str(amount)))*unit_change[table_unit_suppli],
                            amount_prop=amount_prop
                           )
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
            if models.MajorCustomAndSupplie.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                 major_class='custom'):
                obj = models.MajorCustomAndSupplie.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                     major_class='custom')
                obj.major_class = 'custom'
                obj.amount = Decimal(re.sub(',','',str(amount))) * unit_change[amount_unit]
                obj.amount_prop = amount_prop
                obj.amount_relat = Decimal(re.sub(',','',str(amount_relat))) * unit_change[amount_relat_unit]
                obj.amount_relat_prop = amount_relat_prop
                obj.save()
            else:
                models.MajorCustomAndSupplie.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    major_class='custom',
                    amount=Decimal(re.sub(',','',str(amount))) * unit_change[amount_unit],
                    amount_prop=amount_prop,
                    amount_relat=Decimal(re.sub(',','',str(amount_relat))) * unit_change[amount_relat_unit],
                    amount_relat_prop=amount_relat_prop,
                )
        else:
            pass

        if len(instructi_suppli)>0:
            amount = instructi_suppli.get('amount')
            amount_prop = instructi_suppli.get('amount_prop')
            amount_unit = unit.get('suppli_ammount')
            amount_relat = instructi_suppli.get('amount_relat')
            amount_relat_prop = instructi_suppli.get('amount_relat_prop')
            amount_relat_unit = unit.get('suppli_ammount_relat')
            if models.MajorCustomAndSupplie.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                 major_class='suppli'):
                obj = models.MajorCustomAndSupplie.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                     major_class='suppli')
                obj.major_class = 'suppli'
                obj.amount = Decimal(re.sub(',','',str(amount))) * unit_change[amount_unit]
                obj.amount_prop = amount_prop
                obj.amount_relat = Decimal(re.sub(',','',str(amount_relat))) * unit_change[amount_relat_unit]
                obj.amount_relat_prop = amount_relat_prop
                obj.save()
            else:
                models.MajorCustomAndSupplie.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    major_class='suppli',
                    amount=Decimal(re.sub(',','',str(amount))) * unit_change[amount_unit],
                    amount_prop=amount_prop,
                    amount_relat=Decimal(re.sub(',','',str(amount_relat))) * unit_change[amount_relat_unit],
                    amount_relat_prop=amount_relat_prop,
                )
        else:
            pass

        if len(instructi)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.mfcs_instructi = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    mfcs_instructi=instructi
                   )

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
        unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
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
                    if models.MajorCustomAndSupplieDetail.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          major_class='custom',name=name):
                        obj = models.MajorCustomAndSupplieDetail.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              major_class='custom',name=name)
                        obj.major_class = 'custom'
                        obj.name = name
                        obj.amount = Decimal(re.sub(',','',str(amount)))*unit_change[table_unit_cunstom_detail]
                        obj.amount_prop = amount_prop
                        obj.save()
                    else:
                        models.MajorCustomAndSupplieDetail.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            major_class='custom',
                            name=name,
                            amount=Decimal(re.sub(',','',str(amount)))*unit_change[table_unit_cunstom_detail],
                            amount_prop=amount_prop
                           )
            else:
                pass

            if df_suppli_detail is not None:
                df = df_suppli_detail.drop([0])
                names = list(df.iloc[:, 1])
                amounts = list(df.iloc[:, 2])
                amount_props = list(df.iloc[:, 3])
                for name, amount, amount_prop in zip(names, amounts, amount_props):
                    if models.MajorCustomAndSupplieDetail.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                          major_class='suppli',name=name):
                        obj = models.MajorCustomAndSupplieDetail.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                              major_class='suppli',name=name)
                        obj.major_class = 'suppli'
                        obj.name = name
                        obj.amount = Decimal(re.sub(',','',str(amount)))*unit_change[table_unit_suppli_detail]
                        obj.amount_prop = amount_prop
                        obj.save()
                    else:
                        models.MajorCustomAndSupplieDetail.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            major_class='suppli',
                            name=name,
                            amount=Decimal(re.sub(',','',str(amount)))*unit_change[table_unit_suppli_detail],
                            amount_prop=amount_prop
                           )
            else:
                pass
        else:
            pass

        if df_custom is not None and len(df_custom)>0:
            amount = df_custom.iloc[0,1]
            amount_prop = df_custom.iloc[1,1]
            amount_unit = table_unit_cunstom
            # amount_relat = instructi_sale.get('amount_relat')
            amount_relat_prop = df_custom.iloc[2,1]
            # amount_relat_unit = unit.get('sale_ammount_relat')
            if models.MajorCustomAndSupplie.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                 major_class='custom'):
                obj = models.MajorCustomAndSupplie.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                     major_class='custom')
                obj.major_class = 'custom'
                obj.amount = Decimal(re.sub(',','',str(amount))) * unit_change[amount_unit]
                obj.amount_prop = amount_prop
                # obj.amount_relat = Decimal(re.sub(',','',str(amount_relat))) * unit_change[amount_relat_unit]
                obj.amount_relat_prop = amount_relat_prop
                obj.save()
            else:
                models.MajorCustomAndSupplie.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    major_class='custom',
                    amount=Decimal(re.sub(',','',str(amount))) * unit_change[amount_unit],
                    amount_prop=amount_prop,
                    # amount_relat=Decimal(re.sub(',','',str(amount_relat))) * unit_change[amount_relat_unit],
                    amount_relat_prop=amount_relat_prop,
                )
        else:
            pass

        if df_suppli is not None and len(df_suppli)>0:
            amount = df_suppli.iloc[0, 1]
            amount_prop = df_suppli.iloc[1, 1]
            amount_unit = table_unit_suppli
            # amount_relat = instructi_sale.get('amount_relat')
            amount_relat_prop = df_suppli.iloc[2, 1]
            # amount_relat_unit = unit.get('sale_ammount_relat')
            if models.MajorCustomAndSupplie.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                 major_class='suppli'):
                obj = models.MajorCustomAndSupplie.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                     major_class='suppli')
                obj.major_class = 'suppli'
                obj.amount = Decimal(re.sub(',','',str(amount))) * unit_change[amount_unit]
                obj.amount_prop = amount_prop
                # obj.amount_relat = Decimal(re.sub(',','',str(amount_relat))) * unit_change[amount_relat_unit]
                obj.amount_relat_prop = amount_relat_prop
                obj.save()
            else:
                print(amount)
                print(amount_unit)
                models.MajorCustomAndSupplie.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    major_class='suppli',
                    amount=Decimal(re.sub(',','',str(amount))) * unit_change[amount_unit],
                    amount_prop=amount_prop,
                    # amount_relat=Decimal(re.sub(',','',str(amount_relat))) * unit_change[amount_relat_unit],
                    amount_relat_prop=amount_relat_prop,
                )
        else:
            pass

class Expens(HandleIndexContent):
    '''
        费用
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(Expens, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        instructi = ''
        df = None
        pattern = re.compile('^(.适用.不适用)?(单位：.*元)?$')
        if self.indexno in ['0402010200','04020300']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains("说明").any():
                                    df = remove_space_from_df(table)
                                else:
                                    pass
                    elif classify == 't' and len(item) > 0:
                        if pattern.match(item):
                            pass
                        else:
                            instructi = item
                    else:
                        pass
        else:
            pass
        return df, instructi

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df, instructi = self.recognize()
        if len(df) > 0:
            df = df.drop([0])
            names = list(df.iloc[:, 0])
            instructs = list(df.iloc[:, (len(df.columns)-1)])
            for name, instruct in zip(names, instructs):
                if models.ExpensAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                      name=name):
                    obj = models.ExpensAnalysi.objects.get(stk_cd_id=self.stk_cd_id,
                                                                         acc_per=self.acc_per,name=name)
                    obj.name = name
                    obj.instruct = instruct
                    obj.save()
                else:
                    models.ExpensAnalysi.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        name=name,
                        instruct=instruct
                    )
            else:
                pass
        else:
            pass

        if len(instructi) > 0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.ea_instructi = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    ea_instructi=instructi
                )
        else:
            pass

class RDInvest(HandleIndexContent):
    '''
            研发投入情况
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RDInvest, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0402010300']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:, 0].str.contains("研发").any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                else:
                                    pass
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            pass
                    else:
                        pass
        else:
            pass

        return df,unit

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit = self.recognize()
        if df is not None and len(df) > 0:
            unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
            expens = df.iloc[list(np.where((df.iloc[:, 0] == '本期费用化研发投入'))[0])[0],1]
            capit = df.iloc[list(np.where((df.iloc[:, 0] == '本期资本化研发投入'))[0])[0],1]
            total = df.iloc[list(np.where((df.iloc[:, 0] == '研发投入合计'))[0])[0],1]
            proport_of_incom = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发投入总额占营业收入比例')))[0])[0],1]
            staff_number = df.iloc[list(np.where((df.iloc[:, 0].str.contains('公司研发人员的数量')))[0])[0],1]
            proport_of_staff = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发人员数量占公司总人数的比例')))[0])[0],1]
            if models.RDInvest.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.RDInvest.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per)
                obj.expens = Decimal(re.sub(',','',str(expens)))*unit_change[unit]
                obj.capit = Decimal(re.sub(',','',str(capit)))*unit_change[unit]
                obj.total = Decimal(re.sub(',','',str(total)))*unit_change[unit]
                obj.proport_of_incom = Decimal(re.sub(',','',str(proport_of_incom)))
                obj.staff_number = int(float(re.sub(',','',str(staff_number))))
                obj.proport_of_staff = Decimal(re.sub(',','',str(proport_of_staff)))
                obj.save()
            else:
                models.RDInvest.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    expens=Decimal(re.sub(',','',str(expens)))*unit_change[unit],
                    capit=Decimal(re.sub(',','',str(capit)))*unit_change[unit],
                    total=Decimal(re.sub(',','',str(total)))*unit_change[unit],
                    proport_of_incom=Decimal(re.sub(',','',str(proport_of_incom))),
                    staff_number=Decimal(re.sub(',','',str(staff_number))),
                    proport_of_staff=Decimal(re.sub(',','',str(proport_of_staff))),
                )
        else:
            pass

class RDInvestSZ(HandleIndexContent):
    '''
            研发投入情况
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RDInvestSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        pattern0 = re.compile('^.*?单位：(.*?)$')
        contents = []
        unit='元'
        if self.indexno in ['04020400']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:, 0].str.contains("研发").any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                else:
                                    pass
                    elif classify == 't' and len(item) > 0:
                        if pattern0.match(item):
                            unit = pattern0.match(item).groups()[0]
                        else:
                            contents.append(item)
                    else:
                        pass
        else:
            pass

        return df,unit,''.join(contents)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = self.recognize()
        pattern = re.compile('^.*?研发投入金额（(.*?)）.*?$')
        if df is not None and len(df) > 0:
            unit = pattern.match(df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发投入金额')))[0])[0],0]).groups()[0]
            unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
            total = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发投入金额')))[0])[0],1]
            capit = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发投入资本化的金额')))[0])[0],1]
            # total = df.iloc[list(np.where((df.iloc[:, 0] == '研发投入合计'))[0])[0],1]
            proport_of_incom = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发投入占营业收入比例')))[0])[0],1]
            staff_number = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发人员数量')))[0])[0],1]
            proport_of_staff = df.iloc[list(np.where((df.iloc[:, 0].str.contains('研发人员数量占比')))[0])[0],1]
            if models.RDInvest.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.RDInvest.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per)
                # obj.expens = Decimal(re.sub(',','',str(expens)))*unit_change[unit]
                obj.capit = Decimal(re.sub(',','',str(capit)))*unit_change[unit]
                obj.total = Decimal(re.sub(',','',str(total)))*unit_change[unit]
                obj.proport_of_incom = Decimal(re.sub(',','',str(proport_of_incom)))
                obj.staff_number = int(float(re.sub(',','',str(staff_number))))
                obj.proport_of_staff = Decimal(re.sub(',','',str(proport_of_staff)))
                obj.save()
            else:
                models.RDInvest.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    # expens=Decimal(re.sub(',','',str(expens)))*unit_change[unit],
                    capit=Decimal(re.sub(',','',str(capit)))*unit_change[unit],
                    total=Decimal(re.sub(',','',str(total)))*unit_change[unit],
                    proport_of_incom=Decimal(re.sub(',','',str(proport_of_incom))),
                    staff_number=Decimal(re.sub(',','',str(staff_number))),
                    proport_of_staff=Decimal(re.sub(',','',str(proport_of_staff))),
                )
        else:
            pass

class CashFlow(HandleIndexContent):
    '''
            现金流变动
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CashFlow, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0402010400','04020500']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:, 0].str.contains("现金").any():
                                    if table.iloc[0, :].str.contains("说明").any():
                                        df = remove_space_from_df(table)
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

        return df,unit,''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = self.recognize()
        if df is not None and len(df) > 0:
            # unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
            df = df.drop([0])
            items = list(df.iloc[:,0])
            descs = list(df.iloc[:,(len(df.columns)-1)])
            for item,desc in zip(items,descs):
                if models.CashFlowAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,item=item):
                    obj = models.CashFlowAnalysi.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,item=item)
                    obj.item = item
                    obj.desc = desc
                    obj.save()
                else:
                    models.CashFlowAnalysi.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        item=item,
                        desc=desc
                    )
        else:
            pass

        if len(instructi)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.cfa_instructi = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    cfa_instructi=instructi
                   )
        else:
            pass

class AssetAndLiabil(HandleIndexContent):
    '''
            资产负债变动情况说明
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(AssetAndLiabil, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0402030100','04040100']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains("说明").any():
                                    df = remove_space_from_df(table)
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

        return df,unit,''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = self.recognize()
        if df is not None and len(df) > 0:
            # unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
            df = df.drop([0])
            items = list(df.iloc[:,0])
            descs = list(df.iloc[:,(len(df.columns)-1)])
            for item,desc in zip(items,descs):
                if models.AssetAndLiabil.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,item=item):
                    obj = models.AssetAndLiabil.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,item=item)
                    obj.item = item
                    obj.desc = desc
                    obj.save()
                else:
                    models.AssetAndLiabil.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        item=item,
                        desc=desc
                    )
        else:
            pass

        if len(instructi)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.al_instructi = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    al_instructi=instructi
                   )
        else:
            pass

class LimitAsset(HandleIndexContent):
    '''
            资产受限情况说明
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(LimitAsset, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0402030200']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_space_from_df(item[0][0])
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

        return df,unit,''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = self.recognize()
        if df is not None and len(df) > 0:
            # unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
            df = df.drop([0])
            items = list(df.iloc[:,0])
            descs = list(df.iloc[:,(len(df.columns)-1)])
            for item,desc in zip(items,descs):
                if models.LimitAsset.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,item=item):
                    obj = models.LimitAsset.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,item=item)
                    obj.item = item
                    obj.desc = desc
                    obj.save()
                else:
                    models.LimitAsset.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        item=item,
                        desc=desc
                    )
        else:
            pass

        if len(instructi)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.la_instructi = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    la_instructi=instructi
                   )
        else:
            pass

class OveralInvest(HandleIndexContent):
    '''
                投资总体情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(OveralInvest, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['04050100']:
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
            pattern = re.compile('^.*?报告期投资额（(.*?)）.*?$')
            unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
            this_period = df.iloc[1,0]
            last_period = df.iloc[1, 1]
            unit = pattern.match(df.iloc[list(np.where((df.iloc[:, 0].str.contains('报告期投资额')))[0])[0], 0]).groups()[0]
            if models.OveralInvest.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.OveralInvest.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.this_period = Decimal(re.sub(',','',str(this_period)))*unit_change[unit]
                obj.last_period = Decimal(re.sub(',','',str(last_period)))*unit_change[unit]
                obj.save()
            else:
                # print(unit)
                # print(this_period)
                # print(re.sub(',','',str(this_period)))
                models.OveralInvest.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    this_period=Decimal(re.sub(',','',str(this_period)))*unit_change[unit],
                    last_period=Decimal(re.sub(',','',str(last_period)))*unit_change[unit]
                )

class EquitiInvest(HandleIndexContent):
    '''
                股权投资情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(EquitiInvest, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['04050200']:
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
            unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
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
            main_busis = list(df.iloc[:, main_busi_pos[0]])
            invest_methods = list(df.iloc[:, invest_method_pos[0]])
            invest_amounts = list(df.iloc[:, invest_amount_pos[0]])
            sharehold_ratios = list(df.iloc[:, sharehold_ratio_pos[0]])
            sourc_of_funds = list(df.iloc[:, sourc_of_fund_pos[0]])
            partners = list(df.iloc[:, partner_pos[0]])
            invest_periods = list(df.iloc[:, invest_period_pos[0]])
            product_types = list(df.iloc[:, product_type_pos[0]])
            progresses = list(df.iloc[:, progress_pos[0]])
            expect_revenus = list(df.iloc[:, expect_revenu_pos[0]])
            current_invest_gains = list(df.iloc[:, current_invest_gain_pos[0]])
            involv_litigs = list(df.iloc[:, involv_litig_pos[0]])
            date_of_disclosurs = list(df.iloc[:, date_of_disclosur_pos[0]])
            disclosur_indexes = list(df.iloc[:, disclosur_index_pos[0]])

            for (name_of_invest_compa, main_busi,invest_method,invest_amount ,\
                    sharehold_ratio,sourc_of_fund,partner,invest_period,product_type,progress, \
                        expect_revenu,current_invest_gain, involv_litig ,date_of_disclosur, \
                                  disclosur_index ) in zip(name_of_invest_compas, main_busis,invest_methods,invest_amounts ,\
                    sharehold_ratios,sourc_of_funds,partners,invest_periods,product_types,progresses, \
                        expect_revenus,current_invest_gains, involv_litigs ,date_of_disclosurs, \
                                  disclosur_indexes    ):
                if models.EquitiInvest.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, name_of_invest_compa=name_of_invest_compa):
                    obj = models.EquitiInvest.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, name_of_invest_compa=name_of_invest_compa)
                    obj.name_of_invest_compa = name_of_invest_compa
                    obj.main_busi = main_busi
                    obj.invest_method = invest_method
                    obj.invest_amount = Decimal(re.sub(',','',str(invest_amount)))*unit_change[unit]
                    obj.sharehold_ratio = sharehold_ratio
                    obj.sourc_of_fund = sourc_of_fund
                    obj.partner = partner
                    obj.invest_period = invest_period
                    obj.product_type = product_type
                    obj.progress = progress
                    obj.expect_revenu = Decimal(re.sub(',','',str(expect_revenu)))*unit_change[unit]
                    obj.current_invest_gain = Decimal(re.sub(',','',str(current_invest_gain)))*unit_change[unit]
                    obj.involv_litig = involv_litig
                    obj.date_of_disclosur = date_of_disclosur
                    obj.disclosur_index = disclosur_index
                    obj.save()
                else:
                    print(expect_revenu)
                    models.EquitiInvest.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        name_of_invest_compa=name_of_invest_compa,
                        main_busi=main_busi,
                        invest_method=invest_method,
                        invest_amount=Decimal(re.sub(',','',str(invest_amount)))*unit_change[unit],
                        sharehold_ratio=sharehold_ratio,
                        sourc_of_fund=sourc_of_fund,
                        partner=partner,
                        invest_period=invest_period,
                        product_type=product_type,
                        progress=progress,
                        expect_revenu=Decimal(re.sub(',','',str(expect_revenu)))*unit_change[unit],
                        current_invest_gain=Decimal(re.sub(',','',str(current_invest_gain)))*unit_change[unit],
                        involv_litig=involv_litig,
                        date_of_disclosur=date_of_disclosur,
                        disclosur_index=disclosur_index
                    )
        else:
            pass

        # if len(instructi) > 0:
        #     if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
        #         obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
        #         obj.la_instructi = instructi
        #         obj.save()
        #     else:
        #         models.BusiSituatDiscussAndAnalysi.objects.create(
        #             stk_cd_id=self.stk_cd_id,
        #             acc_per=self.acc_per,
        #             la_instructi=instructi
        #         )
        # else:
        #     pass

class SellMajorAsset(HandleIndexContent):
    '''
                    出售重大资产情况,出售重大股权情况
                '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(SellMajorAsset, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['04060100','04060200']:
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
            pattern1 = re.compile('.*?交易价格（(.*?元)）.*?')
            pattern2 = re.compile('.*?本期初起至出售日该.*?为上市公司贡献的净利润（(.*?元)）.*?')
            unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}

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
                if models.SellMajorAsset.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                        trade_class=trade_class,trade_partner=trade_partner,asset_sold=asset_sold):
                    obj = models.SellMajorAsset.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            trade_class=trade_class,trade_partner=trade_partner, asset_sold=asset_sold)
                    obj.trade_class = trade_class
                    obj.trade_partner = trade_partner
                    obj.asset_sold = asset_sold
                    obj.sale_day = sale_day
                    print(trade_price,unit1)
                    obj.trade_price = Decimal(re.sub(',', '', str(trade_price))) * unit_change[unit1]
                    obj.before_net_profit = Decimal(re.sub(',', '', str(before_net_profit))) * unit_change[unit2]
                    obj.impact_of_sale = impact_of_sale
                    obj.proport_net_profit = proport_net_profit
                    obj.price_principl = price_principl
                    obj.relat_transa = relat_transa
                    obj.connect_relat = connect_relat
                    obj.transfer_of_titl = transfer_of_titl
                    obj.debt_transf = debt_transf
                    obj.is_on_schedul = is_on_schedul
                    obj.date_of_disclosur = date_of_disclosur
                    obj.disclosur_index = disclosur_index
                    obj.save()
                else:
                    print(trade_price,unit1)
                    models.SellMajorAsset.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        trade_class=trade_class,
                        trade_partner=trade_partner,
                        asset_sold=asset_sold,
                        sale_day=sale_day,
                        trade_price=Decimal(re.sub(',', '', str(trade_price))) * unit_change[unit1],
                        before_net_profit=Decimal(re.sub(',', '', str(before_net_profit))) * unit_change[unit2],
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
        else:
            pass

class IndustriOperInformAnalysi(HandleIndexContent):
    '''
            行业经营性信息分析
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(IndustriOperInformAnalysi, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0402040000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_space_from_df(item[0][0])
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

        return df,unit,''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = self.recognize()

        if len(instructi)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.ioia_instructi = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    ioia_instructi=instructi
                   )
        else:
            pass

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
                unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}

                name_pos = list(np.where((df.iloc[0, :] == '公司名称'))[0])
                company_type_pos = list(np.where((df.iloc[0, :].str.contains('公司类型')))[0])
                main_bussi_pos = list(np.where((df.iloc[0, :] == '主要业务'))[0])
                regist_capit_pos = list(np.where((df.iloc[0, :].str.contains('注册资本') ))[0])
                total_asset_pos = list(np.where((df.iloc[0, :].str.contains('总资产')))[0])
                net_asset_pos = list(np.where((df.iloc[0, :].str.contains('净资产')))[0])
                oper_incom_pos = list(np.where((df.iloc[0, :].str.contains('营业收入')))[0])
                oper_profit_pos = list(np.where((df.iloc[0, :].str.contains('营业利润')))[0])
                net_profit_pos = list(np.where((df.iloc[0, :] == '净利润'))[0])

                df = df.drop([0])

                names = list(df.iloc[:, name_pos[0]])
                company_types = list(df.iloc[:, company_type_pos[0]])
                main_bussis = list(df.iloc[:, main_bussi_pos[0]])
                regist_capits = list(df.iloc[:, regist_capit_pos[0]])
                total_assets = list(df.iloc[:, total_asset_pos[0]])
                net_assets = list(df.iloc[:, net_asset_pos[0]])
                oper_incoms = list(df.iloc[:, oper_incom_pos[0]])
                oper_profits = list(df.iloc[:, oper_profit_pos[0]])
                net_profits = list(df.iloc[:, net_profit_pos[0]])


                for (name,company_type,main_bussi,regist_capit,total_asset,net_asset,oper_incom, \
                               oper_profit,net_profit ) \
                        in zip(names,company_types,main_bussis,regist_capits,total_assets,net_assets,oper_incoms, \
                               oper_profits,net_profits ):
                    if models.MajorHoldCompani.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            name=name):
                        obj = models.MajorHoldCompani.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                name=name)
                        obj.name = name
                        obj.company_type = company_type
                        obj.main_bussi = main_bussi
                        obj.regist_capit = Decimal(re.sub(',', '', str(regist_capit))) * unit_change[unit]
                        obj.total_asset = Decimal(re.sub(',', '', str(total_asset))) * unit_change[unit]
                        obj.net_asset = Decimal(re.sub(',', '', str(net_asset))) * unit_change[unit]
                        obj.oper_incom = Decimal(re.sub(',', '', str(oper_incom))) * unit_change[unit]
                        obj.oper_profit = Decimal(re.sub(',', '', str(oper_profit))) * unit_change[unit]
                        obj.net_profit = Decimal(re.sub(',', '', str(net_profit))) * unit_change[unit]
                        obj.save()
                    else:
                        models.MajorHoldCompani.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            name=name,
                            company_type=company_type,
                            main_bussi=main_bussi,
                            regist_capit=Decimal(re.sub(',', '', str(regist_capit))) * unit_change[unit],
                            total_asset=Decimal(re.sub(',', '', str(total_asset))) * unit_change[unit],
                            net_asset=Decimal(re.sub(',', '', str(net_asset))) * unit_change[unit],
                            oper_incom=Decimal(re.sub(',', '', str(oper_incom))) * unit_change[unit],
                            oper_profit=Decimal(re.sub(',', '', str(oper_profit))) * unit_change[unit],
                            net_profit=Decimal(re.sub(',', '', str(net_profit))) * unit_change[unit],

                        )
            else:
                pass
            if dfs.get('acquisit_and_dispos') is not None:
                df = dfs.get('acquisit_and_dispos')
                name_pos = list(np.where((df.iloc[0, :] == '公司名称'))[0])
                acquisit_and_dispos_pos = list(np.where((df.iloc[0, :].str.contains('报告期内取得和处置子公司方式')))[0])
                impact_on_production_pos = list(np.where((df.iloc[0, :] == '对整体生产经营和业绩的影响 '))[0])

                df = df.drop([0])

                names = list(df.iloc[:, name_pos[0]])
                acquisit_and_disposes = list(df.iloc[:, acquisit_and_dispos_pos[0]])
                impact_on_productions = list(df.iloc[:, impact_on_production_pos[0]])

                for (name,acquisit_and_dispos,impact_on_production) \
                        in zip(names,acquisit_and_disposes,impact_on_productions):
                    if models.AcquisitAndDisposCom.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            name=name):
                        obj = models.AcquisitAndDisposCom.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                                name=name)
                        obj.name = name
                        obj.acquisit_and_dispos = acquisit_and_dispos
                        obj.impact_on_production = impact_on_production
                        obj.save()
                    else:
                        models.AcquisitAndDisposCom.objects.create(
                            stk_cd_id=self.stk_cd_id,
                            acc_per=self.acc_per,
                            name=name,
                            acquisit_and_dispos=acquisit_and_dispos,
                            impact_on_production=impact_on_production,
                        )




        if len(instructi)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.mhca_instructi = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    mhca_instructi=instructi
                   )
        else:
            pass

class MajorHoldCompaniAnalysi(HandleIndexContent):
    '''
            主要参股公司分析
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MajorHoldCompaniAnalysi, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0402070000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_space_from_df(item[0][0])
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

        return df,unit,''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = self.recognize()

        if len(instructi)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.mhca_instructi = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    mhca_instructi=instructi
                   )
        else:
            pass

class IndustriStructurAndTrend(HandleIndexContent):
    '''
            行业结构和趋势分析
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(IndustriStructurAndTrend, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0403010000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_space_from_df(item[0][0])
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

        return df,unit,''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = self.recognize()

        if len(instructi)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.industri_structur_and_trend = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    industri_structur_and_trend=instructi
                   )
        else:
            pass

class CompaniDevelopStrategi(HandleIndexContent):
    '''
            公司发展战略
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CompaniDevelopStrategi, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0403020000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_space_from_df(item[0][0])
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

        return df,unit,''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = self.recognize()

        if len(instructi)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.comp_develop_strategi = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    comp_develop_strategi=instructi
                   )
        else:
            pass

class BussiPlan(HandleIndexContent):
    '''
            公司经营计划
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BussiPlan, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0403030000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_space_from_df(item[0][0])
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

        return df,unit,''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = self.recognize()

        if len(instructi)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.bussi_plan = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    bussi_plan=instructi
                   )
        else:
            pass

class PossiblRisk(HandleIndexContent):
    '''
            可能面临的风险
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(PossiblRisk, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0403040000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_space_from_df(item[0][0])
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

        return df,unit,''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = self.recognize()

        if len(instructi)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.possibl_risk = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    possibl_risk=instructi
                   )
        else:
            pass

class ProspectFuture(HandleIndexContent):
    '''
            公司未来发展的展望
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ProspectFuture, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['04090000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        df = remove_space_from_df(item[0][0])
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

        return df,unit,''.join(instructi)

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = self.recognize()

        if len(instructi)>0:
            if models.BusiSituatDiscussAndAnalysi.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BusiSituatDiscussAndAnalysi.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.prospect_future = instructi
                obj.save()
            else:
                models.BusiSituatDiscussAndAnalysi.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    prospect_future=instructi
                   )
        else:
            pass