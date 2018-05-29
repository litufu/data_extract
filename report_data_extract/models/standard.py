# _author : litufu
# date : 2018/4/15
from django.db import models

class StdContentIndex(models.Model):
    '''
    标准索引表
    '''
    market = models.CharField(verbose_name='证券市场',max_length=2)
    name = models.CharField(verbose_name='索引名称',max_length=100)
    no_name = models.CharField(verbose_name='含序号名称',max_length=100)
    fatherno = models.CharField(verbose_name='父级别编码',max_length=10)
    level = models.CharField(verbose_name='编码层次',max_length=1)
    selfno = models.CharField(verbose_name='自身编码',max_length=2)
    no = models.CharField(verbose_name='索引完整编号',max_length=10)
    has_child = models.CharField(verbose_name='是否有下一级索引',max_length=1,default='0')

    class Meta:
        unique_together = ('market', 'no',)

class StdCompareIndex(models.Model):
    '''
    标准索引对照表
    '''
    market = models.CharField(verbose_name='证券市场', max_length=2,default='sz')
    fatherno = models.CharField(verbose_name='父级别编码', max_length=10,default='')
    compare_name = models.CharField(verbose_name='索引名称',max_length=100)
    index_name = models.ForeignKey(StdContentIndex,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('market', 'compare_name','fatherno')


class CompanyList(models.Model):
    '''
    上市公司基础信息表
    '''
    code = models.CharField('公司代码',max_length=10,primary_key=True)
    name = models.CharField('公司名称',max_length=10)
    area = models.CharField('所属地区',max_length=10,default='北京')
    industry = models.CharField('所属行业',max_length=10)
    timeToMarket = models.DateField('上市时间')

    class Meta:
        verbose_name = "公司列表"
        verbose_name_plural = "公司列表清单"

    def __str__(self):
        return self.code

class CommonInfo(models.Model):
    '''
    公用信息表
    '''
    stk_cd = models.ForeignKey(CompanyList, on_delete=models.CASCADE, verbose_name='股票代码')
    acc_per = models.DateField('会计期间')

    class Meta:
        abstract = True

    # def __str__(self):
    #     return '股票代码:{},会计期间:{}'.format(self.stk_cd, self.acc_per)



class IndexHandleMethod(models.Model):
    '''
    索引及对应的处理类对应表
    '''
    indexno = models.ForeignKey(StdContentIndex,on_delete=models.CASCADE, verbose_name='索引编码')
    handle_classname = models.CharField(max_length=30,verbose_name='处理类名')

    class Meta:
        unique_together = ('indexno', 'handle_classname')


class StandardTables(models.Model):
    '''
    标准数据储存表
    '''
    tablename = models.CharField(verbose_name='表英文名', max_length=100, blank=True,unique=True)
    table_cn_name = models.CharField(verbose_name='表中文名', max_length=100, blank=True)
    table_desc = models.CharField(verbose_name='表文件描述', max_length=200, blank=True, default='')

class ReportType(models.Model):
    type = models.CharField(verbose_name='报表类型代码',max_length=1,primary_key=True)
    name = models.CharField(verbose_name='报表类型名称',max_length=10)

    class Meta:
        verbose_name = "报表类型"
        verbose_name_plural = "报表类型清单"

    def __str__(self):
        return self.name

class CommonBeforeAndEndName(models.Model):
    SUBJECT = (
        ('interest_receiv', 'interest_receiv'),  # 应收利息
        ('dividend_receiv', 'dividend_receiv'),  # 应收股利
        ('other_receiv_natur', 'other_receiv_natur'),  # 其他应收款性质
        ('noncurr_asset_due_within_one_year', 'noncurr_asset_due_within_one_year'),  # 一年内到期的非流动资产
        ('other_current_asset', 'other_current_asset'),  # 其他流动资产
        ('construct_in_progres', 'construct_in_progres'),  # 在建工程
        ('engin_materi', 'engin_materi'),  # 工程物资
        ('fix_asset_clean_up', 'fix_asset_clean_up'),  # 固定资产清理
        ('unconfirm_defer_incom_tax', 'unconfirm_defer_incom_tax'),  # 未确认递延所得税资产明细
        ('expir_in_the_follow_year', 'expir_in_the_follow_year'),  # 未确认递延所得税资产的可抵扣亏损将于以下年度到期
        ('other_noncurr_asset', 'other_noncurr_asset'),  # 其他非流动资产
        ('shortterm_loan', 'shortterm_loan'),  # 短期借款
        ('financi_liabil_measur_at_fair_valu', 'financi_liabil_measur_at_fair_valu'),  # 以公允价值计量且其变动计入当期损益的金融负债
        ('bill_payabl', 'bill_payabl'),  # 应付票据
        ('account_payabl', 'account_payabl'),  # 应付账款
        ('advanc_receipt', 'advanc_receipt'),  # 预收款项
        ('tax_payabl', 'tax_payabl'),  # 应交税费
        ('interest_payabl', 'interest_payabl'),  # 应付利息
        ('other_payabl', 'other_payabl'),  # 其他应付款
        ('liabil_held_for_sale', 'liabil_held_for_sale'),  # 持有待售负债
        ('noncurr_liabil_due_within_one_year', 'noncurr_liabil_due_within_one_year'),  # 1 年内到期的非流动负债
        ('long_term_loan', 'long_term_loan'),  # 长期借款
        ('bond_payabl', 'bond_payabl'),  # 应付债券
        ('longterm_payabl', 'longterm_payabl'),  # 长期应付款
        ('estim_liabil', 'estim_liabil'),  # 预计负债
        ('other_noncurr_liabi', 'other_noncurr_liabi'),  # 其他非流动负债
        ('undistributed_profit', 'undistributed_profit'),  # 未分配利润
        ('tax_and_surcharg', 'tax_and_surcharg'),  # 税金及附加
        ('sale_expens', 'sale_expens'),  # 销售费用
        ('manag_cost', 'manag_cost'),  # 管理费用
        ('financi_expens', 'financi_expens'),  # 财务费用
        ('asset_impair_loss', 'asset_impair_loss'),  # 资产减值损失
        ('chang_in_fair_valu', 'chang_in_fair_valu'),  # 公允价值变动损益
        ('invest_incom', 'invest_incom'),  # 投资收益
        ('asset_dispos_incom', 'asset_dispos_incom'),  # 资产处置收益
        ('other_incom', 'other_incom'),  # 其他收益
        ('nonoper_incom', 'nonoper_incom'),  # 营业外收入
        ('nonoper_expens', 'nonoper_expens'),  # 营业外支出
        ('incom_tax_expens', 'incom_tax_expens'),  # 所得税费用
        ('receipt_other_busi', 'receipt_other_busi'),  # 收到的其他与经营活动有关的现金
        ('payment_other_busi', 'payment_other_busi'),  # 支付的其他与经营活动有关的现金
        ('receipt_other_invest', 'receipt_other_invest'),  # 收到的其他与投资活动有关的现金
        ('payment_other_invest', 'payment_other_invest'),  # 支付的其他与投资活动有关的现金
        ('receipt_other_financ', 'receipt_other_financ'),  # 收到的其他与筹资活动有关的现金
        ('payment_other_financ', 'payment_other_financ'),  # 支付的其他与筹资活动有关的现金
        ('addit_materi', 'addit_materi'),  # 现金流量表补充资料
        ('composit_of_cash_and_cash_equival', 'composit_of_cash_and_cash_equival'),  # 现金和现金等价物的构成
        ('asset_with_limit_ownership', 'asset_with_limit_ownership'),  # 所有权或使用权受到限制的资产
        ('govern_subsidi', 'govern_subsidi'),  # 政府补助
        ('nonrecur_gain_and_loss', 'nonrecur_gain_and_loss'),  # 非经常性损益
    )
    subject = models.CharField(verbose_name='科目名称', max_length=30, choices=SUBJECT, default='')
    name = models.CharField(verbose_name='项目名称', max_length=150, default='')

class CommonBICEName(models.Model):
    SUBJECT = (
        ('goodwil_impair', 'goodwil_impair'),  # 商誉减值准备
        ('special_payabl', 'special_payabl'),  # 专项应付款
        ('cptl_rsrv', 'cptl_rsrv'),  # 资本公积
        ('stock', 'stock'),  # 库存股
        ('other_comprehens_incom', 'other_comprehens_incom'),  # 其他综合收益
        ('special_reserv', 'special_reserv'),  # 专项储备
        ('surplu_reserv', 'surplu_reserv'),  # 盈余公积


    )
    subject = models.CharField(verbose_name='科目名称', max_length=30, choices=SUBJECT, default='')
    name = models.CharField(verbose_name='项目名称', max_length=150, default='')

class PayablEmployeCompensName(models.Model):
    SUBJECT = (
        ('p', 'PayablEmployeCompens'),  # 应付职工薪酬列示
        ('short', 'ShorttermCompens'),  # 短期薪酬
        ('set', 'SetTheDrawPlanList'),  # 设定提存计划

    )
    subject = models.CharField(verbose_name='科目名称', max_length=30, choices=SUBJECT, default='')
    name = models.CharField(verbose_name='项目名称',max_length=150,default='')

class FixAndIntangAssetType(models.Model):
    name = models.CharField(verbose_name='项目名称',max_length=150,default='',unique=True)

    def __str__(self):
        return '固定资产无形资产类别名称'

class FixAndIntangChangeType(models.Model):
    name = models.CharField(verbose_name='变动类型名称', max_length=150, default='',unique=True)

    def __str__(self):
        return '固定资产无形资产类别名称'

class DeferIncomTaxName(models.Model):
    name = models.CharField(verbose_name='递延所得税资产/负债项目名称',max_length=150,default='',unique=True)

class SubjectName(models.Model):
    name = models.CharField(verbose_name='科目名称', max_length=30, default='',unique=True)

class CurrencName(models.Model):
    name = models.CharField(verbose_name='外币名称', max_length=30, default='',unique=True)


class Subject(models.Model):
    cn_name = models.CharField(verbose_name='中文名称', max_length=150, default='', unique=True)
    en_name = models.CharField(verbose_name='英文名称', max_length=300, default='')
    en_ab_name = models.CharField(verbose_name='英文缩写', max_length=150, default='')
    level = models.CharField(verbose_name='科目层次', max_length=10, default='')
    fatherno = models.CharField(verbose_name='父级编码', max_length=10, default='')
    selfno = models.CharField(verbose_name='自身编码', max_length=10, default='')
    no = models.CharField(verbose_name='索引完整编号', max_length=10, default='')
    desc = models.TextField(verbose_name='描述', default='')