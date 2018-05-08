# _author : litufu
# date : 2018/4/18

from django.db import models
from .standard import CommonInfo


class ImportMatter(CommonInfo):
    cash_dividend_polici = models.TextField(verbose_name='现金分红政策',default='')
    distribute_plan = models.TextField(verbose_name='分配方案',default='')
    commit = models.TextField(verbose_name='承诺事项',default='')
    profit_predict = models.TextField(verbose_name='盈利预测',default='')
    account_firm = models.TextField(verbose_name='聘任、解聘会计师事务所情况',default='')
    relat_transact_desc = models.TextField(verbose_name='关联交易情况',default='')
    big_sale_return_rt = models.TextField(verbose_name='关联交易中大额销货退回的详细情况',default='')
    perf_agre_rt = models.TextField(verbose_name='关联股权收购交易中的业绩约定实现情况',default='')
    other_relat_trade = models.TextField(verbose_name='其他重大关联交易',default='')
    other_major_issu = models.TextField(verbose_name='其他重大事项的说明',default='')
    social_respons_work = models.TextField(verbose_name='社会责任工作情况',default='')
    outsid_of_key_emitt = models.TextField(verbose_name='重点排污单位之外的公司',default='')
    posit_profit_no_divi= models.TextField(verbose_name='报告期内盈利且母公司可供普通股股东分配利润为正但未提出普通股现金红利分配预案的原因',default='')
    purpos_of_profit= models.TextField(verbose_name='公司未分配利润的用途和使用计划',default='')


    class Meta:
        unique_together = ('stk_cd', 'acc_per')

class CashDividendPolici(CommonInfo):
    number_of_bonu_share = models.DecimalField(verbose_name='每10股送红股数（股）',default=0.00,max_digits=22, decimal_places=2)
    number_of_dividend = models.DecimalField(verbose_name='每10股派息数(元)（含税）',default=0.00,max_digits=22, decimal_places=2)
    transfer_increas = models.DecimalField(verbose_name='每10股转增数（股）',default=0.00,max_digits=22, decimal_places=2)
    amount_of_cash_divid = models.DecimalField(verbose_name='现金分红的数额（含税）',default=0.00,max_digits=22, decimal_places=2)
    common_sharehold_np = models.DecimalField(verbose_name='分红年度合并报表中归属于上市公司普通股股东的净利润',default=0.00,max_digits=22, decimal_places=2)
    distribut_ratio = models.DecimalField(verbose_name='占合并报表中归属于上市公司普通股股东的净利润的比率',default=0.00,max_digits=10, decimal_places=2)
    distribut_profit = models.DecimalField(verbose_name='可分配利润',default=0.00,max_digits=10, decimal_places=2)
    prop_of_distribut_profit = models.DecimalField(verbose_name='可分配利润',default=0.00,max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('stk_cd', 'acc_per')

class Commit(CommonInfo):
    background = models.TextField(verbose_name='承诺背景',default='')
    commit_type = models.CharField(verbose_name='承诺类型',max_length=150,default='')
    parti = models.CharField(verbose_name='承诺方',max_length=500,default='')
    content = models.TextField(verbose_name='承诺内容',default='')
    time_and_deadline = models.CharField(verbose_name='承诺时间和期限',max_length=150,default='')
    time = models.CharField(verbose_name='承诺时间',max_length=150,default='')
    deadline = models.CharField(verbose_name='承诺期限',max_length=150,default='')
    is_there_deadline = models.CharField(verbose_name='是否有履行期限',max_length=10,default='')
    is_strictli_perform = models.CharField(verbose_name='是否严格履行',max_length=10,default='')
    reason_for_incomplet = models.TextField(verbose_name='未能严格履行的原因',default='')
    failur_to_perform = models.TextField(verbose_name='未能及时履行应说明下一步计划',default='')
    perform = models.TextField(verbose_name='履行情况',default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','background','commit_type','parti','content')

class ProfitPredict(CommonInfo):
    asset_or_project_nam = models.CharField(verbose_name='盈利预测资产或项目名称',max_length=300,default='')
    start_time = models.CharField(verbose_name='预测起始时间',max_length=100,default='')
    end_time = models.CharField(verbose_name='预测终止时间',max_length=100,default='')
    forecast_perform = models.DecimalField(verbose_name='当期预测业绩',default=0.00,max_digits=22, decimal_places=2)
    actual_result = models.DecimalField(verbose_name='当期实际业绩',default=0.00,max_digits=22, decimal_places=2)
    unpredict_reason = models.TextField(verbose_name='未达预测的原因',default='')
    origin_disclosur_date = models.CharField(verbose_name='原预测披露的日期', max_length=100, default='')
    origin_disclosur_index = models.CharField(verbose_name='原预测披露的索引', max_length=100, default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','asset_or_project_nam')

class AccountFirm(CommonInfo):
    name = models.CharField(verbose_name='境内会计师事务所名称',max_length=150,default='')
    remuner = models.DecimalField(verbose_name='境内会计师事务所报酬',default=0.00,max_digits=22, decimal_places=2)
    audit_period = models.CharField(verbose_name='境内会计师事务所审计年限',max_length=150,default=0)
    intern_control_name = models.CharField(verbose_name='境内会计师事务所名称', max_length=150, default='')
    intern_control_remuner = models.DecimalField(verbose_name='境内会计师事务所报酬', default=0.00, max_digits=22, decimal_places=2)
    cpa_name = models.CharField(verbose_name='境内注册会计师名称', max_length=150, default='')
    cpa_period = models.CharField(verbose_name='境内会计师事务所注册会计师审计服务的连续年限', max_length=150, default=0)
    oversea_name = models.CharField(verbose_name='境外会计师事务所名称', max_length=150, default='')
    oversea_remuner = models.DecimalField(verbose_name='境外会计师事务所报酬', default=0.00, max_digits=22, decimal_places=2)
    oversea_audit_period = models.CharField(verbose_name='境外会计师事务所审计年限', max_length=150, default=0)
    oversea_cpa_name = models.CharField(verbose_name='境外注册会计师名称', max_length=150, default='')


    class Meta:
        unique_together = ('stk_cd', 'acc_per')


class RelatTransact(CommonInfo):
    dealer = models.CharField(verbose_name='关联交易方',max_length=150,default='')
    relationship = models.CharField(verbose_name='关联关系',max_length=150,default='')
    transact_type = models.CharField(verbose_name='关联交易类型',max_length=150,default='')
    transact_content = models.CharField(verbose_name='关联交易内容',max_length=150,default='')
    price_principl = models.CharField(verbose_name='关联交易定价原则',max_length=150,default='')
    trade_price = models.CharField(verbose_name='关联交易价格',max_length=150,default='')
    transact_amount = models.DecimalField(verbose_name='关联交易金额', default=0.00, max_digits=22, decimal_places=2)
    proport_of_similar = models.DecimalField(verbose_name='占同类交易金额的比例', default=0.00, max_digits=22, decimal_places=2)
    approv_transact_amou = models.DecimalField(verbose_name='获批的交易额度', default=0.00, max_digits=22, decimal_places=2)
    exceed_approv_amou = models.CharField(verbose_name='是否超过获批额度 ', default='', max_length=10)
    bill_method = models.CharField(verbose_name='关联交易结算方式', default='', max_length=150)
    market_price = models.CharField(verbose_name='市场价格', default='', max_length=150)
    price_diff_reason = models.CharField(verbose_name='交易价格与市场参考价格差异较大的原因', default='', max_length=300)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','dealer','transact_type','transact_content')

class OtherMajorContract(CommonInfo):
    compani_parti_name = models.CharField(verbose_name='合同订立公司方名称',max_length=150,default='')
    other_side_name = models.CharField(verbose_name='合同订立对方名称',max_length=150,default='')
    subject = models.CharField(verbose_name='合同标的',max_length=300,default='')
    date = models.CharField(verbose_name='合同签订日期',max_length=300,default='')
    book_valu_of_asset = models.CharField(verbose_name='合同涉及资产的账面价值',max_length=300,default='')
    evalu_of_asset = models.CharField(verbose_name='合同涉及资产的评估价值',max_length=300,default='')
    evalu_agenc_name = models.CharField(verbose_name='评估机构名称',max_length=150,default='')
    base_date_of_assess = models.CharField(verbose_name='评估基准日',max_length=150,default='')
    price_principl = models.CharField(verbose_name='定价原则',max_length=150,default='')
    price = models.CharField(verbose_name='交易价格',max_length=150,default='')
    is_relat_trade = models.CharField(verbose_name='是否关联交易',max_length=150,default='')
    relationship = models.CharField(verbose_name='关联关系',max_length=150,default='')
    progress = models.CharField(verbose_name='截至报告期末的执行情况',max_length=300,default='')
    date_of_disclosur = models.CharField(verbose_name='披露日期',max_length=150,default='')
    disclosur_index = models.CharField(verbose_name='披露索引',max_length=150,default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','compani_parti_name','other_side_name','subject')



