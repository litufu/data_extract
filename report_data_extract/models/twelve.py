# _author : litufu
# date : 2018/5/10
from django.db import models
from .standard import CommonInfo
from .eleventh import ReportType

class CompositOfEnterprisGroup(CommonInfo):
    NATURE = (
        ('s', 'subcompani'),
        ('j', 'joint_ventur'),
    )
    natur_of_the_unit = models.CharField(verbose_name='单位性质', max_length=30, choices=NATURE, default='s')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(verbose_name='公司名称',max_length=150,default='')
    main_place_of_busi = models.CharField(verbose_name='主要经营地',max_length=150,default='')
    registr_place = models.CharField(verbose_name='注册地',max_length=150,default='')
    busi_natur = models.CharField(verbose_name='业务性质',max_length=150,default='')
    direct_sharehold = models.CharField(verbose_name='直接持股比例',max_length=150,default='')
    indirect_sharehold = models.CharField(verbose_name='间接持股比例',max_length=150,default='')
    get_method = models.CharField(verbose_name='取得方式',max_length=150,default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep",'natur_of_the_unit', 'name')

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

class