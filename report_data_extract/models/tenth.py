# _author : litufu
# date : 2018/4/28

from django.db import models
from .standard import CommonInfo

class BasicCorporBond(CommonInfo):
    bond_name = models.CharField(verbose_name='债券名称',max_length=150,default='')
    abbrevi = models.CharField(verbose_name='简称',max_length=30,default='')
    code = models.CharField(verbose_name='代码',max_length=30,default='')
    releas_date = models.CharField(verbose_name='发行日',max_length=30,default='')
    expiri_date = models.CharField(verbose_name='到期日',max_length=30,default='')
    bond_balanc = models.DecimalField(verbose_name='债券余额',max_digits=22,decimal_places=2,default=0.00)
    interest_rate = models.DecimalField(verbose_name='利率',max_digits=22,decimal_places=2,default=0.00)
    debt_servic = models.CharField(verbose_name='还本付息方式', max_length=30, default='')
    trade_place = models.CharField(verbose_name='交易场所', max_length=30, default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','bond_name')

class BondManagAndCreditRateAgenc(CommonInfo):
    MAJOR_CLASS = (
        ('manager', 'bond_truste'),
        ('credit', 'credit_rate_agenc'),
    )
    institut_categori = models.CharField(verbose_name='债券受托管理人/资信评级机构', choices=MAJOR_CLASS, max_length=15, blank=True)
    name = models.CharField(verbose_name='机构名称',max_length=150, default='')
    addr = models.CharField(verbose_name='机构地址',max_length=150, default='')
    contact_person = models.CharField(verbose_name='联系人',max_length=150, default='')
    contact_tel = models.CharField(verbose_name='联系电话',max_length=150, default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','name')

class BondDesc(CommonInfo):
    use_of_rais_fund = models.TextField(verbose_name='公司债券募集资金使用情况',default='')
    corpor_bond_rate = models.TextField(verbose_name='公司债券评级情况',default='')
    credit_enhanc_mechan = models.TextField(verbose_name='公司债券增信机制、偿债计划及其他相关情况',default='')
    bank_credit_condit = models.TextField(verbose_name='银行授信情况',default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per')
