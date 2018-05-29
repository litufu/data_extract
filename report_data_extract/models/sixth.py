# _author : litufu
# date : 2018/4/18

from django.db import models
from .standard import CommonInfo

class ChangInShareAndSharehold(CommonInfo):
    '''
    普通股股份变动及股东情况
    '''
    change_desc = models.TextField(verbose_name='普通股股份变动情况说明',default='')
    report_end_sharehold_num = models.IntegerField(verbose_name='截止报告期末普通股股东总数',default=0,blank=True,null=True)
    disclos_last_month_sharehold_num = models.IntegerField(verbose_name='年度报告披露日前上一月末普通股股东总数',default=0,blank=True,null=True)
    sharehold_relat = models.TextField(verbose_name='股东关联关系或一致行动的说明',default='')
    unlimit_sharehold_relat = models.TextField(verbose_name='前 10 名无限售流通股股东之间，以及前 10 名无限售流通股股东和前 10名股东之间关联关系或一致行动的说明',default='')
    secur_issuanc = models.TextField(verbose_name='证券发行情况',default='')
    share_change_desc = models.TextField(verbose_name='公司股份总数及股东结构的变动、公司资产和负债结构的变动情况说明',default='')
    restrict_on_sharehold = models.TextField(verbose_name='控股股东、实际控制人、重组方及其他承诺主体股份限制减持情况',default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per')

class ChangInOrdinariShare(CommonInfo):
    '''
    普通股股份变动情况表
    '''
    PROJECT_CLASS = (
        ('restrict_sale', 'restrict_sale'),
        ('state_hold', 'state_hold'),
        ('state_own_legal_pers', 'state_own_legal_pers'),
        ('other_domest_capit', 'other_domest_capit'),
        ('domest_non_state_own', 'domest_non_state_own'),
        ('domest_natur_person', 'domest_natur_person'),
        ('foreign_hold', 'foreign_hold'),
        ('oversea_legal_person', 'oversea_legal_person'),
        ('oversea_natur_person', 'oversea_natur_person'),
        ('unlimit_sale', 'unlimit_sale'),
        ('rmb_ordinari_share', 'rmb_ordinari_share'),
        ('domest_list_foreign', 'domest_list_foreign'),
        ('overseas_list_foreig', 'overseas_list_foreig'),
        ('others', 'others'),
        ('total_number', 'total_number'),
    )
    name = models.CharField(verbose_name='项目', choices=PROJECT_CLASS, max_length=50, blank=True)
    quantiti_befor_chang = models.IntegerField(verbose_name='变动前数量')
    issu_new_share = models.IntegerField(verbose_name='发行新股')
    give_share = models.IntegerField(verbose_name='送股')
    turnov_from_cpf = models.IntegerField(verbose_name='公积金转股')
    other = models.IntegerField(verbose_name='其他变动')
    subtot_chang = models.IntegerField(verbose_name='变动小计')
    quantiti_after_chang = models.IntegerField(verbose_name='变动后数量')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','name')

class ChangInRestrictSaleOfShare(CommonInfo):
    sharehold_name = models.CharField(verbose_name='股东名称',max_length=150,default='')
    begin = models.IntegerField(verbose_name='年初限售股数',default=0,blank=True,null=True)
    releas = models.IntegerField(verbose_name='本年解除限售股数',default=0,blank=True,null=True)
    increas = models.IntegerField(verbose_name='本年增加限售股数',default=0,blank=True,null=True)
    end = models.IntegerField(verbose_name='年末限售股数', default=0, blank=True, null=True)
    reason = models.CharField(verbose_name='限售原因', max_length=150, default='')
    restrict_sale_date = models.CharField(verbose_name='解除限售日期', max_length=150, default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','sharehold_name')

class TopTenSharehold(CommonInfo):
    sharehold_name = models.CharField(verbose_name='股东名称',max_length=150,default='')
    increas_and_decreas = models.DecimalField(verbose_name='报告期内增减',default=0.00,max_digits=22, decimal_places=2)
    end_hold_num = models.DecimalField(verbose_name='期末持股数量',default=0.00,max_digits=22, decimal_places=2)
    ratio = models.DecimalField(verbose_name='比例',default=0.00,max_digits=22, decimal_places=2)
    restrict_share = models.DecimalField(verbose_name='持有有限售条件股份数量',default=0.00,max_digits=22, decimal_places=2)
    pledg_or_freez_status = models.CharField(verbose_name='质押或冻结情况',max_length=150,default='')
    pledg_or_freez_num = models.CharField(verbose_name='质押或冻结数量',max_length=150,default='')
    natur_of_sharehold = models.CharField(verbose_name='股东性质',max_length=150,default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','sharehold_name')

class TopTenUnlimitSharehold(CommonInfo):
    sharehold_name = models.CharField(verbose_name='股东名称',max_length=150,default='')
    hold_num = models.DecimalField(verbose_name='持有无限售条件流通股的数量',default=0.00,max_digits=22, decimal_places=2)
    type = models.CharField(verbose_name='股份种类',max_length=150,default='')
    type_num = models.DecimalField(verbose_name='股份种类数量',default=0.00,max_digits=22, decimal_places=2)


    class Meta:
        unique_together = ('stk_cd', 'acc_per','sharehold_name')

class ShareholdCorpor(CommonInfo):
    '''
    法人控股
    '''
    TYPE_CLASS = (
        ('cs', 'control_sharehold'),
        ('ac', 'actual_control_sharehold'),
        ('os', 'other_corpor_sharehold_more_than_ten'),
    )
    type = models.CharField(verbose_name='控股股东/实际控制人/其他超过10%的股东', choices=TYPE_CLASS, max_length=50, blank=True)
    name = models.CharField(verbose_name='名称', max_length=150, default='')
    unit_owner = models.CharField(verbose_name='单位负责人或法定代表人', max_length=150, default='')
    date_of_establish = models.CharField(verbose_name='成立日期', max_length=150, default='')
    main_busines = models.TextField(verbose_name='主要经营业务', default='')
    regist_capit = models.CharField(verbose_name='注册资本',max_length=150, default='')
    control_other_list_com = models.TextField(verbose_name='报告期内控股和参股的其他境内外上市公司的股权情况', default='')
    other_desc = models.TextField(verbose_name='其他情况说明', default='')


    class Meta:
        unique_together = ('stk_cd', 'acc_per')

class ControlShareholdNaturPerson(CommonInfo):
    '''
    自然人控股
    '''
    TYPE_CLASS = (
        ('cs', 'control_sharehold'),
        ('ac', 'actual_control_sharehold'),
    )
    type = models.CharField(verbose_name='控股股东/实际控制人', choices=TYPE_CLASS, max_length=50, blank=True)
    name = models.CharField(verbose_name='名称', max_length=150, default='')
    countri_of_citizensh = models.CharField(verbose_name='国籍', max_length=150, default='')
    other_right_of_abod = models.CharField(verbose_name='是否取得其他国家或地区居留权', max_length=150, default='')
    chang_date = models.CharField(verbose_name='变更日期', max_length=150, default='')
    major_occup_and_job = models.TextField(verbose_name='主要职业及职务', default='')
    control_other_list_com = models.TextField(verbose_name='报告期内控股和参股的其他境内外上市公司的股权情况', default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per')

class SecurIssuanc(CommonInfo):
    '''
    证券发行情况
    '''
    TYPE_CLASS = (
        ('stock', 'stock'),
        ('bond', 'bond'),
        ('deriv_secur', 'deriv_secur'),
    )
    type = models.CharField(verbose_name='股票/债券/衍生证券', choices=TYPE_CLASS, max_length=20, blank=True)
    stock = models.CharField(verbose_name='股票及其衍生证券名称',max_length=150,default='')
    date = models.CharField(verbose_name='发行日期',max_length=150,default='')
    price = models.CharField(verbose_name='发行价格（或利率）',max_length=150,default='')
    num = models.CharField(verbose_name='发行数量',max_length=150,default='')
    to_market_date = models.CharField(verbose_name='上市日期',max_length=150,default='')
    number_permit_trade = models.CharField(verbose_name='获准上市交易数量',max_length=150,default='')
    transact_termin_date = models.CharField(verbose_name='交易终止日期',max_length=150,default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','type','stock','date')
