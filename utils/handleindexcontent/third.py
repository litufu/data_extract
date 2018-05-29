# _author : litufu
# date : 2018/4/20
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import re
import numpy as np
from itertools import chain
import pandas as pd

from report_data_extract import models
from utils.handleindexcontent.base import HandleIndexContent
from utils.mytools import remove_space_from_df
from utils.handleindexcontent.commons import recognize_instucti,recognize_df_and_instucti,save_instructi
from utils.handleindexcontent.base import create_and_update

class MajorBusiModelIndu(HandleIndexContent):
    '''
    报告期内公司所从事的主要业务、经营模式及行业情况说明
    '''
    def __init__(self,stk_cd_id,acc_per ,indexno, indexcontent):
        super(MajorBusiModelIndu, self).__init__(stk_cd_id,acc_per,indexno,indexcontent)

    def recognize(self):
        indexnos = ['0301000000','03010000']
        pass

    def converse(self):

        pass


    def logic(self):
        pass

    def save(self):
        df,unit,instructi  = recognize_instucti(self.indexcontent)
        save_instructi(instructi,models.CompaniBusiOverview,self.stk_cd_id,self.acc_per,'major_busi_model_indu')

class MajorChangInMajorAsset(HandleIndexContent):
    '''
    报告期内公司主要资产发生重大变化情况的说明
    '''
    def __init__(self,stk_cd_id,acc_per ,indexno, indexcontent):
        super(MajorChangInMajorAsset, self).__init__(stk_cd_id,acc_per,indexno,indexcontent)

    def recognize(self):
        indexnos = ['0302000000','03020100']
        pass

        contents = []
        table = None
        all_content = {}
        if self.indexno in ['0302000000','03020100']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 't' and len(item) > 0:
                        # 逻辑检验：含有公司的中文名称
                        content = re.sub('.适用.不适用', '', item)
                        contents.append(content)
                    elif classify == 'c' and len(item) > 0:
                        if item[0][0].iloc[0, :].str.contains("说明").any():
                            table = remove_space_from_df(item[0][0])
                    else:
                        pass
        else:
            pass
        all_content['content'] = ''.join(contents)
        all_content['table'] = table
        return all_content



    def converse(self):

        pass


    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None and len(df)>1:
            df = df.drop([0])
            major_assets = list(df.iloc[:,0])
            change_reasons = list(df.iloc[:,len(df.columns)-1])
            for major_asset,change_reason in zip(major_assets,change_reasons):
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    major_asset=major_asset,
                    change_reason=change_reason
                )
                create_and_update('CompaniBusiOverview',**value_dict)
                # if models.CompaniBusiOverview.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                #     obj = models.CompaniBusiOverview.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                #     obj.major_asset = major_asset
                #     obj.change_reason = change_reason
                #     obj.save()
                # else:
                #     models.CompaniBusiOverview.objects.create(
                #         stk_cd_id=self.stk_cd_id,
                #         acc_per=self.acc_per,
                #         major_asset=major_asset,
                #         change_reason=change_reason
                #        )
        else:
            pass
        save_instructi(instructi,models.CompaniBusiOverview,self.stk_cd_id,self.acc_per,'major_chang_in_major_asset')


class MajorOverseaAsset(HandleIndexContent):
    '''
        主要境外资产情况
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(MajorOverseaAsset, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['03020200']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None:
            asset_contentss = list(chain.from_iterable(df.iloc[:,list(np.where(df.iloc[0,:] == '资产的具体内容')[0])].values))
            caus_of_formats = list(chain.from_iterable(df.iloc[:,list(np.where(df.iloc[0,:] == '形成原因')[0])].values))
            asset_sizes = list(chain.from_iterable(df.iloc[:,list(np.where(df.iloc[0,:] == '资产规模')[0])].values))
            locats = list(chain.from_iterable(df.iloc[:,list(np.where(df.iloc[0,:] == '所在地')[0])].values))
            oper_modes = list(chain.from_iterable(df.iloc[:,list(np.where(df.iloc[0,:] == '运营模式')[0])].values))
            control_measurs = list(chain.from_iterable(df.iloc[:,list(np.where(df.iloc[0,:] == '保障资产安全性的控制措施')[0])].values))
            revenu_status = list(chain.from_iterable(df.iloc[:,list(np.where(df.iloc[0,:] == '收益状况')[0])].values))
            proport_of_overseas = list(chain.from_iterable(df.iloc[:,list(np.where(df.iloc[0,:] == '境外资产占公司净资产的比重')[0])].values))
            impair_risks = list(chain.from_iterable(df.iloc[:,list(np.where(df.iloc[0,:] == '是否存在重大减值风险')[0])].values))
            for asset_contents,caus_of_format,asset_size,locat,oper_mode,control_measur,revenu_statu, \
                proport_of_oversea,impair_risk in zip(asset_contentss,caus_of_formats,asset_sizes,locats,
                                                oper_modes,control_measurs,revenu_status,proport_of_overseas,impair_risks):
                if asset_contents == '资产的具体内容':
                    continue
                value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    asset_contents=asset_contents,
                    caus_of_format=caus_of_format,
                    asset_size=asset_size,
                    locat=locat,
                    oper_mode=oper_mode,
                    control_measur=control_measur,
                    revenu_statu=revenu_statu,
                    proport_of_oversea=proport_of_oversea,
                    impair_risk=impair_risk
                )
                create_and_update('MajorOverseaAsset',**value_dict)
                # if models.MajorOverseaAsset.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                #     obj = models.MajorOverseaAsset.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                #     obj.asset_contents = asset_contents
                #     obj.caus_of_format = caus_of_format
                #     obj.asset_size = asset_size
                #     obj.locat = locat
                #     obj.oper_mode = oper_mode
                #     obj.control_measur = control_measur
                #     obj.revenu_statu = revenu_statu
                #     obj.proport_of_oversea = proport_of_oversea
                #     obj.impair_risk = impair_risk
                #     obj.save()
                # else:
                #     models.MajorOverseaAsset.objects.create(
                #         stk_cd_id=self.stk_cd_id,
                #         acc_per=self.acc_per,
                #         asset_contents=asset_contents,
                #         caus_of_format=caus_of_format,
                #         asset_size=asset_size,
                #         locat=locat,
                #         oper_mode=oper_mode,
                #         control_measur=control_measur,
                #         revenu_statu=revenu_statu,
                #         proport_of_oversea=proport_of_oversea,
                #         impair_risk=impair_risk
                #
                #     )
        else:
            pass

class CoreCompetit(HandleIndexContent):
    '''
        报告期内公司主要资产发生重大变化情况的说明
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CoreCompetit, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0303000000','03030000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_instucti(self.indexcontent)
        save_instructi(instructi,models.CompaniBusiOverview,self.stk_cd_id,self.acc_per,'core_competit')

