# _author : litufu
# date : 2018/4/18

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import numpy as np
from utils.mytools import remove_space_from_df
from utils.handleindexcontent.base import HandleIndexContent
from report_data_extract import models
from utils.handleindexcontent.commons import save_instructi,recognize_instucti,recognize_df_and_instucti
from utils.handleindexcontent.base import create_and_update


class CompanyInfo(HandleIndexContent):
    '''
    公司信息
    '''
    def __init__(self,stk_cd_id,acc_per ,indexno, indexcontent):
        super(CompanyInfo, self).__init__(stk_cd_id,acc_per,indexno,indexcontent)

    def recognize(self):
        indexnos = ['0201000000']
        pass


    def converse(self):

        pass


    def logic(self):
        pass

    def save(self):
        df,unit,instructi  = recognize_df_and_instucti(self.indexcontent)
        if df is not None:
            chines_name = df.iloc[list(np.where(df.iloc[:,0] == '公司的中文名称')[0]), 1].values[0]
            chines_abbrevi = df.iloc[list(np.where(df.iloc[:, 0] == '公司的中文简称')[0]), 1].values[0]
            foreign_name = df.iloc[list(np.where(df.iloc[:, 0] == '公司的外文名称')[0]), 1].values[0]
            foreign_abbrevi = df.iloc[list(np.where(df.iloc[:, 0] == '公司的外文名称缩写')[0]), 1].values[0]
            legal_repres = df.iloc[list(np.where(df.iloc[:, 0] == '公司的法定代表人')[0]), 1].values[0]
            value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    chines_name=chines_name,
                    chines_abbrevi=chines_abbrevi,
                    foreign_name=foreign_name,
                    foreign_abbrevi=foreign_abbrevi,
                    legal_repres=legal_repres)
            create_and_update('CompaniProfil',**value_dict)
        else:
            pass


class ContactAndContactInf(HandleIndexContent):
    '''
    联系人和联系方式
    '''
    def __init__(self,stk_cd_id,acc_per ,indexno, indexcontent):
        super(ContactAndContactInf, self).__init__(stk_cd_id,acc_per,indexno,indexcontent)

    def recognize(self):
        indexnos = ['0202000000','02020000']
        pass

    def converse(self):

        pass


    def logic(self):
        pass

    def save(self):
        df,unit,instructi  = recognize_df_and_instucti(self.indexcontent)
        if df is not None:
            board_secretary_nam = df.iloc[list(np.where(df.iloc[:, 0] == '姓名')[0]), 1].values[0]
            board_secretary_addr = df.iloc[list(np.where(df.iloc[:, 0] == '联系地址')[0]), 1].values[0]
            board_secretary_tel = df.iloc[list(np.where(df.iloc[:, 0] == '电话')[0]), 1].values[0]
            board_secretary_fax = df.iloc[list(np.where(df.iloc[:, 0] == '传真')[0]), 1].values[0]
            board_secretary_email = df.iloc[list(np.where(df.iloc[:, 0] == '电子信箱')[0]), 1].values[0]
            value_dict = dict(stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    board_secretary_nam=board_secretary_nam,
                    board_secretary_addr=board_secretary_addr,
                    board_secretary_tel=board_secretary_tel,
                    board_secretary_fax=board_secretary_fax,
                    board_secretary_email=board_secretary_email)
            create_and_update('CompaniProfil',**value_dict)
        else:
            pass


class BasicInform(HandleIndexContent):
    '''
        基本情况间接
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BasicInform, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0203000000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None:
            compani_regist_addre = df.iloc[list(np.where(df.iloc[:, 0] == '公司注册地址')[0]), 1].values[0]
            postal_regist = df.iloc[list(np.where(df.iloc[:, 0] == '公司注册地址的邮政编码')[0]), 1].values[0]
            compani_offic_addres = df.iloc[list(np.where(df.iloc[:, 0] == '公司办公地址')[0]), 1].values[0]
            postal_offic = df.iloc[list(np.where(df.iloc[:, 0] == '公司办公地址的邮政编码')[0]), 1].values[0]
            compani_websit = df.iloc[list(np.where(df.iloc[:, 0] == '公司网址')[0]), 1].values[0]
            compani_email = df.iloc[list(np.where(df.iloc[:, 0] == '电子信箱')[0]), 1].values[0]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                compani_regist_addre=compani_regist_addre,
                postal_regist=postal_regist,
                compani_offic_addres=compani_offic_addres,
                postal_offic=postal_offic,
                compani_websit=compani_websit,
                compani_email=compani_email
            )
            create_and_update('CompaniProfil',**value_dict)
        else:
            pass

class ComOtherRelatInform(HandleIndexContent):
    '''
            其他相关资料
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ComOtherRelatInform, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['0206000000']
        pass

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unti,instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None:
            account_firm_name = df.iloc[list(np.where((df.iloc[:, 0].str.contains("会计师事务所"))
                                                    & (df.iloc[:, 1].str.match("名称")))[0]), 2].values[0]
            account_offic_addres = df.iloc[list(np.where((df.iloc[:, 0].str.contains("会计师事务所"))
                                                 & (df.iloc[:, 1].str.match("办公地址")))[0]), 2].values[0]
            sign_accountant_nam = df.iloc[list(np.where((df.iloc[:, 0].str.contains("会计师事务所"))
                                                 & (df.iloc[:, 1].str.match("签字会计师姓名")))[0]), 2].values[0]
            sponsor_name = df.iloc[list(np.where((df.iloc[:, 0].str.contains("保荐机构"))
                                                 & (df.iloc[:, 1].str.match("名称")))[0]), 2].values[0]
            sponsor_addres = df.iloc[list(np.where((df.iloc[:, 0].str.contains("保荐机构"))
                                                 & (df.iloc[:, 1].str.match("办公地址")))[0]), 2].values[0]
            sponsor_repr = df.iloc[list(np.where((df.iloc[:, 0].str.contains("保荐机构"))
                                                 & (df.iloc[:, 1].str.contains("保荐代表人")))[0]), 2].values[0]
            continu_supervis_per = df.iloc[list(np.where((df.iloc[:, 0].str.contains("保荐机构"))
                                                 & (df.iloc[:, 1].str.contains("持续督导的期间")))[0]), 2].values[0]

            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                account_firm_name=account_firm_name,
                account_offic_addres=account_offic_addres,
                sign_accountant_nam=sign_accountant_nam,
                sponsor_name=sponsor_name,
                sponsor_addres=sponsor_addres,
                sponsor_repr=sponsor_repr,
                continu_supervis_per=continu_supervis_per
            )
            create_and_update('CompaniProfil',**value_dict)
        else:
            pass


class CompanyInfoSZ(HandleIndexContent):
    '''
    公司信息
    '''
    def __init__(self,stk_cd_id,acc_per ,indexno, indexcontent):
        super(CompanyInfoSZ, self).__init__(stk_cd_id,acc_per,indexno,indexcontent)

    def recognize(self):
        indexnos = ['02010000']
        pass


    def converse(self):

        pass


    def logic(self):
        pass

    def save(self):
        df,unit,instructi  = recognize_df_and_instucti(self.indexcontent)
        if df is not None:
            chines_name = df.iloc[list(np.where(df.iloc[:,0] == '公司的中文名称')[0]), 1].values[0] if len(list(np.where(df.iloc[:,0] == '公司的中文名称')[0]))==1 else ''
            chines_abbrevi = df.iloc[list(np.where(df.iloc[:, 0] == '公司的中文简称')[0]), 1].values[0] if len(list(np.where(df.iloc[:,0] == '公司的中文简称')[0]))==1 else ''
            foreign_name = df.iloc[list(np.where(df.iloc[:, 0] == '公司的外文名称（如有）')[0]), 1].values[0] if len(list(np.where(df.iloc[:,0] == '公司的外文名称（如有）')[0]))==1 else ''
            foreign_abbrevi = df.iloc[list(np.where(df.iloc[:, 0] == '公司的外文名称缩写（如有）')[0]), 1].values[0] if len(list(np.where(df.iloc[:,0] == '公司的外文名称缩写（如有）')[0]))==1 else ''
            legal_repres = df.iloc[list(np.where(df.iloc[:, 0] == '公司的法定代表人')[0]), 1].values[0] if len(list(np.where(df.iloc[:,0] == '公司的法定代表人')[0]))==1 else ''
            compani_regist_addre = df.iloc[list(np.where(df.iloc[:, 0] == '注册地址')[0]), 1].values[0] if len(list(np.where(df.iloc[:,0] == '注册地址')[0]))==1 else ''
            postal_regist = df.iloc[list(np.where(df.iloc[:, 0] == '注册地址的邮政编码')[0]), 1].values[0] if len(list(np.where(df.iloc[:,0] == '注册地址的邮政编码')[0]))==1 else ''
            compani_offic_addres = df.iloc[list(np.where(df.iloc[:, 0] == '办公地址')[0]), 1].values[0] if len(list(np.where(df.iloc[:,0] == '办公地址')[0]))==1 else ''
            postal_offic = df.iloc[list(np.where(df.iloc[:, 0] == '办公地址的邮政编码')[0]), 1].values[0] if len(list(np.where(df.iloc[:,0] == '办公地址的邮政编码')[0]))==1 else ''
            compani_websit = df.iloc[list(np.where(df.iloc[:, 0].str.contains('网址'))[0]), 1].values[0] if len(list(np.where(df.iloc[:, 0].str.contains('网址'))[0]))==1 else ''
            compani_email = df.iloc[list(np.where(df.iloc[:, 0] == '电子信箱')[0]), 1].values[0] if len(list(np.where(df.iloc[:,0] == '电子信箱')[0]))==1 else ''
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                chines_name=chines_name,
                chines_abbrevi=chines_abbrevi,
                foreign_name=foreign_name,
                foreign_abbrevi=foreign_abbrevi,
                legal_repres=legal_repres,
                postal_regist=postal_regist,
                compani_regist_addre=compani_regist_addre,
                compani_offic_addres=compani_offic_addres,
                postal_offic=postal_offic,
                compani_websit=compani_websit,
                compani_email=compani_email,
            )
            create_and_update('CompaniProfil',**value_dict)
        else:
            pass


class RegistrChang(HandleIndexContent):
    '''
        注册变更情况
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(RegistrChang, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        indexnos = ['02040000']
        pass


    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        df,unit,instructi = recognize_df_and_instucti(self.indexcontent)
        if df is not None:
            organ_code = df.iloc[list(np.where(df.iloc[:, 0] == '组织机构代码')[0]), 1].values[0]
            chang_in_main_busi = df.iloc[list(np.where(df.iloc[:, 0] == '公司上市以来主营业务的变化情况（如有）')[0]), 1].values[0]
            chang_in_control_sha = df.iloc[list(np.where(df.iloc[:, 0] == '历次控股股东的变更情况（如有）')[0]), 1].values[0]
            value_dict = dict(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    organ_code=organ_code,
                    chang_in_main_busi=chang_in_main_busi,
                    chang_in_control_sha=chang_in_control_sha
            )
            create_and_update('CompaniProfil',**value_dict)
        else:
            pass


class ComOtherRelatInformSZ(HandleIndexContent):
    '''
            注册变更情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(ComOtherRelatInformSZ, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        dfs = {}
        if self.indexno in ['02050000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        if item[0][0].iloc[:, 0].str.match("会计师事务所名称").any():
                            df1 = remove_space_from_df(item[0][0])
                            dfs['accout'] = df1
                        elif item[0][0].iloc[:, 0].str.match("财务顾问名称").any():
                            df2 = remove_space_from_df(item[0][0])
                            dfs['sponsor'] = df2
                        else:
                            pass
                    else:
                        pass
        else:
            pass
        return dfs

    def converse(self):

        pass

    def logic(self):
        pass

    def save(self):
        dfs = self.recognize()
        df = dfs.get('accout')
        if df is not None:
            account_firm_name = df.iloc[list(np.where(df.iloc[:, 0] == '会计师事务所名称')[0]), 1].values[0]
            account_offic_addres = df.iloc[list(np.where(df.iloc[:, 0] == '会计师事务所办公地址')[0]), 1].values[0]
            sign_accountant_nam = df.iloc[list(np.where(df.iloc[:, 0] == '签字会计师姓名')[0]), 1].values[0]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                account_firm_name=account_firm_name,
                account_offic_addres=account_offic_addres,
                sign_accountant_nam=sign_accountant_nam
            )
            create_and_update('CompaniProfil',**value_dict)
        else:
            pass

        df1 = dfs.get('sponsor')
        if df1 is not None:
            df = df1.T
            print(df)
            sponsor_name = df.iloc[list(np.where(df.iloc[:, 0] == '财务顾问名称')[0]), 1].values[0]
            sponsor_addres = df.iloc[list(np.where(df.iloc[:, 0] == '财务顾问办公地址')[0]), 1].values[0]
            sponsor_repr = df.iloc[list(np.where(df.iloc[:, 0] == '财务顾问主办人姓名')[0]), 1].values[0]
            continu_supervis_per = df.iloc[list(np.where(df.iloc[:, 0] == '持续督导期间')[0]), 1].values[0]
            value_dict = dict(
                stk_cd_id=self.stk_cd_id,
                acc_per=self.acc_per,
                sponsor_name=sponsor_name,
                sponsor_addres=sponsor_addres,
                sponsor_repr=sponsor_repr,
                continu_supervis_per=continu_supervis_per
            )
            create_and_update('CompaniProfil',**value_dict)
        else:
            pass