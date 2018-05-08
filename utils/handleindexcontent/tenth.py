# _author : litufu
# date : 2018/4/28

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
import re
import numpy as np
from utils.mytools import HandleIndexContent,remove_space_from_df,remove_per_from_df,similar
from report_data_extract import models
from decimal import Decimal
import decimal
from collections import OrderedDict
from itertools import chain
import pandas as pd

class BasicCorporBond(HandleIndexContent):
    '''
        公司债券基本情况
        '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BasicCorporBond, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0a01000000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('债券').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
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
        if df is not None and len(df) > 0:
            unit_change = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000, '亿元': 100000000}
            bond_name_pos = list(np.where(df.iloc[0, :].str.contains('债券名称'))[0])
            abbrevi_pos = list(np.where(df.iloc[0, :].str.contains('简称'))[0])
            code_pos = list(np.where(df.iloc[0, :].str.contains('代码'))[0])
            releas_date_pos = list(np.where(df.iloc[0, :].str.contains('发行日'))[0])
            expiri_date_pos = list(np.where(df.iloc[0, :].str.contains('到期日'))[0])
            bond_balanc_pos = list(np.where(df.iloc[0, :].str.contains('债券余额'))[0])
            interest_rate_pos = list(np.where(df.iloc[0, :].str.contains('利率'))[0])
            debt_servic_pos = list(np.where(df.iloc[0, :].str.contains('还本付息方式'))[0])
            trade_place_pos = list(np.where(df.iloc[0, :].str.contains('交易场所'))[0])

            df = df.drop([0])
            bond_names = list(df.iloc[:, bond_name_pos[0]])
            abbrevis = list(df.iloc[:, abbrevi_pos[0]])
            codes = list(df.iloc[:, code_pos[0]])
            releas_dates = list(df.iloc[:, releas_date_pos[0]])
            expiri_dates = list(df.iloc[:, expiri_date_pos[0]])
            bond_balancs = list(df.iloc[:, bond_balanc_pos[0]])
            interest_rates = list(df.iloc[:, interest_rate_pos[0]])
            debt_servics = list(df.iloc[:, debt_servic_pos[0]])
            trade_places = list(df.iloc[:, trade_place_pos[0]])

            for (bond_name, abbrevi,code,releas_date,expiri_date,bond_balanc, \
                           interest_rate,debt_servic,trade_place) \
                    in zip(bond_names, abbrevis,codes,releas_dates,expiri_dates,bond_balancs, \
                           interest_rates,debt_servics,trade_places):

                if models.BasicCorporBond.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                    bond_name=bond_name):
                    obj = models.BasicCorporBond.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                                        bond_name=bond_name)
                    obj.bond_name = bond_name
                    obj.abbrevi = abbrevi
                    obj.code = code
                    obj.releas_date = releas_date
                    obj.expiri_date = expiri_date
                    obj.bond_balanc = Decimal(re.sub(',', '', str(bond_balanc))) * unit_change[unit]
                    obj.interest_rate = Decimal(re.sub(',', '', str(interest_rate)))
                    obj.debt_servic = debt_servic
                    obj.trade_place = trade_place
                    obj.save()
                else:
                    models.BasicCorporBond.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        bond_name=bond_name,
                        abbrevi=abbrevi,
                        code=code,
                        releas_date=releas_date,
                        expiri_date=expiri_date,
                        bond_balanc=Decimal(re.sub(',', '', str(bond_balanc))) * unit_change[unit],
                        interest_rate=Decimal(re.sub(',', '', str(interest_rate))),
                        debt_servic=debt_servic,
                        trade_place=trade_place
                    )

class BondManagAndCreditRateAgenc(HandleIndexContent):
    '''
    公司债券受托管理联系人、联系方式及资信评级机构联系方式
    '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BondManagAndCreditRateAgenc, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0a02000000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[:,0].str.contains('债券').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
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
        if df is not None and len(df) > 0:
            bond_man_name_pos = list(np.where((df.iloc[:,0].str.contains('债券受托管理人'))&(df.iloc[:, 1].str.contains('名称')))[0])
            bond_man_addr_pos = list(np.where((df.iloc[:,0].str.contains('债券受托管理人'))&(df.iloc[:, 1].str.contains('办公地址')))[0])
            bond_man_contact_person_pos = list(np.where((df.iloc[:,0].str.contains('债券受托管理人'))&(df.iloc[:, 1].str.contains('联系人')))[0])
            bond_man_contact_tel_pos = list(np.where((df.iloc[:,0].str.contains('债券受托管理人'))&(df.iloc[:, 1].str.contains('联系电话')))[0])
            credit_name_pos = list(np.where((df.iloc[:,0].str.contains('资信评级机构'))&(df.iloc[:, 1].str.contains('名称')))[0])
            credit_addr_pos = list(np.where((df.iloc[:,0].str.contains('资信评级机构'))&(df.iloc[:, 1].str.contains('办公地址')))[0])

            bond_man_names = list(df.iloc[bond_man_name_pos,2])
            bond_man_addrs = list(df.iloc[bond_man_addr_pos,2])
            bond_man_contact_persons = list(df.iloc[bond_man_contact_person_pos,2])
            bond_man_contact_tels = list(df.iloc[bond_man_contact_tel_pos,2])
            credit_names = list(df.iloc[credit_name_pos,2])
            credit_addrs = list(df.iloc[credit_addr_pos,2])

            for (credit_name,credit_addr) \
                    in zip(credit_names,credit_addrs):

                if models.BondManagAndCreditRateAgenc.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                         name=credit_name):
                    obj = models.BondManagAndCreditRateAgenc.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                             name=credit_name)
                    obj.institut_categori = 'credit'
                    obj.name = credit_name
                    obj.addr = credit_addr
                    obj.save()
                else:
                    models.BondManagAndCreditRateAgenc.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        institut_categori = 'credit',
                        name=credit_name,
                        addr=credit_addr,
                    )

            for (bond_man_name,bond_man_addr,bond_man_contact_person,bond_man_contact_tel) \
                    in zip(bond_man_names,bond_man_addrs,bond_man_contact_persons,bond_man_contact_tels):

                if models.BondManagAndCreditRateAgenc.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                         name=bond_man_name):
                    obj = models.BondManagAndCreditRateAgenc.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, \
                                                             name=bond_man_name)
                    obj.institut_categori = 'manager'
                    obj.name = bond_man_name
                    obj.addr = bond_man_addr
                    obj.contact_person = bond_man_contact_person
                    obj.contact_tel = bond_man_contact_tel
                    obj.save()
                else:
                    models.BondManagAndCreditRateAgenc.objects.create(
                        stk_cd_id=self.stk_cd_id,
                        acc_per=self.acc_per,
                        institut_categori = 'manager',
                        name=bond_man_name,
                        addr=bond_man_addr,
                        contact_person=bond_man_contact_person,
                        contact_tel=bond_man_contact_tel,
                    )

class UseOfRaisFund(HandleIndexContent):
    '''
            公司债券募集资金使用情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(UseOfRaisFund, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0a03000000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('债券').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
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
        if len(instructi) > 0:
            if models.BondDesc.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BondDesc.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.use_of_rais_fund = instructi
                obj.save()
            else:
                models.BondDesc.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    use_of_rais_fund=instructi
                )
        else:
            pass

class CorporBondRate(HandleIndexContent):
    '''
            公司债券评级情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CorporBondRate, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0a04000000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('债券').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
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
        if len(instructi) > 0:
            if models.BondDesc.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BondDesc.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.corpor_bond_rate = instructi
                obj.save()
            else:
                models.BondDesc.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    corpor_bond_rate=instructi
                )
        else:
            pass

class CreditEnhancMechanism(HandleIndexContent):
    '''
            债券增信机制、偿债计划及其他相关情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(CreditEnhancMechanism, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0a05000000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('债券').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
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
        if len(instructi) > 0:
            if models.BondDesc.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BondDesc.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.credit_enhanc_mechan = instructi
                obj.save()
            else:
                models.BondDesc.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    credit_enhanc_mechan=instructi
                )
        else:
            pass

class BankCreditCondit(HandleIndexContent):
    '''
            银行授信情况
            '''

    def __init__(self, stk_cd_id, acc_per, indexno, indexcontent):
        super(BankCreditCondit, self).__init__(stk_cd_id, acc_per, indexno, indexcontent)

    def recognize(self):
        df = None
        instructi = []
        unit = '元'
        pattern0 = re.compile('^.*?单位：(.*?)$')
        if self.indexno in ['0a0a000000']:
            for content in self.indexcontent:
                for classify, item in content.items():
                    if classify == 'c' and len(item) > 0:
                        for tables in item:
                            for table in tables:
                                if table.iloc[0, :].str.contains('授信').any():
                                    df = remove_per_from_df(remove_space_from_df(table))
                                    instructi.append(df.to_string())
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
        if len(instructi) > 0:
            if models.BondDesc.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per):
                obj = models.BondDesc.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per)
                obj.bank_credit_condit = instructi
                obj.save()
            else:
                models.BondDesc.objects.create(
                    stk_cd_id=self.stk_cd_id,
                    acc_per=self.acc_per,
                    bank_credit_condit=instructi
                )
        else:
            pass


