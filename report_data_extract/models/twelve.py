# _author : litufu
# date : 2018/5/10
from django.db import models
from .standard import CommonInfo
from .eleventh import ReportType,CompanyName,SubjectName

class BusiMergerNotUnderTheSameControl(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CompanyName,on_delete=models.CASCADE,verbose_name='被购买方名称')
    acquisit_time = models.CharField(verbose_name='股权取得时点',default='',max_length=150)
    acquisit_cost = models.DecimalField(verbose_name='股权取得成本', decimal_places=2, max_digits=22, default=0.00)
    acquisit_rate = models.DecimalField(verbose_name='股权取得比例', decimal_places=2, max_digits=22, default=0.00)
    acquisit_style = models.CharField(verbose_name='取得方式',max_length=150,default='')
    purchas_day = models.CharField(verbose_name='购买日',max_length=150,default='')
    purchas_day_determi_basi = models.CharField(verbose_name='购买日的确定依据',max_length=300,default='')
    income = models.DecimalField(verbose_name='购买日至期末被购买方的收入', decimal_places=2, max_digits=22, default=0.00)
    np = models.DecimalField(verbose_name='购买日至期末被购买方的净利润', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '本期发生的非同一控制下企业合并 ：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class BusiMergerUnderTheSameControl(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CompanyName,on_delete=models.CASCADE,verbose_name='被合并方名称')
    acquisit_rate = models.DecimalField(verbose_name='企业合并中取得的权益比例', decimal_places=2, max_digits=22, default=0.00)
    same_control_basi = models.CharField(verbose_name='构成同一控制下企业合并的依据',max_length=150,default='')
    merger_date = models.CharField(verbose_name='合并日',max_length=150,default='')
    merger_date_determi_basi = models.CharField(verbose_name='合并日的确定依据',max_length=300,default='')
    this_income = models.DecimalField(verbose_name='合并当期期初至合并日被合并方的收入', decimal_places=2, max_digits=22, default=0.00)
    this_np = models.DecimalField(verbose_name='合并当期期初至合并日被合并方的净利润', decimal_places=2, max_digits=22, default=0.00)
    before_income = models.DecimalField(verbose_name='比较期间被合并方的收入', decimal_places=2, max_digits=22, default=0.00)
    before_np = models.DecimalField(verbose_name='比较期间被合并方的净利润', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '本年发生的同一控制下企业合并 ：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class ConsolidCostAndGoodwil(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CompanyName, on_delete=models.CASCADE, verbose_name='被购买方名称')
    cash = models.DecimalField(verbose_name='现金', decimal_places=2, max_digits=22, default=0.00)
    non_cash_asset = models.DecimalField(verbose_name='非现金资产的公允价值', decimal_places=2, max_digits=22, default=0.00)
    issu_or_assum_debt = models.DecimalField(verbose_name='发行或承担的债务的公允价值', decimal_places=2, max_digits=22, default=0.00)
    issuanc_of_equiti_secur = models.DecimalField(verbose_name='发行的权益性证券的公允价值', decimal_places=2, max_digits=22, default=0.00)
    or_have_consider = models.DecimalField(verbose_name='或有对价的公允价值', decimal_places=2, max_digits=22, default=0.00)
    share_held_prior_to_the_acquis = models.DecimalField(verbose_name='购买日之前持有的股权于购买日的公允价值', decimal_places=2, max_digits=22, default=0.00)
    other = models.DecimalField(verbose_name='其他', decimal_places=2, max_digits=22, default=0.00)
    total_combin_cost = models.DecimalField(verbose_name='合并成本合计', decimal_places=2, max_digits=22, default=0.00)
    recogniz_net_asset_fair_valu = models.DecimalField(verbose_name='减：取得的可辨认净资产公允价值份额', decimal_places=2, max_digits=22, default=0.00)
    goodwil = models.DecimalField(verbose_name='商誉/合并成本小于取得的可辨认净资产公允价值份额的金额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '合并成本及商誉 ：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class ConsolidCost(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CompanyName, on_delete=models.CASCADE, verbose_name='单位名称')
    cash = models.DecimalField(verbose_name='现金', decimal_places=2, max_digits=22, default=0.00)
    non_cash_asset = models.DecimalField(verbose_name='非现金资产的账面价值', decimal_places=2, max_digits=22, default=0.00)
    issu_or_assum_debt = models.DecimalField(verbose_name='发行或承担的债务的账面价值', decimal_places=2, max_digits=22, default=0.00)
    issuanc_of_equiti_secur = models.DecimalField(verbose_name='发行的权益性证券的面值', decimal_places=2, max_digits=22, default=0.00)
    or_have_consider = models.DecimalField(verbose_name='或有对价', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '合并成本 ：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class AcquireRecognisAssetAndLiab(CommonInfo):
    VALUE_TYPE = (
        ('f', 'fair'),
        ('b', 'book'),
    )

    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    company_name = models.ForeignKey(CompanyName, on_delete=models.CASCADE, verbose_name='公司名称')
    value_type = models.CharField(verbose_name='价值类型', max_length=30, choices=VALUE_TYPE, default='f')
    subject = models.ForeignKey(SubjectName,verbose_name='科目名称', on_delete=models.CASCADE)
    amount = models.DecimalField(verbose_name='金额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'company_name','value_type','subject')

    def __str__(self):
        return '被购买方于购买日可辨认资产、负债 ：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class BookValuOfAssetAndLiabil(CommonInfo):
    VALUE_TYPE = (
        ('m', 'merger_date'),
        ('b', 'before'),
    )

    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    company_name = models.ForeignKey(CompanyName, on_delete=models.CASCADE, verbose_name='公司名称')
    deadlin = models.CharField(verbose_name='截止日期', max_length=30, choices=VALUE_TYPE, default='f')
    subject = models.ForeignKey(SubjectName, verbose_name='科目名称', on_delete=models.CASCADE)
    amount = models.DecimalField(verbose_name='金额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'company_name', 'deadlin', 'subject')

    def __str__(self):
        return '合并日被合并方资产、负债的账面价值 ：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class CompositOfEnterprisGroup(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CompanyName,on_delete=models.CASCADE,verbose_name='公司名称')
    main_place_of_busi = models.CharField(verbose_name='主要经营地',max_length=150,default='')
    registr_place = models.CharField(verbose_name='注册地',max_length=150,default='')
    busi_natur = models.CharField(verbose_name='业务性质',max_length=150,default='')
    direct_sharehold = models.CharField(verbose_name='直接持股比例',max_length=150,default='')
    indirect_sharehold = models.CharField(verbose_name='间接持股比例',max_length=150,default='')
    get_method = models.CharField(verbose_name='取得方式',max_length=150,default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep",'name')

    def __str__(self):
        return '企业集团的构成：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class ImportNonwhollyownSubsidia(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    subcompani_name = models.CharField(verbose_name='子公司名称', max_length=150, default='')
    minor_sharehold = models.CharField(verbose_name='少数股东持股比例', max_length=150, default='')
    profit_attrib_to_minor = models.DecimalField(verbose_name='本期归属于少数股东的损益', decimal_places=2, max_digits=22, default=0.00)
    dividend_to_minor = models.DecimalField(verbose_name='本期向少数股东宣告分派的股利', decimal_places=2, max_digits=22, default=0.00)
    minor_equiti = models.DecimalField(verbose_name='期末少数股东权益余额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'subcompani_name')

    def __str__(self):
        return '重要的非全资子公司：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class MajorNonwhollyownSubsidiaryFinanciInform(CommonInfo):
    BEFORE_END = (
        ('b', 'before'),
        ('e', 'end'),
    )

    SUBJECT = (
        ('1', 'liquid_asset'),#流动资产
        ('2', 'non_curr_asset'),#非流动资产
        ('3', 'total_asset'),#总资产
        ('4', 'current_liabil'),#流动负债
        ('5', 'non_curr_liabil'),#非流动负债
        ('6', 'total_liabil'),#总负债
        ('7', 'oper_incom'),#营业收入
        ('8', 'net_profit'),#净利润
        ('9', 'total_comprehens_incom'),#综合收益总额
        ('10', 'cash_flow_from_oper'),#经营活动现金流
        ('11', 'cash_and_cash_equiva'),#现金及现金等价物
        ('12', 'minor_shareholder_equit'),#少数股东权益
        ('13', 'net_asset'),#净资产
        ('14', 'net_asset_share'),#净资产份额
        ('15', 'adjust'),#调整事项
        ('16', 'goodwil'),#商誉
        ('17', 'intern_transact_unreal_profit'),#内部交易未实现利润
        ('18', 'other_adjust'),#其他调整
        ('19', 'book_value_of_equiti_invest'),#权益投资的账面价值
        ('20', 'fair_value_of_equiti_invest'),#权益投资的公允价值
        ('21', 'financi_expens'),#财务费用
        ('22', 'incom_tax_expens'),#所得税费用
        ('23', 'discontinu_oper_net_profit'),#终止经营的净利润
        ('24', 'other_comprehens_incom'),#其他综合收益
        ('25', 'dividend_receiv'),#收到的股利
    )
    COM_TYPE = (
        ('s', 'subsidiari'),
        ('j', 'joint_ventur'),
        ('p', 'pool'),
    )
    company_type = models.CharField(verbose_name='公司类型', max_length=30, choices=COM_TYPE, default='s')
    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='e')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    subcompani_name = models.CharField(verbose_name='公司名称', max_length=150, default='')
    subject = models.CharField(verbose_name='项目名称', max_length=30, choices=SUBJECT, default='e')
    amount = models.DecimalField(verbose_name='金额', decimal_places=2, max_digits=22,default=0.00)


    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'company_type','before_end','subcompani_name','subject')

    def __str__(self):
        return '重要的非全资子公司财务信息：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class ParentCompaniAndActualControl(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    parent_compani_name = models.CharField(verbose_name='母公司名称', max_length=150, default='')
    registr = models.CharField(verbose_name='注册地', max_length=150, default='')
    busi_natur = models.CharField(verbose_name='业务性质', max_length=150, default='')
    regist_capit = models.DecimalField(verbose_name='注册资本', decimal_places=2, max_digits=22, default=0.00)
    parent_company_share = models.DecimalField(verbose_name='母公司对本企业的持股比例', decimal_places=2, max_digits=22, default=0.00)
    parent_company_vote_right = models.DecimalField(verbose_name='母公司对本企业的表决权比例', decimal_places=2, max_digits=22, default=0.00)
    actual_control = models.CharField(verbose_name='实际控制人', max_length=150, default='')
    desc = models.TextField(verbose_name='说明',default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'parent_compani_name',)

    def __str__(self):
        return '母公司及实际控制人信息：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class OtherRelat(CommonInfo):

    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='其他关联方名称',max_length=150,default='',unique=True)
    relationship = models.CharField(verbose_name='关联关系',max_length=150,default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name',)

    def __str__(self):
        return '其他关联方信息：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class PurchasAndSale(CommonInfo):
    TRANSACT_TYPE = (
        ('s', 'sale'),#销售交易
        ('p', 'purchase'),#采购交易
        ('atdr', 'asset_transfer_debt_restructur'),#资产转让及债务重组交易
    )
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    transact_type = models.CharField( verbose_name='交易类型',choices=TRANSACT_TYPE,default='s',max_length=30)
    name = models.CharField(verbose_name='关联方', max_length=150, default='')
    content = models.CharField(verbose_name='交易内容', max_length=150, default='')
    approv_transact_amou = models.CharField(verbose_name='获批的交易额度', max_length=150, default='')
    is_exceed_amount = models.CharField(verbose_name='是否超过交易额度', max_length=150, default='')
    before = models.DecimalField(verbose_name='上期发生额', decimal_places=2, max_digits=22, default=0.00)
    end = models.DecimalField(verbose_name='本期发生额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'transact_type','name',)

    def __str__(self):
        return '采购或销售关联交易：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class RelatPartiLeas(CommonInfo):
    TRANSACT_TYPE = (
        ('from', 'rent_from'), #承租
        ('to', 'rent_to'), #出租
    )
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    transact_type = models.CharField(verbose_name='交易类型', choices=TRANSACT_TYPE, default='s', max_length=30)
    name = models.CharField(verbose_name='关联方', max_length=150, default='')
    content = models.CharField(verbose_name='交易内容', max_length=150, default='')
    before = models.DecimalField(verbose_name='上期发生额', decimal_places=2, max_digits=22, default=0.00)
    end = models.DecimalField(verbose_name='本期发生额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'transact_type', 'name',)

    def __str__(self):
        return '出租或承租：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class MoneyLend(CommonInfo):
    TRANSACT_TYPE = (
        ('from', 'lend_from'), #借入
        ('to', 'lend_to'), #借出
    )
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    transact_type = models.CharField(verbose_name='交易类型', choices=TRANSACT_TYPE, default='s', max_length=30)
    name = models.CharField(verbose_name='关联方', max_length=150, default='')
    amount = models.DecimalField(verbose_name='拆借金额', decimal_places=2, max_digits=22, default=0.00)
    start_date = models.CharField(verbose_name='起始日', max_length=150, default='')
    expiri_date = models.CharField(verbose_name='到期日', max_length=150, default='')
    desc = models.CharField(verbose_name='说明', max_length=300, default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'transact_type', 'name','amount','start_date','expiri_date')

    def __str__(self):
        return '资金拆借：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class KeyManagStaffRemuner(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='项目', max_length=150, default='')
    end = models.DecimalField(verbose_name='本期发生额', decimal_places=2, max_digits=22, default=0.00)
    before = models.DecimalField(verbose_name='上期发生额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = (
        "stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '关键管理人员薪酬：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class RelatReceivPayabl(CommonInfo):
    TRANSACT_TYPE = (
        ('r', 'receiv'),  # 应收款
        ('p', 'payabl'),  # 应付款
    )
    BEFORE_END = (
        ('b', 'before'),
        ('e', 'end'),
    )
    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='e')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    natur_of_payment = models.CharField(verbose_name='款项性质', choices=TRANSACT_TYPE, default='s', max_length=30)
    name = models.CharField(verbose_name='科目名称', max_length=150, default='')
    relat_parti_name = models.CharField(verbose_name='关联方名称', max_length=150, default='')
    book_value = models.DecimalField(verbose_name='账面余额', decimal_places=2, max_digits=22, default=0.00)
    bad_debt_prepar = models.DecimalField(verbose_name='坏账准备', decimal_places=2, max_digits=22, default=0.00)


    class Meta:
        unique_together = (
        "stk_cd", "acc_per", "typ_rep", 'before_end', 'name', 'natur_of_payment', 'name', 'relat_parti_name')

    def __str__(self):
        return '关联方应收应付款：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class InvestInSubsidiari(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CompanyName, on_delete=models.CASCADE, verbose_name='公司名称')
    before = models.DecimalField(verbose_name='期初余额', decimal_places=2, max_digits=22, default=0.00)
    increase = models.DecimalField(verbose_name='本期增加', decimal_places=2, max_digits=22, default=0.00)
    cut_back = models.DecimalField(verbose_name='本期减少', decimal_places=2, max_digits=22, default=0.00)
    end = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22, default=0.00)
    impair = models.DecimalField(verbose_name='本期计提减值准备', decimal_places=2, max_digits=22, default=0.00)
    impair_balanc = models.DecimalField(verbose_name='减值准备期末余额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '对子公司投资：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class ReturnOnEquitiAndEarnPerShare(CommonInfo):
    TYPE = (
        ('b', 'before_deduct_non_recur'),  # 扣非前
        ('a', 'after_deduct_non_recur'),  # 扣非后
    )
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    gain_or_loss_type = models.CharField(verbose_name='收益类别', choices=TYPE, default='s', max_length=30)
    return_on_equiti = models.DecimalField(verbose_name='净资产收益率', decimal_places=2, max_digits=10, default=0.00)
    basic_earn_per_share = models.DecimalField(verbose_name='基本每股收益', decimal_places=2, max_digits=10, default=0.00)
    dilut_earn_per_share = models.DecimalField(verbose_name='稀释每股收益', decimal_places=2, max_digits=10, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'gain_or_loss_type')

    def __str__(self):
        return '净资产收益率及每股收益：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class TransactImpactInChangeShareOfSubsidiari(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CompanyName, on_delete=models.CASCADE, verbose_name='公司名称')
    project_name = models.CharField(verbose_name='项目名称',default='',max_length=150)
    amount = models.DecimalField(verbose_name='金额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name','project_name')

    def __str__(self):
        return '交易对于少数股东权益及归属于母公司所有者权益的影响：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class ReportDivisFinanciInform(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CompanyName, on_delete=models.CASCADE, verbose_name='报告分部')
    project_name = models.CharField(verbose_name='项目名称', default='', max_length=150)
    amount = models.DecimalField(verbose_name='金额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name', 'project_name')

    def __str__(self):
        return '报告分部的财务信息：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)
