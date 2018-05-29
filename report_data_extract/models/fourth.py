# _author : litufu
# date : 2018/4/18

from django.db import models
from .standard import CommonInfo

class BusiSituatDiscussAndAnalysi(CommonInfo):
    busi_situat_discuss = models.TextField(verbose_name='经营情况讨论与分析',default='')
    major_oper_condit = models.TextField(verbose_name='报告期内主要经营情况',default='')
    revenu_and_cost_anal = models.TextField(verbose_name='收入与成本分析',default='')
    industry_product_region = models.TextField(verbose_name='分行业、分产品、分地区主营业务说明',default='')
    product_and_sale = models.TextField(verbose_name='产销量情况说明',default='')
    cost_analysi = models.TextField(verbose_name='成本分析情况说明',default='')
    top_5_custom_and_supplier = models.TextField(verbose_name='前五大客户及供应商说明',default='')
    chang_in_expense = models.TextField(verbose_name='费用变动分析',default='')
    chang_in_cash_flow_statement = models.TextField(verbose_name='现金流量表变动分析',default='')
    balanc_sheet_chang = models.TextField(verbose_name='资产负债表变动分析',default='')
    restrict_asset = models.TextField(verbose_name='受限资产情况说明',default='')
    industri_busi_inform = models.TextField(verbose_name='行业经营性信息分析',default='')
    main_sharehold_compani_analysi = models.TextField(verbose_name='主要参股公司分析',default='')
    industri_structur_and_trend = models.TextField(verbose_name='行业格局和趋势',default='')
    comp_develop_strategi = models.TextField(verbose_name='公司发展战略',default='')
    bussi_plan = models.TextField(verbose_name='公司经营计划',default='')
    possibl_risk = models.TextField(verbose_name='可能面临的风险',default='')
    busi_chang = models.TextField(verbose_name='主营业务调整及变化情况',default='')
    prospect_future = models.TextField(verbose_name='公司未来发展的展望',default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per')

class MainBusiSubIndustry(CommonInfo):
    industry = models.CharField(verbose_name='分行业',max_length=150,default='')
    oprtng_incm = models.DecimalField(verbose_name='营业收入',default=0.00,max_digits=22, decimal_places=2)
    oprtng_cst = models.DecimalField(verbose_name='营业成本',default=0.00,max_digits=22, decimal_places=2)


    class Meta:
        unique_together = ('stk_cd', 'acc_per','industry')

class MainBusiSubProduct(CommonInfo):
    product = models.CharField(verbose_name='分产品',max_length=150,default='')
    oprtng_incm = models.DecimalField(verbose_name='营业收入',default=0.00,max_digits=22, decimal_places=2)
    oprtng_cst = models.DecimalField(verbose_name='营业成本',default=0.00,max_digits=22, decimal_places=2)


    class Meta:
        unique_together = ('stk_cd', 'acc_per','product')

class MainBusiSubRegion(CommonInfo):
    region = models.CharField(verbose_name='分地区',max_length=150,default='')
    oprtng_incm = models.DecimalField(verbose_name='营业收入',default=0.00,max_digits=22, decimal_places=2)
    oprtng_cst = models.DecimalField(verbose_name='营业成本',default=0.00,max_digits=22, decimal_places=2)


    class Meta:
        unique_together = ('stk_cd', 'acc_per','region')

class CostIndustry(CommonInfo):
    industry = models.CharField(verbose_name='分行业',max_length=150,default='')
    cost_composit = models.CharField(verbose_name='成本构成',max_length=120,default='')
    current_period = models.DecimalField(verbose_name='本期金额',default=0.00,max_digits=22, decimal_places=2)
    last_period = models.DecimalField(verbose_name='上期金额', default=0.00,max_digits=22, decimal_places=2)


    class Meta:
        unique_together = ('stk_cd', 'acc_per','industry','cost_composit')

class CostProduct(CommonInfo):
    product = models.CharField(verbose_name='分产品',max_length=150,default='')
    cost_composit = models.CharField(verbose_name='成本构成', max_length=120, default='')
    current_period = models.DecimalField(verbose_name='本期金额', default=0.00,max_digits=22, decimal_places=2)
    last_period = models.DecimalField(verbose_name='上期金额', default=0.00,max_digits=22, decimal_places=2)


    class Meta:
        unique_together = ('stk_cd', 'acc_per','product','cost_composit')

class CostSubRegion(CommonInfo):
    region = models.CharField(verbose_name='分地区',max_length=150,default='')
    cost_composit = models.CharField(verbose_name='成本构成', max_length=120, default='')
    current_period = models.DecimalField(verbose_name='本期金额', default=0.00,max_digits=22, decimal_places=2)
    last_period = models.DecimalField(verbose_name='上期金额', default=0.00,max_digits=22, decimal_places=2)


    class Meta:
        unique_together = ('stk_cd', 'acc_per','region','cost_composit')


class ProductAndSale(CommonInfo):
    product_vol =  models.CharField(verbose_name='生产量',max_length=150,default='')
    sale_vol =  models.CharField(verbose_name='销售量',max_length=150,default='')
    inventori_vol =  models.CharField(verbose_name='库存量',max_length=150,default='')
    main_product =  models.CharField(verbose_name='主要产品',max_length=150,default='')
    unit =  models.CharField(verbose_name='单位',max_length=150,default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','main_product')

class MajorCustomAndSupplie(CommonInfo):
    MAJOR_CLASS = (
        ('custom', 'custom'),
        ('suppli', 'suppli'),
    )
    major_class = models.CharField(verbose_name='客户/供应商', choices=MAJOR_CLASS, max_length=6, blank=True)
    amount = models.DecimalField(verbose_name='前五大金额', default=0.00,max_digits=22, decimal_places=2)
    amount_prop = models.DecimalField(verbose_name='前五大占比', default=0.00,max_digits=22, decimal_places=2)
    amount_relat = models.DecimalField(verbose_name='前五大中关联方金额', default=0.00,max_digits=22, decimal_places=2)
    amount_relat_prop = models.DecimalField(verbose_name='前五大中关联方占比', default=0.00,max_digits=22, decimal_places=2)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','major_class')

class MajorCustomAndSupplieDetail(CommonInfo):
    MAJOR_CLASS = (
        ('custom', 'custom'),
        ('suppli', 'suppli'),
    )
    major_class = models.CharField(verbose_name='客户/供应商',choices=MAJOR_CLASS,max_length=6,blank=True)
    name = models.CharField(verbose_name='名称', max_length=150, default='', blank=True)
    amount = models.DecimalField(verbose_name='金额', default=0.00,max_digits=22, decimal_places=2)
    amount_prop = models.DecimalField(verbose_name='占比', default=0.00,max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','major_class','name')

class ExpensAnalysi(CommonInfo):
    name = models.CharField(verbose_name='费用名称', max_length=150, default='', blank=True)
    change_reason = models.CharField(verbose_name='变动原因说明', max_length=500, default='', blank=True)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','name')

class RDInvest(CommonInfo):
    expens = models.DecimalField(verbose_name='本期费用化研发投入', default=0.00,max_digits=22, decimal_places=2)
    capit = models.DecimalField(verbose_name='本期资本化研发投入', default=0.00,max_digits=22, decimal_places=2)
    total = models.DecimalField(verbose_name='研发投入合计', default=0.00,max_digits=22, decimal_places=2)
    proport_of_incom = models.DecimalField(verbose_name='研发投入总额占营业收入比例', default=0.00,max_digits=10, decimal_places=2)
    staff_number = models.IntegerField(verbose_name='公司研发人员的数量', default=0)
    proport_of_staff = models.DecimalField(verbose_name='研发人员数量占公司总人数的比例', default=0.00,max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('stk_cd', 'acc_per')

class CashFlowAnalysi(CommonInfo):
    item = models.CharField(verbose_name='现金流量表项目', max_length=150, default='', blank=True)
    desc = models.CharField(verbose_name='现金流量表项目变动原因说明', max_length=150, default='', blank=True)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','item')

class AssetAndLiabil(CommonInfo):
    item = models.CharField(verbose_name='现金流量表项目', max_length=150, default='', blank=True)
    desc = models.CharField(verbose_name='现金流量表项目变动原因说明', max_length=150, default='', blank=True)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','item')

class LimitAsset(CommonInfo):
    item = models.CharField(verbose_name='资产项目', max_length=150, default='', blank=True)
    desc = models.CharField(verbose_name='资产受限情况说明', max_length=150, default='', blank=True)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','item')

class OveralInvest(CommonInfo):
    this_period = models.DecimalField(verbose_name='本期投资额', default=0.00, max_digits=22, decimal_places=2)
    last_period = models.DecimalField(verbose_name='上期投资额', default=0.00, max_digits=22, decimal_places=2)

    class Meta:
        unique_together = ('stk_cd', 'acc_per')

class EquitiInvest(CommonInfo):
    name_of_invest_compa = models.CharField(verbose_name='被投资公司名称', default='', max_length=150)
    main_busi = models.CharField(verbose_name='主要业务', default='', max_length=500)
    invest_method = models.CharField(verbose_name='投资方式', default='', max_length=150)
    invest_amount = models.DecimalField(verbose_name='投资金额', default=0.00, max_digits=22, decimal_places=2)
    sharehold_ratio = models.DecimalField(verbose_name='投资比例', default=0.00, max_digits=10, decimal_places=2)
    sourc_of_fund = models.CharField(verbose_name='资金来源', default='', max_length=150)
    partner = models.CharField(verbose_name='合作方', default='', max_length=150)
    invest_period = models.CharField(verbose_name='投资期限', default='', max_length=150)
    product_type = models.CharField(verbose_name='产品类型', default='', max_length=150)
    progress = models.CharField(verbose_name='投资进展', default='', max_length=500)
    expect_revenu = models.DecimalField(verbose_name='预计收益', default=0.00, max_digits=10, decimal_places=2)
    current_invest_gain = models.DecimalField(verbose_name='本期收益', default=0.00, max_digits=10, decimal_places=2)
    involv_litig = models.CharField(verbose_name='是否涉诉', default='', max_length=150)
    date_of_disclosur = models.CharField(verbose_name='披露日期', default='', max_length=150)
    disclosur_index = models.CharField(verbose_name='披露索引', default='', max_length=500)


    class Meta:
        unique_together = ('stk_cd', 'acc_per','name_of_invest_compa')

class SellMajorAsset(CommonInfo):
    TRADE_CLASS = (
        ('asset', 'asset'),
        ('equiti', 'equiti'),
    )
    trade_class = models.CharField(verbose_name='资产/股权', choices=TRADE_CLASS, max_length=6, blank=True)
    trade_partner = models.CharField(verbose_name='交易对方', default='', max_length=150)
    asset_sold = models.CharField(verbose_name='被出售项目', default='', max_length=150)
    sale_day = models.CharField(verbose_name='出售日', default='', max_length=150)
    trade_price = models.DecimalField(verbose_name='交易价格', default=0.00, max_digits=22, decimal_places=2)
    before_net_profit = models.DecimalField(verbose_name='本期初起至出售日为上市公司贡献的净利润', default=0.00, max_digits=22, decimal_places=2)
    impact_of_sale = models.CharField(verbose_name='出售对公司的影响', default='', max_length=500)
    proport_net_profit = models.DecimalField(verbose_name='出售为上市公司贡献的净利润占净利润总额的比例', default=0.00, max_digits=22, decimal_places=2)
    price_principl = models.CharField(verbose_name='出售定价原则', default='', max_length=150)
    relat_transa = models.CharField(verbose_name='是否为关联交易', default='', max_length=150)
    connect_relat = models.CharField(verbose_name='与交易对方的关联关系', default='', max_length=150)
    transfer_of_titl = models.CharField(verbose_name='是否已全部过户', default='', max_length=150)
    debt_transf = models.CharField(verbose_name='所涉及的债权债务是否已全部转移', default='', max_length=500)
    is_on_schedul = models.CharField(verbose_name='是否按计划如期实施', default='', max_length=500)
    date_of_disclosur = models.CharField(verbose_name='披露日期', default='', max_length=150)
    disclosur_index = models.CharField(verbose_name='披露索引', default='', max_length=150)


    class Meta:
        unique_together = ('stk_cd', 'acc_per','trade_class','trade_partner','asset_sold')

class MajorHoldCompani(CommonInfo):
    company_name = models.CharField(verbose_name='公司名称', default='', max_length=150)
    company_type = models.CharField(verbose_name='公司类型', default='', max_length=150)
    main_bussi = models.CharField(verbose_name='主营业务', default='', max_length=500)
    regist_capit = models.CharField(verbose_name='注册资本', default='', max_length=50)
    total_asset = models.DecimalField(verbose_name='总资产', default=0.00, max_digits=22, decimal_places=2)
    net_asset = models.DecimalField(verbose_name='净资产', default=0.00, max_digits=22, decimal_places=2)
    oprtng_incm = models.DecimalField(verbose_name='营业收入', default=0.00, max_digits=22, decimal_places=2)
    oprtng_prft = models.DecimalField(verbose_name='营业利润', default=0.00, max_digits=22, decimal_places=2)
    np = models.DecimalField(verbose_name='净利润', default=0.00, max_digits=22, decimal_places=2)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','company_name')

class AcquisitAndDisposCom(CommonInfo):
    company_name = models.CharField(verbose_name='公司名称', default='', max_length=150)
    acquisit_and_dispos = models.CharField(verbose_name='取得和处置子公司方式', default='', max_length=150)
    impact_on_production = models.CharField(verbose_name='对整体生产经营和业绩的影响', default='', max_length=300)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','company_name')
