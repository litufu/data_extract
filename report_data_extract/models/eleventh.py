# _author : litufu
# date : 2018/5/1

from django.db import models
from .standard import CommonInfo

class AuditReport(CommonInfo):
    type_of_opinion = models.CharField(verbose_name='审计意见类型',max_length=30,default='')
    date = models.CharField(verbose_name='审计报告签署日期',max_length=30,default='')
    report_num = models.CharField(verbose_name='审计报告文号',max_length=50,default='')
    full_text = models.TextField(verbose_name='审计报告全文',default='')
    opinion =  models.TextField(verbose_name='非标准审计意见',default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','report_num')

class KeySegment(CommonInfo):
    audit_report = models.ForeignKey(AuditReport,on_delete=models.CASCADE)
    title = models.CharField(verbose_name='关键事项段标题',default='',max_length=150)
    matter_descript = models.TextField(verbose_name='关键审计事项描述',default='')
    audit_respons = models.TextField(verbose_name='审计应对',default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','audit_report','title')

class ReportType(models.Model):
    type = models.CharField(verbose_name='报表类型代码',max_length=1,primary_key=True)
    name = models.CharField(verbose_name='报表类型名称',max_length=10)

    class Meta:
        verbose_name = "报表类型"
        verbose_name_plural = "报表类型清单"

    def __str__(self):
        return self.name

class BalanceSheet(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    before_end = models.CharField(verbose_name='期初期末',max_length=30,choices=BEFORE_END,default='end')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    cash = models.DecimalField('货币资金', max_digits=26, decimal_places=2, default=0.00)
    stlmnt_rsrv_fnd = models.DecimalField('结算备付金', max_digits=26, decimal_places=2, default=0.00)
    lnd_t_bnk = models.DecimalField('拆出资金', max_digits=26, decimal_places=2, default=0.00)
    fncl_ast_hld_fr_trd = models.DecimalField('以公允价值计量且其变动计入当期损益的金融资产', max_digits=26, decimal_places=2, default=0.00)
    drvtv_fncl_ast = models.DecimalField('衍生金融资产', max_digits=26, decimal_places=2, default=0.00)
    bll_rcvbl = models.DecimalField('应收票据', max_digits=26, decimal_places=2, default=0.00)
    acnt_rcvbl = models.DecimalField('应收账款', max_digits=26, decimal_places=2, default=0.00)
    prepayments = models.DecimalField('预付款项', max_digits=26, decimal_places=2, default=0.00)
    rcvbl_prm = models.DecimalField('应收保费', max_digits=26, decimal_places=2, default=0.00)
    acnt_rcvbl_rnsrnc = models.DecimalField('应收分保账款', max_digits=26, decimal_places=2, default=0.00)
    rnsrnc_cntrct_reserve = models.DecimalField('应收分保合同准备金', max_digits=26, decimal_places=2, default=0.00)
    intrst_rcvbl = models.DecimalField('应收利息', max_digits=26, decimal_places=2, default=0.00)
    dvdnd_rcvbl = models.DecimalField('应收股利', max_digits=26, decimal_places=2, default=0.00)
    othr_accnt_rcvbl = models.DecimalField('其他应收款', max_digits=26, decimal_places=2, default=0.00)
    by_bck_sl_of_fnncl_ast = models.DecimalField('买入返售金融资产', max_digits=26, decimal_places=2, default=0.00)
    invntrs = models.DecimalField('存货', max_digits=26, decimal_places=2, default=0.00)
    hld_fr_sl_ast = models.DecimalField('持有待售资产', max_digits=26, decimal_places=2, default=0.00)
    nn_crnt_ast_ds_wthn_on_yr = models.DecimalField('一年内到期的非流动资产', max_digits=26, decimal_places=2, default=0.00)
    othr_crrnt_assts = models.DecimalField('其他流动资产', max_digits=26, decimal_places=2, default=0.00)
    ttl_crrnt_assts = models.DecimalField('流动资产合计', max_digits=26, decimal_places=2, default=0.00)
    lns_and_advncs = models.DecimalField('发放委托贷款及垫款', max_digits=26, decimal_places=2, default=0.00)
    avlbl_fr_sl_fnncl_assts = models.DecimalField('可供出售金融资产', max_digits=26, decimal_places=2, default=0.00)
    hld_t_mtrty_invstmnts = models.DecimalField('持有至到期投资', max_digits=26, decimal_places=2, default=0.00)
    lng_trm_rcvbls = models.DecimalField('长期应收款', max_digits=26, decimal_places=2, default=0.00)
    lng_trm_eqty_rcvbls = models.DecimalField('长期股权投资', max_digits=26, decimal_places=2, default=0.00)
    invnstmnt_prpnrty = models.DecimalField('投资性房地产', max_digits=26, decimal_places=2, default=0.00)
    fxd_assts = models.DecimalField('固定资产', max_digits=26, decimal_places=2, default=0.00)
    cnstrctn_in_prcss = models.DecimalField('在建工程', max_digits=26, decimal_places=2, default=0.00)
    engnr_mtrls = models.DecimalField('工程物资', max_digits=26, decimal_places=2, default=0.00)
    dspsl_of_fxd_assnts = models.DecimalField('固定资产清理', max_digits=26, decimal_places=2, default=0.00)
    prdctv_blgcl_assts = models.DecimalField('生产性生物资产', max_digits=26, decimal_places=2, default=0.00)
    ol_and_gs_assts = models.DecimalField('油气资产', max_digits=26, decimal_places=2, default=0.00)
    intngbl_assts = models.DecimalField('无形资产', max_digits=26, decimal_places=2, default=0.00)
    r_d_expnss = models.DecimalField('开发支出', max_digits=26, decimal_places=2, default=0.00)
    goodwill = models.DecimalField('商誉', max_digits=26, decimal_places=2, default=0.00)
    lng_trm_dfrrd_expns = models.DecimalField('长期待摊费用', max_digits=26, decimal_places=2, default=0.00)
    dfrrd_tx_assts = models.DecimalField('递延所得税资产', max_digits=26, decimal_places=2, default=0.00)
    othr_nn_crrnt_assts = models.DecimalField('其他非流动资产', max_digits=26, decimal_places=2, default=0.00)
    ttl_nn_crrnt_assts = models.DecimalField('非流动资产合计', max_digits=26, decimal_places=2, default=0.00)
    ttl_assts = models.DecimalField('资产总计', max_digits=26, decimal_places=2, default=0.00)
    shrt_trm_ln = models.DecimalField('短期借款  ', max_digits=26, decimal_places=2, default=0.00)
    brrwng_frm_th_cntrl_bnk = models.DecimalField('向中央银行借款', max_digits=26, decimal_places=2, default=0.00)
    absrptn_of_dpsts = models.DecimalField('吸收存款及同业存放', max_digits=26, decimal_places=2, default=0.00)
    lns_frm_othr_bnks = models.DecimalField('拆入资金', max_digits=26, decimal_places=2, default=0.00)
    fnncl_lblts_hld_fr_trd = models.DecimalField('以公允价值计量且其变动计入当期损益的金融负债', max_digits=26, decimal_places=2,
                                                 default=0.00)
    drvtv_fnncl_lblts = models.DecimalField('衍生金融负债', max_digits=26, decimal_places=2, default=0.00)
    blls_pybl = models.DecimalField('应付票据', max_digits=26, decimal_places=2, default=0.00)
    accnts_pybl = models.DecimalField('应付账款', max_digits=26, decimal_places=2, default=0.00)
    accnt_rcvd_in_advnc = models.DecimalField('预收款项', max_digits=26, decimal_places=2, default=0.00)
    fnncl_assts_sld_fr_rprchs = models.DecimalField('卖出回购金融资产款', max_digits=26, decimal_places=2, default=0.00)
    hndlng_fe_and_cmmssn = models.DecimalField('应付手续费及佣金', max_digits=26, decimal_places=2, default=0.00)
    emply_bnfts_pybl = models.DecimalField('应付职工薪酬', max_digits=26, decimal_places=2, default=0.00)
    txs_pybl = models.DecimalField('应交税费', max_digits=26, decimal_places=2, default=0.00)
    intrst_pybl = models.DecimalField('应付利息', max_digits=26, decimal_places=2, default=0.00)
    dvdnd_pybl = models.DecimalField('应付股利', max_digits=26, decimal_places=2, default=0.00)
    othr_accnt_pybl = models.DecimalField('其他应付款', max_digits=26, decimal_places=2, default=0.00)
    accnts_pybl_rnsrnc = models.DecimalField('应付分保账款', max_digits=26, decimal_places=2, default=0.00)
    rsrv_fnd_fr_insrnc_cntrcts = models.DecimalField('保险合同准备金', max_digits=26, decimal_places=2, default=0.00)
    actng_sl_of_scrts = models.DecimalField('代理买卖证券款', max_digits=26, decimal_places=2, default=0.00)
    actng_undrwrtng_scrts = models.DecimalField('代理承销证券款', max_digits=26, decimal_places=2, default=0.00)
    hld_fr_sl_dbt = models.DecimalField('持有待售负债', max_digits=26, decimal_places=2, default=0.00)
    nn_crnt_lblts_ds_wthn_on_yr = models.DecimalField('一年内到期的非流动负债', max_digits=26, decimal_places=2, default=0.00)
    othr_crrnt_lnlts = models.DecimalField('其他流动负债', max_digits=26, decimal_places=2, default=0.00)
    ttl_crrnt_lblts = models.DecimalField('流动负债合计', max_digits=26, decimal_places=2, default=0.00)
    lng_trm_ln = models.DecimalField('长期借款', max_digits=26, decimal_places=2, default=0.00)
    bnd_pybl = models.DecimalField('应付债券', max_digits=26, decimal_places=2, default=0.00)
    lng_trm_accnt_pybl = models.DecimalField('长期应付款', max_digits=26, decimal_places=2, default=0.00)
    lng_trm_emply_bnfts_pybl = models.DecimalField('长期应付职工薪酬', max_digits=26, decimal_places=2, default=0.00)
    spcfc_accnt_pybl = models.DecimalField('专项应付款', max_digits=26, decimal_places=2, default=0.00)
    estmtd_lblty = models.DecimalField('预计负债', max_digits=26, decimal_places=2, default=0.00)
    dfrrd_incm = models.DecimalField('递延收益', max_digits=26, decimal_places=2, default=0.00)
    dfrrd_tx_lblts = models.DecimalField('递延所得税负债', max_digits=26, decimal_places=2, default=0.00)
    othr_nn_crrnt_lblts = models.DecimalField('其他非流动负债', max_digits=26, decimal_places=2, default=0.00)
    ttl_nn_crrnt_lblts = models.DecimalField('非流动负债合计', max_digits=26, decimal_places=2, default=0.00)
    ttl_lblts = models.DecimalField('负债合计', max_digits=26, decimal_places=2, default=0.00)
    pd_n_cptl = models.DecimalField('股本', max_digits=26, decimal_places=2, default=0.00)
    othr_eqty_instrmnts = models.DecimalField('其他权益工具', max_digits=26, decimal_places=2, default=0.00)
    cptl_rsrv = models.DecimalField('资本公积', max_digits=26, decimal_places=2, default=0.00)
    lss_trsry_shr = models.DecimalField('减：库存股', max_digits=26, decimal_places=2, default=0.00)
    othr_cmprhnsv_incm = models.DecimalField('其他综合收益', max_digits=26, decimal_places=2, default=0.00)
    spcl_rsrv = models.DecimalField('专项储备', max_digits=26, decimal_places=2, default=0.00)
    srpls_rsrv = models.DecimalField('盈余公积', max_digits=26, decimal_places=2, default=0.00)
    gnrl_rsk_prprtn = models.DecimalField('一般风险准备', max_digits=26, decimal_places=2, default=0.00)
    undstrbtd_prft = models.DecimalField('未分配利润', max_digits=26, decimal_places=2, default=0.00)
    atrbt_t_ownrs_eqty_of_prnt = models.DecimalField('归属于母公司股东权益合计', max_digits=26, decimal_places=2, default=0.00)
    mnrty_eqty = models.DecimalField('少数股东权益', max_digits=26, decimal_places=2, default=0.00)
    ttl_ownrs_eqty = models.DecimalField('股东权益合计', max_digits=26, decimal_places=2, default=0.00)
    ttl_lblts_and_ownrs_eqty = models.DecimalField('负债和股东权益总计', max_digits=26, decimal_places=2, default=0.00)

    def check_logic(self):
        #流动资产校验
        c_ttl_crrnt_assts = self.cash + self.stlmnt_rsrv_fnd + self.lnd_t_bnk + self.fncl_ast_hld_fr_trd + self.drvtv_fncl_ast \
        +self.bll_rcvbl +self.acnt_rcvbl +self.prepayments +self.rcvbl_prm +self.acnt_rcvbl_rnsrnc + self.rnsrnc_cntrct_reserve\
        +self.intrst_rcvbl + self.dvdnd_rcvbl + self.othr_accnt_rcvbl + self.by_bck_sl_of_fnncl_ast +self.invntrs\
        +self.nn_crnt_ast_ds_wthn_on_yr +self.hld_fr_sl_ast +self.othr_crrnt_assts == self.ttl_crrnt_assts
        #非流动资产校验
        c_ttl_nn_crrnt_assts = self.lns_and_advncs + self.avlbl_fr_sl_fnncl_assts + self.hld_t_mtrty_invstmnts + self.lng_trm_rcvbls \
        + self.lng_trm_eqty_rcvbls +self.invnstmnt_prpnrty + self.fxd_assts + self.cnstrctn_in_prcss + self.engnr_mtrls \
        +self.dspsl_of_fxd_assnts +self.prdctv_blgcl_assts +self.ol_and_gs_assts + self.intngbl_assts +self.r_d_expnss \
        +self.goodwill + self.lng_trm_dfrrd_expns + self.dfrrd_tx_assts + self.othr_nn_crrnt_assts == self.ttl_nn_crrnt_assts
        #资产校验
        c_ttl_assts = self.ttl_crrnt_assts + self.ttl_nn_crrnt_assts == self.ttl_assts
        #流动负债校验
        c_ttl_crrnt_lblts = self.shrt_trm_ln + self.brrwng_frm_th_cntrl_bnk + self.lns_frm_othr_bnks + self.fnncl_lblts_hld_fr_trd \
        +self.drvtv_fnncl_lblts +self.blls_pybl + self.accnts_pybl + self.accnt_rcvd_in_advnc + self.fnncl_assts_sld_fr_rprchs\
        +self.hndlng_fe_and_cmmssn + self.emply_bnfts_pybl + self.txs_pybl + self.intrst_pybl + self.dvdnd_pybl + self.othr_accnt_pybl\
        +self.accnts_pybl_rnsrnc + self.rsrv_fnd_fr_insrnc_cntrcts + self.actng_sl_of_scrts + self.hld_fr_sl_dbt + self.nn_crnt_lblts_ds_wthn_on_yr\
        +self.othr_crrnt_lnlts == self.ttl_crrnt_lblts
        #非流动负债校验
        c_ttl_nn_crrnt_lblts = self.lng_trm_ln + self.bnd_pybl + self.lng_trm_accnt_pybl + self.lng_trm_emply_bnfts_pybl + self.spcfc_accnt_pybl \
        +self.estmtd_lblty + self.dfrrd_incm + self.dfrrd_tx_lblts + self.othr_nn_crrnt_lblts == self.ttl_nn_crrnt_lblts
        #负债校验
        c_ttl_lblts = self.ttl_crrnt_lblts + self.ttl_nn_crrnt_lblts == self.ttl_lblts
        #归属母公司权益校验

        if self.typ_rep_id == 'A':
            c_atrbt_t_ownrs_eqty_of_prnt = self.pd_n_cptl + self.othr_eqty_instrmnts + self.cptl_rsrv - self.lss_trsry_shr + self.othr_cmprhnsv_incm \
            + self.spcl_rsrv + self.srpls_rsrv + self.gnrl_rsk_prprtn + self.undstrbtd_prft == self.atrbt_t_ownrs_eqty_of_prnt
        else:
            c_atrbt_t_ownrs_eqty_of_prnt = True
        #所有者权益校验
        if self.typ_rep_id == 'B':
            c_ttl_ownrs_eqty =  self.pd_n_cptl + self.othr_eqty_instrmnts + self.cptl_rsrv - self.lss_trsry_shr + self.othr_cmprhnsv_incm \
            + self.spcl_rsrv + self.srpls_rsrv + self.gnrl_rsk_prprtn + self.undstrbtd_prft == self.ttl_ownrs_eqty
        else:
            c_ttl_ownrs_eqty = self.atrbt_t_ownrs_eqty_of_prnt + self.mnrty_eqty == self.ttl_ownrs_eqty

        #负债+所有者权益 = 总资产
        c_ttl_lblts_and_ownrs_eqty = self.ttl_lblts + self.ttl_ownrs_eqty == self.ttl_lblts_and_ownrs_eqty
        #总资产相等
        logic = self.ttl_assts == self.ttl_lblts_and_ownrs_eqty
        print('流动资产校验',c_ttl_crrnt_assts)
        print('非流动资产校验',c_ttl_nn_crrnt_assts)
        print('资产校验',c_ttl_assts)
        print('流动负债校验',c_ttl_crrnt_lblts)
        print('非流动负债校验',c_ttl_nn_crrnt_lblts)
        print('负债校验',c_ttl_lblts)
        print('归属母公司权益校验',c_atrbt_t_ownrs_eqty_of_prnt)
        print('所有者权益校验',c_ttl_ownrs_eqty)
        print('总资产相等',logic)

        return c_ttl_crrnt_assts and c_ttl_nn_crrnt_assts and c_ttl_assts and c_ttl_crrnt_lblts and c_ttl_nn_crrnt_lblts\
            and c_ttl_lblts and c_atrbt_t_ownrs_eqty_of_prnt and c_ttl_ownrs_eqty and logic and c_ttl_lblts_and_ownrs_eqty


    class Meta:
        unique_together = ("stk_cd", "acc_per","typ_rep",'before_end')

    def __str__(self):
        return '资产负债表:{}于{}的{}'.format(self.stk_cd,self.acc_per,self.typ_rep)

class IncomeStatement(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END,default='end')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    tl_oprtng_incm = models.DecimalField('营业总收入', max_digits=26, decimal_places=2, default=0.00)
    oprtng_incm = models.DecimalField('营业收入', max_digits=26, decimal_places=2, default=0.00)
    intrst_incm = models.DecimalField('利息收入', max_digits=26, decimal_places=2, default=0.00)
    ernd_prm = models.DecimalField('已赚保费', max_digits=26, decimal_places=2, default=0.00)
    f_and_cmsn_incm = models.DecimalField('手续费及佣金收入', max_digits=26, decimal_places=2, default=0.00)
    tl_oprtng_csts = models.DecimalField('营业总成本', max_digits=26, decimal_places=2, default=0.00)
    oprtng_cst = models.DecimalField('营业成本', max_digits=26, decimal_places=2, default=0.00)
    intrst_expns = models.DecimalField('利息支出', max_digits=26, decimal_places=2, default=0.00)
    f_and_cmsn_expns = models.DecimalField('手续费及佣金支出', max_digits=26, decimal_places=2, default=0.00)
    srndr_mny = models.DecimalField('退保金', max_digits=26, decimal_places=2, default=0.00)
    clms_pyts_nt = models.DecimalField('赔付支出净额', max_digits=26, decimal_places=2, default=0.00)
    drw_insrnc_cntrct_rsrv_nt = models.DecimalField('提取保险合同准备金净额', max_digits=26, decimal_places=2, default=0.00)
    dvdnd_pymnt_plcy = models.DecimalField('保单红利支出', max_digits=26, decimal_places=2, default=0.00)
    rnsrnc_csts = models.DecimalField('分保费用', max_digits=26, decimal_places=2, default=0.00)
    txs_and_srchrgs = models.DecimalField('税金及附加', max_digits=26, decimal_places=2, default=0.00)
    sls_expns = models.DecimalField('销售费用', max_digits=26, decimal_places=2, default=0.00)
    mngmnt_csts = models.DecimalField('管理费用', max_digits=26, decimal_places=2, default=0.00)
    fncl_expns = models.DecimalField('财务费用', max_digits=26, decimal_places=2, default=0.00)
    ast_imprmnt_ls = models.DecimalField('资产减值损失', max_digits=26, decimal_places=2, default=0.00)
    gns_frm_chngs_in_fr_vl = models.DecimalField('公允价值变动收益', max_digits=26, decimal_places=2, default=0.00)
    invstmnt_incm = models.DecimalField('投资收益', max_digits=26, decimal_places=2, default=0.00)
    exchng_gns = models.DecimalField('汇兑收益', max_digits=26, decimal_places=2, default=0.00)
    dspsl_of_asts = models.DecimalField('资产处置收益', max_digits=26, decimal_places=2, default=0.00)
    othr_bnfts = models.DecimalField('其他收益', max_digits=26, decimal_places=2, default=0.00)
    oprtng_prft = models.DecimalField('营业利润', max_digits=26, decimal_places=2, default=0.00)
    n_prtng_incm = models.DecimalField('营业外收入', max_digits=26, decimal_places=2, default=0.00)
    oprtng_expns = models.DecimalField('营业外支出', max_digits=26, decimal_places=2, default=0.00)
    th_tl_prft = models.DecimalField('利润总额', max_digits=26, decimal_places=2, default=0.00)
    incm_tx_expns = models.DecimalField('所得税费用', max_digits=26, decimal_places=2, default=0.00)
    np = models.DecimalField('净利润', max_digits=26, decimal_places=2, default=0.00)
    cnt_np = models.DecimalField('持续经营净利润', max_digits=26, decimal_places=2, default=0.00)
    ter_np = models.DecimalField('终止经营净利润', max_digits=26, decimal_places=2, default=0.00)
    np_mi = models.DecimalField('少数股东损益', max_digits=26, decimal_places=2, default=0.00)
    np_pa = models.DecimalField('归属于母公司股东的净利润', max_digits=26, decimal_places=2, default=0.00)
    ocomin = models.DecimalField('其他综合收益的税后净额', max_digits=26, decimal_places=2, default=0.00)
    ocomin_pa = models.DecimalField('归属母公司股东的其他综合收益的税后净额', max_digits=26, decimal_places=2, default=0.00)
    ocomin_mi = models.DecimalField('归属于少数股东的其他综合收益的税后净额', max_digits=26, decimal_places=2, default=0.00)
    tl_cmprhnsv_incm = models.DecimalField('综合收益总额', max_digits=26, decimal_places=2, default=0.00)
    comin_pa = models.DecimalField('归属于母公司股东的综合收益总额', max_digits=26, decimal_places=2, default=0.00)
    comin_mi = models.DecimalField('归属于少数股东的综合收益总额', max_digits=26, decimal_places=2, default=0.00)
    eps = models.DecimalField('基本每股收益', max_digits=26, decimal_places=2, default=0.00)
    deps = models.DecimalField('稀释每股收益', max_digits=26, decimal_places=2, default=0.00)

    def check_logic(self):
        #收入检验
        if self.typ_rep_id == 'A':
            c_tl_oprtng_incm = self.oprtng_incm + self.intrst_incm + self.ernd_prm + self.f_and_cmsn_incm == self.tl_oprtng_incm
        else:
            c_tl_oprtng_incm = True
        print('收入检验:{}'.format(c_tl_oprtng_incm))
        #成本检验
        if self.typ_rep_id == 'A':
            c_tl_oprtng_csts = self.oprtng_cst + self.intrst_expns + self.f_and_cmsn_expns + self.srndr_mny + self.clms_pyts_nt + self.drw_insrnc_cntrct_rsrv_nt\
            + self.dvdnd_pymnt_plcy + self.rnsrnc_csts + self.txs_and_srchrgs + self.sls_expns + self.mngmnt_csts + self.fncl_expns \
            + self.ast_imprmnt_ls == self.tl_oprtng_csts
        else:
            c_tl_oprtng_csts = True

        print('成本检验:{}'.format(c_tl_oprtng_csts))
        #营业利润校验
        if self.typ_rep_id == 'A':
            c_oprtng_prft = self.tl_oprtng_incm - self.tl_oprtng_csts  + self.gns_frm_chngs_in_fr_vl + self.invstmnt_incm +  self.exchng_gns \
            + self.dspsl_of_asts + self.othr_bnfts == self.oprtng_prft
        else:
            c_oprtng_prft = self.oprtng_incm - self.oprtng_cst -(self.txs_and_srchrgs + self.sls_expns + self.mngmnt_csts + self.fncl_expns \
            + self.ast_imprmnt_ls)+ self.gns_frm_chngs_in_fr_vl + self.invstmnt_incm + self.exchng_gns \
                            + self.dspsl_of_asts + self.othr_bnfts == self.oprtng_prft

        print('营业利润检验:{}'.format(c_oprtng_prft))
        #利润总额校验
        c_th_tl_prft = self.oprtng_prft + self.n_prtng_incm - self.oprtng_expns == self.th_tl_prft

        print('利润总额检验:{}'.format(c_th_tl_prft))
        #净利润校验
        c_np_1 = self.th_tl_prft - self.incm_tx_expns == self.np
        if self.typ_rep_id == 'A':
            c_np_2 = self.np_pa + self.np_mi == self.np
        else:
            c_np_2 = True
        c_np_3 = True if self.cnt_np == 0 else self.cnt_np + self.ter_np == self.np
        print('净利润检验{}{}{}'.format(c_np_1,c_np_2,c_np_3))
        #其他综合收益检验
        if self.typ_rep_id == 'A':
            c_ocomin = True if self.ocomin_pa == 0 else self.ocomin_pa + self.ocomin_mi == self.ocomin
        else:
            c_ocomin = True

        print('其他综合收益检验{}'.format(c_ocomin))
        #综合收益检验
        if self.typ_rep_id == 'A':
            c_tl_cmprhnsv_incm = self.comin_pa + self.comin_mi == self.tl_cmprhnsv_incm
        else:
            c_tl_cmprhnsv_incm = True
        print('综合收益检验{}'.format(c_tl_cmprhnsv_incm))

        return c_tl_oprtng_incm and c_tl_oprtng_csts and c_oprtng_prft and c_th_tl_prft and c_np_1 \
    and c_np_2 and c_np_3 and c_ocomin and c_tl_cmprhnsv_incm

    class Meta:
        unique_together = ("stk_cd", "acc_per","typ_rep",'before_end')

    def __str__(self):
        return '利润表：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class CashFlow(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END,default='end')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    rcv_gds_srvc = models.DecimalField('销售商品、提供劳务收到的现金', max_digits=26, decimal_places=2, default=0.00)
    cstmr_intrbnk = models.DecimalField('客户存款和同业存放款项净增加额', max_digits=26, decimal_places=2, default=0.00)
    br_cntrl_bnk = models.DecimalField('向中央银行借款净增加额', max_digits=26, decimal_places=2, default=0.00)
    rcv_othr_fncl_instns = models.DecimalField('向其他金融机构拆入资金净增加额', max_digits=26, decimal_places=2, default=0.00)
    rcv_orgnl_insrnc = models.DecimalField('收到原保险合同保费取得的现金', max_digits=26, decimal_places=2, default=0.00)
    rnsrnc_bsns = models.DecimalField('收到再保险业务现金净额', max_digits=26, decimal_places=2, default=0.00)
    hshld_dpsts_nt_incrs = models.DecimalField('保户储金及投资款净增加额', max_digits=26, decimal_places=2, default=0.00)
    dspsl_fncl_asts = models.DecimalField('处置以公允价值计量且其变动计入当期损益的金融资产净增加额', max_digits=26, decimal_places=2, default=0.00)
    rcv_intrst_fe_cmsn = models.DecimalField('收取利息、手续费及佣金的现金', max_digits=26, decimal_places=2, default=0.00)
    cptl_insrtd = models.DecimalField('拆入资金净增加额', max_digits=26, decimal_places=2, default=0.00)
    rprchs_bsns_fnds = models.DecimalField('回购业务资金净增加额', max_digits=26, decimal_places=2, default=0.00)
    tx_rfnd = models.DecimalField('收到的税费返还', max_digits=26, decimal_places=2, default=0.00)
    rcv_othr_oprtng = models.DecimalField('收到其他与经营活动有关的现金', max_digits=26, decimal_places=2, default=0.00)
    sub_rcv_oprtng = models.DecimalField('经营活动现金流入小计', max_digits=26, decimal_places=2, default=0.00)
    pay_gds_and_srvcs = models.DecimalField('购买商品、接受劳务支付的现金', max_digits=26, decimal_places=2, default=0.00)
    cstmr_lns_and_advncs = models.DecimalField('客户贷款及垫款净增加额', max_digits=26, decimal_places=2, default=0.00)
    pay_cntrl_bnks = models.DecimalField('存放中央银行和同业款项净增加额', max_digits=26, decimal_places=2, default=0.00)
    pay_orgnl_insrnc = models.DecimalField('支付原保险合同赔付款项的现金', max_digits=26, decimal_places=2, default=0.00)
    pay_intrst_fe_cmsn = models.DecimalField('支付利息、手续费及佣金的现金', max_digits=26, decimal_places=2, default=0.00)
    pay_plcy_dvdnds = models.DecimalField('支付保单红利的现金', max_digits=26, decimal_places=2, default=0.00)
    pay_emplyee = models.DecimalField('支付给职工以及为职工支付的现金', max_digits=26, decimal_places=2, default=0.00)
    pay_txs = models.DecimalField('支付的各项税费', max_digits=26, decimal_places=2, default=0.00)
    pay_othr_oprtng = models.DecimalField('支付其他与经营活动有关的现金', max_digits=26, decimal_places=2, default=0.00)
    sub_pay_oprtng = models.DecimalField('经营活动现金流出小计', max_digits=26, decimal_places=2, default=0.00)
    nt_oprtng_actvts = models.DecimalField('经营活动产生的现金流量净额', max_digits=26, decimal_places=2, default=0.00)
    rcvd_frm_invstmnt = models.DecimalField('收回投资收到的现金', max_digits=26, decimal_places=2, default=0.00)
    invstmnt_incm = models.DecimalField('取得投资收益收到的现金', max_digits=26, decimal_places=2, default=0.00)
    dspsl_fxd_asts = models.DecimalField('处置固定资产、无形资产和其他长期资产收回的现金净额', max_digits=26, decimal_places=2, default=0.00)
    dspsl_sbsdrs = models.DecimalField('处置子公司及其他营业单位收到的现金净额', max_digits=26, decimal_places=2, default=0.00)
    rcv_othr_invstng = models.DecimalField('收到其他与投资活动有关的现金', max_digits=26, decimal_places=2, default=0.00)
    sub_rcv_invstmnt = models.DecimalField('投资活动现金流入小计', max_digits=26, decimal_places=2, default=0.00)
    bld_fxd_asts = models.DecimalField('购建固定资产、无形资产和其他长期资产支付的现金', max_digits=26, decimal_places=2, default=0.00)
    csh_invstmnt = models.DecimalField('投资支付的现金', max_digits=26, decimal_places=2, default=0.00)
    pldgd_lns = models.DecimalField('质押贷款净增加额', max_digits=26, decimal_places=2, default=0.00)
    acq_sbsdrs = models.DecimalField('取得子公司及其他营业单位支付的现金净额', max_digits=26, decimal_places=2, default=0.00)
    pay_othr_invstng = models.DecimalField('支付其他与投资活动有关的现金', max_digits=26, decimal_places=2, default=0.00)
    sub_pay_invstmnt = models.DecimalField('投资活动现金流出小计', max_digits=26, decimal_places=2, default=0.00)
    nt_invstng_actvts = models.DecimalField('投资活动产生的现金流量净额', max_digits=26, decimal_places=2, default=0.00)
    absrb_invstmnt = models.DecimalField('吸收投资收到的现金', max_digits=26, decimal_places=2, default=0.00)
    incld_rcv_mnrty = models.DecimalField('其中：子公司吸收少数股东投资收到的现金', max_digits=26, decimal_places=2, default=0.00)
    brwngs = models.DecimalField('取得借款收到的现金', max_digits=26, decimal_places=2, default=0.00)
    isnc_bnds = models.DecimalField('发行债券收到的现金', max_digits=26, decimal_places=2, default=0.00)
    rcvd_othr_ncng = models.DecimalField('收到其他与筹资活动有关的现金', max_digits=26, decimal_places=2, default=0.00)
    sub_rcv_fncng = models.DecimalField('筹资活动现金流入小计', max_digits=26, decimal_places=2, default=0.00)
    pay_dbt = models.DecimalField('偿还债务支付的现金', max_digits=26, decimal_places=2, default=0.00)
    dstrbt_dvdnds = models.DecimalField('分配股利、利润或偿付利息支付的现金', max_digits=26, decimal_places=2, default=0.00)
    py_prf_mnrty = models.DecimalField('其中：子公司支付给少数股东的股利、利润', max_digits=26, decimal_places=2, default=0.00)
    py_othr_rsng = models.DecimalField('支付其他与筹资活动有关的现金', max_digits=26, decimal_places=2, default=0.00)
    sub_pay_fncng = models.DecimalField('筹资活动现金流出小计', max_digits=26, decimal_places=2, default=0.00)
    nt_fncng = models.DecimalField('筹资活动产生的现金流量净额', max_digits=26, decimal_places=2, default=0.00)
    exchng_rt = models.DecimalField('汇率变动对现金及现金等价物的影响', max_digits=26, decimal_places=2, default=0.00)
    csh_incr = models.DecimalField('现金及现金等价物净增加额', max_digits=26, decimal_places=2, default=0.00)
    beg_csh = models.DecimalField('期初现金及现金等价物余额', max_digits=26, decimal_places=2, default=0.00)
    end_csh = models.DecimalField('期末现金及现金等价物余额', max_digits=26, decimal_places=2, default=0.00)

    def check_logic(self):
        #经营流入检验
        c_sub_rcv_oprtng = self.rcv_gds_srvc + self.cstmr_intrbnk + self.br_cntrl_bnk + self.rcv_othr_fncl_instns + self.rcv_orgnl_insrnc\
        +self.rnsrnc_bsns + self.rprchs_bsns_fnds + self.tx_rfnd + self.rcv_othr_oprtng == self.sub_rcv_oprtng
        print('经营流入检验:{}'.format(c_sub_rcv_oprtng))
        #经营流出检验
        c_sub_pay_oprtng = self.pay_gds_and_srvcs + self.cstmr_lns_and_advncs + self.pay_cntrl_bnks + self.pay_orgnl_insrnc + self.pay_intrst_fe_cmsn\
        + self.pay_plcy_dvdnds + self.pay_emplyee + self.pay_txs + self.pay_othr_oprtng == self.sub_pay_oprtng
        print('经营流出检验:{}'.format(c_sub_pay_oprtng))
        #经营现金流净额
        c_nt_oprtng_actvts = self.sub_rcv_oprtng - self.sub_pay_oprtng == self.nt_oprtng_actvts
        print('经营净流量检验:{}'.format(c_nt_oprtng_actvts))
        #投资流入检验
        c_sub_rcv_invstmnt = self.rcvd_frm_invstmnt + self.invstmnt_incm +  self.dspsl_fxd_asts + self.dspsl_sbsdrs \
        + self.rcv_othr_invstng == self.sub_rcv_invstmnt
        print('投资流入:{}'.format(c_sub_rcv_invstmnt))
        #投资流出检验
        c_sub_pay_invstmnt = self.bld_fxd_asts + self.csh_invstmnt + self.pldgd_lns + self.acq_sbsdrs \
        + self.pay_othr_invstng == self.sub_pay_invstmnt
        print('投资流出:{}'.format(c_sub_pay_invstmnt))
        #投资净现金流检验
        c_nt_invstng_actvts = self.sub_rcv_invstmnt - self.sub_pay_invstmnt == self.nt_invstng_actvts
        print('投资净流量:{}'.format(c_nt_invstng_actvts))
        #筹资现金流入检验
        c_sub_rcv_fncng = self.absrb_invstmnt + self.brwngs + self.isnc_bnds + self.rcvd_othr_ncng == self.sub_rcv_fncng
        print('筹资流入:{}'.format(c_sub_rcv_fncng))
        #筹资活动流出检验
        c_sub_pay_fncng = self.pay_dbt + self.dstrbt_dvdnds + self.py_othr_rsng == self.sub_pay_fncng
        print('筹资流出:{}'.format(c_sub_pay_fncng))
        #筹资净现金流检验
        c_nt_fncng = self.sub_rcv_fncng - self.sub_pay_fncng == self.nt_fncng
        print('筹资净流量:{}'.format(c_nt_fncng))
        #现金增加额检验
        c_csh_incr = self.nt_oprtng_actvts + self.nt_invstng_actvts + self.nt_fncng + self.exchng_rt == self.csh_incr
        print('现金增加额:{}'.format(c_csh_incr))
        #logic
        logic = self.csh_incr  + self.beg_csh == self.end_csh
        print('期初期末现金余额:{}'.format(logic))

        return c_sub_rcv_oprtng and c_sub_pay_oprtng and c_nt_oprtng_actvts and c_sub_rcv_invstmnt and \
               c_sub_rcv_invstmnt and c_sub_pay_invstmnt and c_nt_invstng_actvts and c_sub_rcv_fncng and c_sub_pay_fncng \
                and c_nt_fncng and c_csh_incr and logic

    class Meta:
        unique_together = ("stk_cd", "acc_per","typ_rep",'before_end')

    def __str__(self):
        return '现金流量表：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class CompaniBasicSituat(CommonInfo):
    compani_overview = models.TextField(verbose_name='公司概况',default='')
    scope_of_merger = models.TextField(verbose_name='合并范围',default='')
    signific_amount_judgement = models.TextField(verbose_name=' 单项金额重大的判断依据或金额标准',default='')
    signific_amount_withdraw = models.TextField(verbose_name=' 单项金额重大并单项计提坏账准备的计提方法',default='')
    no_signific_amount_judgement = models.TextField(verbose_name='单项金额不重大但单项计提坏账准备的理由',default='')
    no_signific_amount_withdraw = models.TextField(verbose_name='单项金额不重大但单项计提坏账准备的计提方法',default='')
    balanc_percentag = models.TextField(verbose_name='余额百分比法',default='')
    other_withdraw_method = models.TextField(verbose_name='其他坏账计提方法',default='')
    rd_expense_account_polici = models.TextField(verbose_name='内部研究开发支出会计政策',default='')
    income_account_polici = models.TextField(verbose_name='收入确认会计政策',default='')
    chang_in_account_estim = models.TextField(verbose_name='会计估计变更',default='')
    tax_incent = models.TextField(verbose_name='税收优惠',default='')

class AgeAnalysi(CommonInfo):
    item = models.CharField(verbose_name='项目',max_length=150,default='')
    one_month = models.DecimalField(verbose_name='1个月内计提比例',decimal_places=2,max_digits=10,default=0.00)
    two_month = models.DecimalField(verbose_name='2个月内计提比例',decimal_places=2,max_digits=10,default=0.00)
    three_month = models.DecimalField(verbose_name='3个月内计提比例',decimal_places=2,max_digits=10,default=0.00)
    four_month = models.DecimalField(verbose_name='4个月内计提比例',decimal_places=2,max_digits=10,default=0.00)
    five_month = models.DecimalField(verbose_name='5个月内计提比例',decimal_places=2,max_digits=10,default=0.00)
    six_month = models.DecimalField(verbose_name='6个月内计提比例',decimal_places=2,max_digits=10,default=0.00)
    seven_month = models.DecimalField(verbose_name='7个月内计提比例',decimal_places=2,max_digits=10,default=0.00)
    eight_month = models.DecimalField(verbose_name='8个月内计提比例',decimal_places=2,max_digits=10,default=0.00)
    nine_month = models.DecimalField(verbose_name='9个月内计提比例',decimal_places=2,max_digits=10,default=0.00)
    ten_month = models.DecimalField(verbose_name='10个月内计提比例',decimal_places=2,max_digits=10,default=0.00)
    eleven_month = models.DecimalField(verbose_name='11个月内计提比例',decimal_places=2,max_digits=10,default=0.00)
    twelve_month = models.DecimalField(verbose_name='12个月内计提比例',decimal_places=2,max_digits=10,default=0.00)
    two_year = models.DecimalField(verbose_name='2年内计提比例',decimal_places=2,max_digits=10,default=0.00)
    three_year = models.DecimalField(verbose_name='3年内计提比例',decimal_places=2,max_digits=10,default=0.00)
    four_year = models.DecimalField(verbose_name='4年内计提比例',decimal_places=2,max_digits=10,default=0.00)
    five_year = models.DecimalField(verbose_name='5年内计提比例',decimal_places=2,max_digits=10,default=0.00)
    over_five_year = models.DecimalField(verbose_name='5年以上计提比例',decimal_places=2,max_digits=10,default=0.00)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','item')

class DepreciOfFixAssetMethod(CommonInfo):
    asset_type = models.CharField(verbose_name='类别',max_length=150,default='')
    method = models.CharField(verbose_name='折旧方法',max_length=150,default='')
    years = models.CharField(verbose_name='折旧年限',max_length=150,default='')
    residu_rate = models.CharField(verbose_name='残值率',max_length=150,default='')
    annual_depreci_rate = models.CharField(verbose_name='年折旧率',max_length=150,default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','asset_type')

class MainTaxAndTaxRate(CommonInfo):
    tax_type = models.CharField(verbose_name='税种',max_length=150,default='')
    basi = models.CharField(verbose_name='计税依据',max_length=150,default='')
    rate = models.CharField(verbose_name='税率',max_length=150,default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','tax_type')

class IncomTaxRate(CommonInfo):
    name = models.CharField(verbose_name='纳税主体',max_length=150,default='')
    rate = models.CharField(verbose_name='税率',max_length=150,default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per', 'name')

class MoneyFund(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    cash = models.DecimalField(verbose_name='库存现金',decimal_places=2,max_digits=22,default=0.00)
    bank_save = models.DecimalField(verbose_name='银行存款',decimal_places=2,max_digits=22,default=0.00)
    other_monetari_fund = models.DecimalField(verbose_name='其他货币资金',decimal_places=2,max_digits=22,default=0.00)
    total = models.DecimalField(verbose_name='合计',decimal_places=2,max_digits=22,default=0.00)
    oversea_total_amount = models.DecimalField(verbose_name='存放在境外的款项总额',decimal_places=2,max_digits=22,default=0.00)
    instruct = models.TextField(verbose_name='说明',default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per","typ_rep",'before_end')

    def __str__(self):
        return '货币资金：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

    def check_logic(self):
        c_total = self.cash + self.bank_save + self.other_monetari_fund == self.total
        print('货币资金表内关系{}'.format(c_total))
        obj = BalanceSheet.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,typ_rep_id=self.typ_rep_id,before_end=self.before_end)
        c_bs = obj.cash == self.total
        print('货币资金表间关系{}'.format(c_bs))
        return c_total and c_bs

# class __BillReceiv__(CommonInfo):
#     BEFORE_END = (
#         ('before', 'before'),
#         ('end', 'end'),
#     )
#     ITEM = (
#         ('bank', 'bank_accept_bill'),
#         ('trade', 'trade_accept_draft'),
#         ('total', 'total'),
#     )
#     before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
#     typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
#     item = models.CharField(verbose_name='项目', max_length=30, choices=ITEM, default='bank')
#     balanc = models.DecimalField(verbose_name='余额',decimal_places=2,max_digits=22,default=0.00)
#     pledg = models.DecimalField(verbose_name='质押金额',decimal_places=2,max_digits=22,default=0.00)
#     derecognition = models.DecimalField(verbose_name='终止确认金额',decimal_places=2,max_digits=22,default=0.00)
#     recognition = models.DecimalField(verbose_name='未终止确认金额',decimal_places=2,max_digits=22,default=0.00)
#     transfer_receiv = models.DecimalField(verbose_name='转应收账款金额',decimal_places=2,max_digits=22,default=0.00)
#     instruct = models.TextField(verbose_name='说明',default='')
#
#     class Meta:
#         unique_together = ("stk_cd", "acc_per","typ_rep",'before_end','item')
#
#     def __str__(self):
#         return '应收票据：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)
#
#     def check_logic(self):
#         obj1 = self.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,typ_rep_id=self.typ_rep_id,before_end=self.before_end,item='bank')
#         obj2 = self.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,typ_rep_id=self.typ_rep_id,before_end=self.before_end,item='trade')
#         obj3 = self.objects.get(stk_cd_id=self.stk_cd_id,acc_per=self.acc_per,typ_rep_id=self.typ_rep_id,before_end=self.before_end,item='total')
#         projects = ['balanc','pledg','derecognition','recognition','transfer_receiv']
#         flags = set()
#         for project in projects
#             flag = getattr(obj1,project)+getattr(obj2,project) == getattr(obj3,project)
#             flags.add(flag)
#         if len(flags) == 1 and list(flags)[0] == True:
#             print('应收票据表内关系正确')


class BillReceiv(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )

    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    bank = models.DecimalField(verbose_name='银行承兑汇票余额',decimal_places=2,max_digits=22,default=0.00)
    trade = models.DecimalField(verbose_name='商业承兑汇票余额',decimal_places=2,max_digits=22,default=0.00)
    total = models.DecimalField(verbose_name='余额合计',decimal_places=2,max_digits=22,default=0.00)
    bank_pledg = models.DecimalField(verbose_name='银行承兑汇票质押金额',decimal_places=2,max_digits=22,default=0.00)
    trade_pledg = models.DecimalField(verbose_name='商业承兑汇票质押金额',decimal_places=2,max_digits=22,default=0.00)
    total_pledg = models.DecimalField(verbose_name='质押金额合计',decimal_places=2,max_digits=22,default=0.00)
    bank_derecognition = models.DecimalField(verbose_name='银行承兑汇票终止确认金额',decimal_places=2,max_digits=22,default=0.00)
    trade_derecognition = models.DecimalField(verbose_name='商业承兑汇票终止确认金额',decimal_places=2,max_digits=22,default=0.00)
    total_derecognition = models.DecimalField(verbose_name='终止确认金额合计',decimal_places=2,max_digits=22,default=0.00)
    bank_recognition = models.DecimalField(verbose_name='银行承兑汇票未终止确认金额',decimal_places=2,max_digits=22,default=0.00)
    trade_recognition = models.DecimalField(verbose_name='商业承兑汇票未终止确认金额',decimal_places=2,max_digits=22,default=0.00)
    total_recognition = models.DecimalField(verbose_name='未终止确认金额合计',decimal_places=2,max_digits=22,default=0.00)
    bank_transfer_receiv = models.DecimalField(verbose_name='银行承兑汇票转应收账款金额',decimal_places=2,max_digits=22,default=0.00)
    trade_transfer_receiv = models.DecimalField(verbose_name='商业承兑汇票转应收账款金额',decimal_places=2,max_digits=22,default=0.00)
    total_transfer_receiv = models.DecimalField(verbose_name='转应收账款金额合计',decimal_places=2,max_digits=22,default=0.00)
    instruct = models.TextField(verbose_name='说明',default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per","typ_rep",'before_end')

    def __str__(self):
        return '应收票据：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

    def check_logic(self):
        c_total = self.bank + self.trade == self.total
        c_pledg = self.bank_pledg + self.trade_pledg == self.total_pledg
        c_derecognition = self.bank_derecognition + self.trade_derecognition == self.total_derecognition
        c_recognition = self.bank_recognition + self.trade_recognition == self.total_recognition
        c_transfer_receiv = self.bank_transfer_receiv + self.trade_transfer_receiv == self.total_transfer_receiv
        check_inner = c_total and  c_pledg and c_derecognition and c_recognition and c_transfer_receiv
        print('应收票据表内关系{}'.format(check_inner))
        obj = BalanceSheet.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, typ_rep_id=self.typ_rep_id,
                                       before_end=self.before_end)
        check_outer = obj.bll_rcvbl == self.total
        print('应收票据表间关系{}'.format(check_outer))
        return check_inner and check_outer

class Receiv(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    SUBJECT = (
        ('account', 'account_receiv'),
        ('other', 'other_receiv'),
    )

    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
    subject = models.CharField(verbose_name='应收账款/其他应收款', max_length=30, choices=SUBJECT, default='')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    signific_balanc = models.DecimalField(verbose_name='单项金额重大并单独计提坏账准备的账面余额', decimal_places=2, max_digits=22, default=0.00)
    signific_bad_debt_prepar = models.DecimalField(verbose_name='单项金额重大并单独计提坏账准备的坏账准备', decimal_places=2, max_digits=22, default=0.00)
    signific_value = models.DecimalField(verbose_name='单项金额重大并单独计提坏账准备的账面价值', decimal_places=2, max_digits=22, default=0.00)
    combin_balanc = models.DecimalField(verbose_name='按信用风险特征组合计提坏账准备的账面余额', decimal_places=2, max_digits=22,
                                          default=0.00)
    combin_bad_debt_prepar = models.DecimalField(verbose_name='按信用风险特征组合计提坏账准备的坏账准备', decimal_places=2,
                                                   max_digits=22, default=0.00)
    combin_value = models.DecimalField(verbose_name='按信用风险特征组合计提坏账准备的账面价值', decimal_places=2, max_digits=22,
                                         default=0.00)
    no_signific_balanc = models.DecimalField(verbose_name='单项金额不重大但单独计提坏账准备的账面余额', decimal_places=2, max_digits=22,
                                          default=0.00)
    no_signific_bad_debt_prepar = models.DecimalField(verbose_name='单项金额不重大但单独计提坏账准备的坏账准备', decimal_places=2,
                                                   max_digits=22, default=0.00)
    no_signific_value = models.DecimalField(verbose_name='单项金额不重大但单独计提坏账准备的账面价值', decimal_places=2, max_digits=22,
                                         default=0.00)
    total_balanc = models.DecimalField(verbose_name='账面余额合计', decimal_places=2, max_digits=22,
                                             default=0.00)
    total_bad_debt_prepar = models.DecimalField(verbose_name='坏账准备合计', decimal_places=2,
                                                      max_digits=22, default=0.00)
    total_value = models.DecimalField(verbose_name='账面价值合计', decimal_places=2, max_digits=22,
                                            default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'before_end','subject')

    def __str__(self):
        return '应收账款：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

    def check_logic(self):
        c_signific = self.signific_balanc - self.signific_bad_debt_prepar == self.signific_value
        c_combin = self.combin_balanc - self.combin_bad_debt_prepar == self.combin_value
        c_no_sign = self.no_signific_balanc - self.no_signific_bad_debt_prepar == self.no_signific_value
        c_balance = self.signific_balanc + self.combin_balanc + self.no_signific_balanc == self.total_balanc
        c_bad_debt_prepar = self.signific_bad_debt_prepar + self.combin_bad_debt_prepar + self.no_signific_bad_debt_prepar == self.total_bad_debt_prepar
        c_value = self.signific_value + self.combin_value + self.no_signific_value == self.total_value

        check_inner = c_signific and c_combin and c_no_sign and c_balance and c_bad_debt_prepar and c_value
        print('应收款表内关系{}'.format(check_inner))
        obj = BalanceSheet.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, typ_rep_id=self.typ_rep_id,
                                       before_end=self.before_end)
        if self.subject == 'account':
            check_outer = obj.acnt_rcvbl == self.total_value
        elif self.subject == 'other':
            check_outer = obj.othr_accnt_rcvbl == self.total_value
        else :
            check_outer = False
        print('应收款表间关系{}'.format(check_outer))
        return check_inner and check_outer

class SignificReceiv(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    SUBJECT = (
        ('account', 'account_receiv'),
        ('other', 'other_receiv'),
    )

    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
    subject = models.CharField(verbose_name='应收账款/其他应收款', max_length=30, choices=SUBJECT, default='')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='单位名称',max_length=150,default='')
    balanc = models.DecimalField(verbose_name='账面余额', decimal_places=2, max_digits=22,
                                       default=0.00)
    bad_debt_prepar = models.DecimalField(verbose_name='坏账准备', decimal_places=2,
                                                max_digits=22, default=0.00)
    reason = models.CharField(verbose_name='计提理由',max_length=300,default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'before_end', 'subject','name')

    def __str__(self):
        return '单项金额重大的应收款：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

    def check_logic(self):
        #表内关系在存储时检查
        obj1 = SignificReceiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, typ_rep_id=self.typ_rep_id,
                                before_end=self.before_end, subject=self.subject,name='合计')
        obj2 = Receiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, typ_rep_id=self.typ_rep_id,
                                       before_end=self.before_end,subject=self.subject)
        c_balanc = obj1.balanc == obj2.signific_balanc
        c_bad_debt_prepar = obj1.bad_debt_prepar == obj2.signific_bad_debt_prepar
        check_outer = c_balanc and c_bad_debt_prepar
        print('应收款表间关系{}'.format(check_outer))
        return  check_outer

class ReceivAge(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    SUBJECT = (
        ('account', 'account_receiv'),
        ('other', 'other_receiv'),
        ('prepay', 'prepay'),
    )

    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
    subject = models.CharField(verbose_name='应收账款/其他应收款/预付款项', max_length=30, choices=SUBJECT, default='')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    one_year_balanc = models.DecimalField(verbose_name='1年以内账面余额', decimal_places=2, max_digits=22,
                                 default=0.00)
    two_year_balanc = models.DecimalField(verbose_name='2年以内账面余额', decimal_places=2, max_digits=22,
                                          default=0.00)
    three_year_balanc = models.DecimalField(verbose_name='3年以内账面余额', decimal_places=2, max_digits=22,
                                          default=0.00)
    four_year_balanc = models.DecimalField(verbose_name='4年以内账面余额', decimal_places=2, max_digits=22,
                                          default=0.00)
    five_year_balanc = models.DecimalField(verbose_name='5年以内账面余额', decimal_places=2, max_digits=22,
                                          default=0.00)
    over_five_balanc = models.DecimalField(verbose_name='5年以上账面余额', decimal_places=2, max_digits=22,
                                           default=0.00)
    total_balanc = models.DecimalField(verbose_name='账面余额合计', decimal_places=2, max_digits=22,
                                           default=0.00)
    one_year_bad_debt_prepar = models.DecimalField(verbose_name='1年以内坏账准备', decimal_places=2, max_digits=22,
                                          default=0.00)
    two_year_bad_debt_prepar = models.DecimalField(verbose_name='2年以内坏账准备', decimal_places=2, max_digits=22,
                                          default=0.00)
    three_year_bad_debt_prepar = models.DecimalField(verbose_name='3年以内坏账准备', decimal_places=2, max_digits=22,
                                            default=0.00)
    four_year_bad_debt_prepar = models.DecimalField(verbose_name='4年以内坏账准备', decimal_places=2, max_digits=22,
                                           default=0.00)
    five_year_bad_debt_prepar = models.DecimalField(verbose_name='5年以内坏账准备', decimal_places=2, max_digits=22,
                                           default=0.00)
    over_five_bad_debt_prepar = models.DecimalField(verbose_name='5年以上坏账准备', decimal_places=2, max_digits=22,
                                           default=0.00)
    total_bad_debt_prepar = models.DecimalField(verbose_name='坏账准备合计', decimal_places=2, max_digits=22,
                                                    default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'before_end', 'subject')

    def __str__(self):
        return '账龄组合分析：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

    def check_logic(self):
        c_balance = self.one_year_balanc + self.two_year_balanc +self.three_year_balanc + self.four_year_balanc+\
            self.five_year_balanc + self.over_five_balanc== self.total_balanc
        c_bad_debt_prepar = self.one_year_bad_debt_prepar +  self.two_year_bad_debt_prepar + self.three_year_bad_debt_prepar\
        +self.four_year_bad_debt_prepar + self.five_year_bad_debt_prepar + self.over_five_bad_debt_prepar== self.total_bad_debt_prepar
        check_inner = c_balance and c_bad_debt_prepar
        print('账龄组合表内关系{}'.format(check_inner))
        return check_inner

class ReceivOtherCombin(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    SUBJECT = (
        ('account', 'account_receiv'),
        ('other', 'other_receiv'),
    )

    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
    subject = models.CharField(verbose_name='应收账款/其他应收款', max_length=30, choices=SUBJECT, default='')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='其他组合名称',max_length=150,default='')
    balanc = models.DecimalField(verbose_name='账面余额', decimal_places=2, max_digits=22,
                                          default=0.00)
    bad_debt_prepar = models.DecimalField(verbose_name='坏账准备', decimal_places=2, max_digits=22,
                                                   default=0.00)


    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'before_end', 'subject','name')

    def __str__(self):
        return '其他组合分析：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

    def check_logic(self):
        # 表内关系在存储时检查
        print(self.stk_cd_id)
        print(self.acc_per)
        print(self.typ_rep_id)
        print(self.before_end)
        print(self.subject)
        obj1 = ReceivOtherCombin.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, typ_rep_id=self.typ_rep_id,
                                before_end=self.before_end, subject=self.subject, name='合计')
        obj2 = ReceivAge.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, typ_rep_id=self.typ_rep_id,
                                  before_end=self.before_end, subject=self.subject)
        obj3 = Receiv.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, typ_rep_id=self.typ_rep_id,
                                  before_end=self.before_end, subject=self.subject)
        c_balanc = obj1.balanc + obj2.total_balanc == obj3.combin_balanc
        c_bad_debt_prepar = obj1.bad_debt_prepar + obj2.total_bad_debt_prepar == obj3.combin_bad_debt_prepar
        check_outer = c_balanc and c_bad_debt_prepar
        print('应收款组合表间关系{}'.format(check_outer))
        return check_outer

class WithdrawOrReturnBadDebtPrepar(CommonInfo):
    '''
    计提、转回和核销金额
    '''
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    SUBJECT = (
        ('account', 'account_receiv'),
        ('other', 'other_receiv'),
    )

    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
    subject = models.CharField(verbose_name='应收账款/其他应收款', max_length=30, choices=SUBJECT, default='')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    withdraw = models.DecimalField(verbose_name='计提金额', decimal_places=2, max_digits=22,
                                 default=0.00)
    return_amount = models.DecimalField(verbose_name='转回或收回金额', decimal_places=2, max_digits=22,
                                   default=0.00)
    writeoff = models.DecimalField(verbose_name='核销总金额', decimal_places=2, max_digits=22,
                                   default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'before_end', 'subject')

    def __str__(self):
        return '计提、收回或转回的坏账准备情况：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class ReturnBadDebtPreparList(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    SUBJECT = (
        ('account', 'account_receiv'),
        ('other', 'other_receiv'),
    )

    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
    subject = models.CharField(verbose_name='应收账款/其他应收款', max_length=30, choices=SUBJECT, default='')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='单位名称',max_length=150,default='')
    amount = models.DecimalField(verbose_name='转回或收回金额', decimal_places=2, max_digits=22,
                                   default=0.00)
    style = models.CharField(verbose_name='收回方式', max_length=300,default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'before_end', 'subject','name')

    def __str__(self):
        return '本年坏账准备收回或转回金额重要的：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class WriteOffReceiv(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    SUBJECT = (
        ('account', 'account_receiv'),
        ('other', 'other_receiv'),
    )

    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
    subject = models.CharField(verbose_name='应收账款/其他应收款', max_length=30, choices=SUBJECT, default='')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='单位名称', max_length=150, default='')
    natur = models.CharField(verbose_name='款项性质', max_length=150, default='')
    writeoff = models.DecimalField(verbose_name='核销金额', decimal_places=2, max_digits=22,
                                 default=0.00)
    reason = models.CharField(verbose_name='核销原因', max_length=300, default='')
    program = models.CharField(verbose_name='履行的核销程序', max_length=300, default='')
    is_related = models.CharField(verbose_name='否由关联交易产生', max_length=5, default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'before_end', 'subject', 'name')

    def __str__(self):
        return '重要的核销情况：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class Top5Receiv(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    SUBJECT = (
        ('account', 'account_receiv'),
        ('other', 'other_receiv'),
        ('prepay', 'prepay'),
    )

    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
    subject = models.CharField(verbose_name='应收账款/其他应收款/预付款项', max_length=30, choices=SUBJECT, default='')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='单位名称', max_length=150, default='')
    natur = models.CharField(verbose_name='款项性质', max_length=150, default='')
    balanc = models.DecimalField(verbose_name='余额', decimal_places=2, max_digits=22,
                                   default=0.00)
    bad_debt_prepar = models.DecimalField(verbose_name='坏账准备', decimal_places=2, max_digits=22,
                                   default=0.00)
    age = models.CharField(verbose_name='账龄', max_length=300, default='')
    related = models.CharField(verbose_name='关联关系', max_length=5, default='')
    reason = models.CharField(verbose_name='未结算原因', max_length=300, default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'before_end', 'subject', 'name')

    def __str__(self):
        return '前5名应收款：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class CommonBeforeAndEndName(models.Model):
    SUBJECT = (
        ('interest_receiv', 'interest_receiv'),  # 应收利息
        ('dividend_receiv', 'dividend_receiv'),  # 应收股利
        ('other_receiv_natur', 'other_receiv_natur'),  # 其他应收款性质
        ('other_current_asset', 'other_current_asset'),  # 其他流动资产
        ('engin_materi', 'engin_materi'),  # 工程物资
        ('fix_asset_clean_up', 'fix_asset_clean_up'),  # 固定资产清理
        ('unconfirm_defer_incom_tax', 'unconfirm_defer_incom_tax'),  # 未确认递延所得税资产明细
        ('expir_in_the_follow_year', 'expir_in_the_follow_year'),  # 未确认递延所得税资产的可抵扣亏损将于以下年度到期
        ('other_noncurr_asset', 'other_noncurr_asset'),  # 其他非流动资产
        ('shortterm_loan', 'shortterm_loan'),  # 短期借款
        ('financi_liabil_measur_at_fair_valu', 'financi_liabil_measur_at_fair_valu'),  # 以公允价值计量且其变动计入当期损益的金融负债
        ('bill_payabl', 'bill_payabl'),  # 以公允价值计量且其变动计入当期损益的金融负债
        ('account_payabl', 'account_payabl'),  # 应付账款
        ('advanc_receipt', 'advanc_receipt'),  # 预收款项
        ('tax_payabl', 'tax_payabl'),  # 应交税费
        ('interest_payabl', 'interest_payabl'),  # 应付利息
        ('other_payabl', 'other_payabl'),  # 其他应付款
        ('noncurr_liabil_due_within_one_year', 'noncurr_liabil_due_within_one_year'),  # 1 年内到期的非流动负债
        ('bond_payabl', 'bond_payabl'),  # 应付债券
        ('undistributed_profit', 'undistributed_profit'),  # 未分配利润
        ('tax_and_surcharg', 'tax_and_surcharg'),  # 税金及附加
        ('sale_expens', 'sale_expens'),  # 销售费用
        ('manag_cost', 'manag_cost'),  # 管理费用
        ('financi_expens', 'financi_expens'),  # 管理费用
        ('asset_impair_loss', 'asset_impair_loss'),  # 资产减值损失
        ('chang_in_fair_valu', 'chang_in_fair_valu'),  # 公允价值变动损益
        ('invest_incom', 'invest_incom'),  # 投资收益
        ('nonoper_incom', 'nonoper_incom'),  # 营业外收入
        ('nonoper_expens', 'nonoper_expens'),  # 营业外支出
        ('incom_tax_expens', 'incom_tax_expens'),  # 所得税费用
        ('profit_to_incometax', 'profit_to_incometax'),  # 利润到所得税费用
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
    )
    subject = models.CharField(verbose_name='科目名称', max_length=30, choices=SUBJECT, default='')
    name = models.CharField(verbose_name='项目名称', max_length=150, default='')

class CommonBeforeAndEnd(CommonInfo):
    BEFORE_END = (
        ('b', 'before'),
        ('e', 'end'),
    )

    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='e')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CommonBeforeAndEndName,on_delete=models.CASCADE,verbose_name='项目名称')
    amount = models.DecimalField(verbose_name='金额', decimal_places=2, max_digits=22,
                                 default=0.00)
    instruct = models.CharField(verbose_name='说明', max_length=300, default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'before_end', 'name')

    def __str__(self):
        return '项目期初期末：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class CommonBICEName(models.Model):
    SUBJECT = (
        ('defer_incom', 'defer_incom'),  # 递延收益
        ('capit_reserv', 'capit_reserv'),  # 资本公积
        ('other_comprehens_incom', 'other_comprehens_incom'),  # 其他综合收益
        ('surplu_reserv', 'surplu_reserv'),  # 盈余公积


    )
    subject = models.CharField(verbose_name='科目名称', max_length=30, choices=SUBJECT, default='')
    name = models.CharField(verbose_name='项目名称', max_length=150, default='')

class CommonBICE(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CommonBICEName, on_delete=models.CASCADE, verbose_name='项目名称')
    before = models.DecimalField(verbose_name='期初金额', decimal_places=2, max_digits=22,
                                 default=0.00)
    increase = models.DecimalField(verbose_name='本期增加', decimal_places=2, max_digits=22,
                                   default=0.00)
    cut_back = models.DecimalField(verbose_name='本期减少', decimal_places=2, max_digits=22,
                                   default=0.00)
    end = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22,
                              default=0.00)
    instruct = models.CharField(verbose_name='说明', max_length=300, default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '通用期初本期增加本期减少期末：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class PayablEmployeCompensName(models.Model):
    SUBJECT = (
        ('p', 'PayablEmployeCompens'),  # 应付职工薪酬列示
        ('short', 'ShorttermCompens'),  # 短期薪酬
        ('set', 'SetTheDrawPlanList'),  # 设定提存计划

    )
    subject = models.CharField(verbose_name='科目名称', max_length=30, choices=SUBJECT, default='')
    name = models.CharField(verbose_name='项目名称',max_length=150,default='')

class PayablEmployeCompens(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(PayablEmployeCompensName, on_delete=models.CASCADE,verbose_name='项目名称')
    before = models.DecimalField(verbose_name='期初金额', decimal_places=2, max_digits=22,
                                 default=0.00)
    increase = models.DecimalField(verbose_name='本期增加', decimal_places=2, max_digits=22,
                                 default=0.00)
    cut_back = models.DecimalField(verbose_name='本期减少', decimal_places=2, max_digits=22,
                                   default=0.00)
    end = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22,
                                   default=0.00)
    instruct = models.CharField(verbose_name='说明', max_length=300, default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '应付职工薪酬：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class CommonBalancImpairNet(CommonInfo):
    BEFORE_END = (
        ('before', 'before'),
        ('end', 'end'),
    )
    SUBJECT = (
        ('inventori', 'inventori'),
        ('construct_in_progress', 'construct_in_progress'),
    )

    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
    subject = models.CharField(verbose_name='科目名称', max_length=30, choices=SUBJECT, default='')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='项目名称', max_length=150, default='')
    balance = models.DecimalField(verbose_name='余额', decimal_places=2, max_digits=22,
                                 default=0.00)
    impair = models.DecimalField(verbose_name='减值', decimal_places=2, max_digits=22,
                                  default=0.00)
    net = models.DecimalField(verbose_name='净值', decimal_places=2, max_digits=22,
                                 default=0.00)
    instruct = models.CharField(verbose_name='说明', max_length=300, default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'before_end', 'subject', 'name')

    def __str__(self):
        return '项目期初期末：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class OverduInterest(CommonInfo):
    SUBJECT = (
        ('interest_receiv', 'interest_receiv'),
        ('dividend_receiv', 'dividend_receiv'),
    )
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    subject = models.CharField(verbose_name='科目名称', max_length=30, choices=SUBJECT, default='interest_receiv')
    name = models.CharField(verbose_name='单位名称', max_length=150, default='')
    balanc = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22,
                                 default=0.00)
    overdu_time = models.CharField(verbose_name='逾期时间', max_length=150, default='')
    reason = models.CharField(verbose_name='逾期原因', max_length=300, default='')
    impair = models.CharField(verbose_name='是否发生减值及其判断依据', max_length=300, default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '重要逾期利息或一年以上的应收股利：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class InventoriImpairPrepar(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='项目名称', max_length=150, default='')
    before = models.DecimalField(verbose_name='期初余额', decimal_places=2, max_digits=22,
                                 default=0.00)
    accrual = models.DecimalField(verbose_name='本期计提增加', decimal_places=2, max_digits=22,
                                 default=0.00)
    other_increas = models.DecimalField(verbose_name='本期其他增加', decimal_places=2, max_digits=22,
                                  default=0.00)
    transferback_resel = models.DecimalField(verbose_name='转回或转销', decimal_places=2, max_digits=22,
                                        default=0.00)
    other_cut_back = models.DecimalField(verbose_name='其他减少', decimal_places=2, max_digits=22,
                                             default=0.00)
    end = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22,
                                         default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '存货跌价准备：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class ComprehensNote(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='项目名称', max_length=150, default='')
    inventori_capit_of_borrow_cost = models.DecimalField(verbose_name='存货年末余额中含有借款费用资本化金额',
                                                         decimal_places=2, max_digits=22,default=0.00)
    longterm_equiti_invest_desc = models.TextField(verbose_name='长期股权投资说明',default='')
    rd_intang_asset_per = models.DecimalField(verbose_name='内部研发形成的无形资产占无形资产余额的比例',
                                                         decimal_places=2, max_digits=22, default=0.00)
    shortterm_loan = models.TextField(verbose_name='短期借款分类的说明',default='' )
    capit_reserv = models.TextField(verbose_name='资本公积',default='' )
    foreign_busi_entiti_desc = models.TextField(verbose_name='境外经营实体说明',default='' )
    composit_of_enterpris_group = models.TextField(verbose_name='企业集团的构成',default='' )
    joint_ventur = models.TextField(verbose_name='重要的合营企业或联营企业',default='' )
    risk_relat_to_financi_instrument = models.TextField(verbose_name='与金融工具相关的风险',default='' )
    other_relat_transact = models.TextField(verbose_name='其他关联交易说明',default='' )
    relat_parti_commit = models.TextField(verbose_name='关联方承诺',default='' )
    import_commit = models.TextField(verbose_name='重要承诺事项',default='' )
    conting = models.TextField(verbose_name='或有事项',default='' )



    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep")

    def __str__(self):
        return '综合附注：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class ConstructContract(CommonInfo):
    SUBJECT = (
        ('i', 'inventori'),
        ('a', 'advanc_receipt'),
    )

    subject = models.CharField(verbose_name='存货/预收款项', max_length=30, choices=SUBJECT, default='')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    cost = models.DecimalField(verbose_name='累计已发生成本',decimal_places=2, max_digits=22, default=0.00)
    gross_profit = models.DecimalField(verbose_name='累计已确认毛利',decimal_places=2, max_digits=22, default=0.00)
    expect_loss = models.DecimalField(verbose_name='减：预计损失',decimal_places=2, max_digits=22, default=0.00)
    project_settlement = models.DecimalField(verbose_name='已办理结算的金额',decimal_places=2, max_digits=22, default=0.00)
    complet_settl = models.DecimalField(verbose_name='完工与结算差额',decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep",'subject')

    def __str__(self):
        return '建造合同形成的完工与结算差额情况：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class LongtermEquitiInvest(CommonInfo):

    COM_TYPE = (
        ('subsidiari', 'subsidiari'),
        ('joint_ventur', 'joint_ventur'),
        ('pool', 'pool'),
    )

    com_type = models.CharField(verbose_name='公司类型', max_length=30, choices=COM_TYPE, default='')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='被投资单位名称', max_length=150,default='')
    before = models.DecimalField(verbose_name='期初余额', decimal_places=2, max_digits=22, default=0.00)
    addit_invest = models.DecimalField(verbose_name='追加投资', decimal_places=2, max_digits=22, default=0.00)
    reduc_invest = models.DecimalField(verbose_name='减少投资', decimal_places=2, max_digits=22, default=0.00)
    invest_gain_and_loss = models.DecimalField(verbose_name='权益法下确认的投资损益', decimal_places=2, max_digits=22, default=0.00)
    other_comprehens_inc = models.DecimalField(verbose_name='其他综合收益调整', decimal_places=2, max_digits=22, default=0.00)
    chang_in_other_equit = models.DecimalField(verbose_name='其他权益变动', decimal_places=2, max_digits=22, default=0.00)
    cash_dividend_or_pro = models.DecimalField(verbose_name='宣告发放现金股利或利润', decimal_places=2, max_digits=22, default=0.00)
    provis_for_impair = models.DecimalField(verbose_name='计提减值准备', decimal_places=2, max_digits=22, default=0.00)
    other = models.DecimalField(verbose_name='其他', decimal_places=2, max_digits=22, default=0.00)
    end = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22, default=0.00)
    impair_balanc = models.DecimalField(verbose_name='减值准备期末余额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep",'name')

    def __str__(self):
        return '长期股权投资：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class FixAndIntangAssetType(models.Model):
    name = models.CharField(verbose_name='项目名称',max_length=150,default='',unique=True)

    def __str__(self):
        return '固定资产无形资产类别名称'

class FixAndIntangChangeType(models.Model):
    name = models.CharField(verbose_name='变动类型名称', max_length=150, default='',unique=True)

    def __str__(self):
        return '固定资产无形资产类别名称'

class FixAsset(CommonInfo):

    VALUE_CATEGORI = (
        ('o', 'origin_valu'),
        ('a', 'accumul_depreci'),
        ('i', 'impair_prepar'),
        ('n', 'net_worth'),
    )

    AMOUNT_TYPE = (
        ('b', 'before'),
        ('i', 'increas'),
        ('c', 'cut_back'),
        ('e', 'end'),
    )

    ASSET_TYPE =  (
        ('f', 'fix'),
        ('i', 'intang'),
    )

    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    asset_type = models.CharField(verbose_name='资产类别', max_length=30, choices=ASSET_TYPE, default='end')
    valu_categori = models.CharField(verbose_name='价值类别', max_length=30, choices=VALUE_CATEGORI, default='end')
    item = models.ForeignKey(FixAndIntangAssetType,on_delete=models.CASCADE,verbose_name='项目类别')
    increas_cut_back_type = models.ForeignKey(FixAndIntangChangeType,on_delete=models.CASCADE,verbose_name='增减类别')
    amount_type = models.CharField(verbose_name='金额类别' ,choices=AMOUNT_TYPE, max_length=150, default='')
    amount = models.DecimalField(verbose_name='金额', decimal_places=2, max_digits=22, default=0.00)



    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep",'asset_type','valu_categori','item','increas_cut_back_type')

    def __str__(self):
        return '固定资产无形资产：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class FixAssetStatu(CommonInfo):
    VALUE_CATEGORI = (
        ('o', 'origin_valu'),
        ('a', 'accumul_depreci'),
        ('i', 'impair_prepar'),
        ('n', 'net_worth'),
    )

    STATUS = (
        ('i', 'idl'),
        ('f', 'financi_leas_in'),
        ('b', 'busi_leas_out'),
    )

    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    valu_categori = models.CharField(verbose_name='价值类别', max_length=30, choices=VALUE_CATEGORI, default='end')
    item = models.ForeignKey(FixAndIntangAssetType,on_delete=models.CASCADE,verbose_name='项目')
    status = models.CharField(verbose_name='状态类别',choices=STATUS, max_length=150, default='')
    amount = models.DecimalField(verbose_name='金额', decimal_places=2, max_digits=22, default=0.00)
    instruct = models.TextField(verbose_name='说明',default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'valu_categori', 'item','status')

    def __str__(self):
        return '固定资产状态：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class UnfinishProperti(CommonInfo):
    ASSET_CATEGORI = (
        ('f', 'fixasset'),
        ('i', 'intang_asset'),
    )

    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    asset_categori = models.CharField(verbose_name='价值类别', max_length=30, choices=ASSET_CATEGORI, default='end')
    item = models.CharField(verbose_name='项目', max_length=150, default='')
    amount = models.DecimalField(verbose_name='账面价值', decimal_places=2, max_digits=22, default=0.00)
    reason = models.TextField(verbose_name='未办妥产权证书的原因', default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'asset_categori', 'item')

    def __str__(self):
        return '未办妥产权：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class ImportProjectChange(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='项目名称', max_length=150, default='')
    budget = models.CharField(verbose_name='预算数', max_length=150, default='')
    before = models.DecimalField(verbose_name='期初余额', decimal_places=2, max_digits=22, default=0.00)
    increas = models.DecimalField(verbose_name='本期增加金额', decimal_places=2, max_digits=22, default=0.00)
    transfer_to_fix_asset = models.DecimalField(verbose_name='本期转入固定资产金额', decimal_places=2, max_digits=22, default=0.00)
    other_reduct = models.DecimalField(verbose_name='本期其他减少金额', decimal_places=2, max_digits=22, default=0.00)
    end = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22, default=0.00)
    percentag_of_budget = models.CharField(verbose_name='工程累计投入占预算比例', max_length=150, default='')
    progress = models.CharField(verbose_name='工程进度', max_length=150, default='')
    interest_capit_cumul_amount = models.DecimalField(verbose_name='利息资本化累计金额', decimal_places=2, max_digits=22, default=0.00)
    interest_capit_current_amount = models.DecimalField(verbose_name='其中：本期利息资本化金额', decimal_places=2, max_digits=22, default=0.00)
    interest_capit_rate = models.DecimalField(verbose_name='本期利息资本化率', decimal_places=2, max_digits=22, default=0.00)
    sourc_of_fund = models.CharField(verbose_name='资金来源', max_length=150, default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep",  'name')

    def __str__(self):
        return '在建工程：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class DevelopExpenditur(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='项目名称', max_length=150, default='')
    before = models.DecimalField(verbose_name='期初余额', decimal_places=2, max_digits=22, default=0.00)
    increas_rd = models.DecimalField(verbose_name='内部开发支出', decimal_places=2, max_digits=22, default=0.00)
    increas_other = models.DecimalField(verbose_name='其他增加', decimal_places=2, max_digits=22, default=0.00)
    transfer_to_intang_asset = models.DecimalField(verbose_name='确认为无形资产', decimal_places=2, max_digits=22,
                                                default=0.00)
    transfer_to_profit = models.DecimalField(verbose_name='转入当期损益', decimal_places=2, max_digits=22, default=0.00)
    end = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22, default=0.00)


    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '开发支出：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class Goodwil(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='单位名称或事项', max_length=150, default='')
    before = models.DecimalField(verbose_name='期初余额', decimal_places=2, max_digits=22, default=0.00)
    busi_merger = models.DecimalField(verbose_name='企业合并形成', decimal_places=2, max_digits=22, default=0.00)
    other_increas = models.DecimalField(verbose_name='其他增加', decimal_places=2, max_digits=22, default=0.00)
    dispos = models.DecimalField(verbose_name='处置', decimal_places=2, max_digits=22,
                                                   default=0.00)
    other_reduct = models.DecimalField(verbose_name='其他减少', decimal_places=2, max_digits=22, default=0.00)
    end = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '商誉：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class LongtermPrepaidExpens(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='项目', max_length=150, default='')
    before = models.DecimalField(verbose_name='期初余额', decimal_places=2, max_digits=22, default=0.00)
    increas = models.DecimalField(verbose_name='本期增加金额', decimal_places=2, max_digits=22, default=0.00)
    amort = models.DecimalField(verbose_name='本期摊销金额', decimal_places=2, max_digits=22, default=0.00)
    other_reduct = models.DecimalField(verbose_name='其他减少', decimal_places=2, max_digits=22, default=0.00)
    end = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '长期待摊费用：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class DeferIncomTaxName(models.Model):
    name = models.CharField(verbose_name='递延所得税资产/负债项目名称',max_length=150,default='',unique=True)

class DeferIncomTax(CommonInfo):
    BEFORE_END = (
        ('b', 'before'),
        ('e', 'end'),
    )
    SUBJECT = (
        ('a', 'defer_tax_asset'),
        ('d', 'defer_tax_debt'),
    )

    subject = models.CharField(verbose_name='递延所得税资产/递延所得税负债', max_length=30, choices=SUBJECT, default='')
    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='end')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(DeferIncomTaxName, on_delete=models.CASCADE, verbose_name='项目')
    diff = models.DecimalField(verbose_name='差异金额', decimal_places=2, max_digits=22, default=0.00)
    amount = models.DecimalField(verbose_name='所得税资产/负债金额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep",'before_end','subject', 'name')

    def __str__(self):
        return '递延所得税资产/递延所得税负债：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class MajorLiabilAgeOver1Year(CommonInfo):
    SUBJECT = (
        ('ap', 'account_payabl'),
        ('ar', 'advanc_receipt'),
        ('ip', 'interest_payabl'),
        ('op', 'other_payabl'),
    )

    subject = models.CharField(verbose_name='科目名称', max_length=30, choices=SUBJECT, default='')
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='项目名称',max_length=150,default='')
    amount = models.DecimalField(verbose_name='期末金额', decimal_places=2, max_digits=22, default=0.00)
    reason = models.TextField(verbose_name='原因',default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep",  'subject', 'name')

    def __str__(self):
        return '账龄超过1年的重要负债或逾期利息：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class ChangInBondPayabl(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='债券名称', max_length=150, default='')
    face_valu = models.DecimalField(verbose_name='面值', decimal_places=2, max_digits=22, default=0.00)
    date = models.CharField(verbose_name='发行日期', max_length=150, default='')
    term = models.CharField(verbose_name='债券期限', max_length=150, default='')
    amount = models.DecimalField(verbose_name='发行金额', decimal_places=2, max_digits=22, default=0.00)
    before = models.DecimalField(verbose_name='期初余额', decimal_places=2, max_digits=22, default=0.00)
    issu = models.DecimalField(verbose_name='本期发行', decimal_places=2, max_digits=22, default=0.00)
    interest = models.DecimalField(verbose_name='按面值计提利息', decimal_places=2, max_digits=22, default=0.00)
    discount_amort = models.DecimalField(verbose_name='溢折价摊销', decimal_places=2, max_digits=22, default=0.00)
    repay = models.DecimalField(verbose_name='本期偿还', decimal_places=2, max_digits=22, default=0.00)
    other_reduct = models.DecimalField(verbose_name='其他减少', decimal_places=2, max_digits=22, default=0.00)
    end = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep",  'name')

    def __str__(self):
        return '应付债券增减变动：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class GovernSubsidi(CommonInfo):
    SUBJECT = (
        ('a', 'relat_to_asset'),  # 与资产相关
        ('e', 'relat_to_earn'),  # 与收益相关

    )
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CommonBeforeAndEndName,on_delete=models.CASCADE,verbose_name='项目名称')
    before = models.DecimalField(verbose_name='期初余额', decimal_places=2, max_digits=22, default=0.00)
    new = models.DecimalField(verbose_name='本期新增补助金额', decimal_places=2, max_digits=22, default=0.00)
    includ_nonoper_incom = models.DecimalField(verbose_name='本期计入营业外收入金额', decimal_places=2, max_digits=22, default=0.00)
    other = models.DecimalField(verbose_name='其他减少', decimal_places=2, max_digits=22, default=0.00)
    end = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22, default=0.00)
    relat = models.CharField(verbose_name='与资产相关/与收益相关', max_length=30, choices=SUBJECT, default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name','relat')

    def __str__(self):
        return '政府补助项目：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class AllGovernSubsidi(CommonInfo):
    SUBJECT = (
        ('a', 'relat_to_asset'),  # 与资产相关
        ('e', 'relat_to_earn'),  # 与收益相关

    )
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CommonBeforeAndEndName,on_delete=models.CASCADE,verbose_name='项目名称')
    amount = models.DecimalField(verbose_name='项目金额', decimal_places=2, max_digits=22, default=0.00)
    includ_profit = models.DecimalField(verbose_name='计入当期损益的金额', decimal_places=2, max_digits=22, default=0.00)
    relat = models.CharField(verbose_name='与资产相关/与收益相关', max_length=30, choices=SUBJECT, default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name','relat')

    def __str__(self):
        return '所有的政府补助项目：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class OtherComprehensIncom(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CommonBICEName,on_delete=models.CASCADE,verbose_name='项目名称')
    before = models.DecimalField(verbose_name='期初余额', decimal_places=2, max_digits=22, default=0.00)
    amount_before_tax = models.DecimalField(verbose_name='本期所得税前发生额', decimal_places=2, max_digits=22, default=0.00)
    less_transfer_to_profit = models.DecimalField(verbose_name='减：前期计入其他综合收益当期转入损益', decimal_places=2, max_digits=22,
                                               default=0.00)
    less_income_tax = models.DecimalField(verbose_name='减：所得税费用', decimal_places=2, max_digits=22, default=0.00)
    posttax_attribut_to_parent_compan = models.DecimalField(verbose_name='税后归属于母公司', decimal_places=2, max_digits=22, default=0.00)
    posttax_attribut_to_minor_share = models.DecimalField(verbose_name='税后归属于少数股东', decimal_places=2, max_digits=22, default=0.00)
    end = models.DecimalField(verbose_name='期末余额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '其他综合收益：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class OperIncomAndOperCost(CommonInfo):
    SUBJECT = (
        ('i', 'income'),  # 营业收入
        ('c', 'cost'),  # 营业成本

    )

    SERVIC_CATEGORI = (
        ('m', 'main_busi'),  # 主营业务
        ('o', 'other_busi'),  # 其他业务
        ('t', 'total'),  # 汇总

    )
    BEFORE_END = (
        ('b', 'before'),
        ('e', 'end'),
    )

    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    before_end = models.CharField(verbose_name='期初期末', max_length=30, choices=BEFORE_END, default='e')
    subject = models.CharField(verbose_name='营业收入/营业成本', max_length=30, choices=SUBJECT, default='')
    servic_categori = models.CharField(verbose_name='业务类别', max_length=30, choices=SERVIC_CATEGORI, default='')
    amount = models.DecimalField(verbose_name='金额', decimal_places=2, max_digits=22, default=0.00)


    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'before_end','subject','servic_categori')

    def __str__(self):
        return '营业收入及营业成本：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class GovernSubsidiIncludInCurrentProfit(CommonInfo):
    SUBJECT = (
        ('a', 'relat_to_asset'),  # 与资产相关
        ('e', 'relat_to_earn'),  # 与收益相关

    )
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.CharField(verbose_name='项目名称',max_length=150,default='')
    issu_subject = models.CharField(verbose_name='发放主体',max_length=150,default='')
    issu_reason = models.CharField(verbose_name='发放原因',max_length=300,default='')
    natur_type = models.CharField(verbose_name='性质类型',max_length=150,default='')
    doe_it_affect_profit = models.CharField(verbose_name='补贴是否影响当年盈亏',max_length=150,default='')
    is_special = models.CharField(verbose_name='是否特殊补贴 ',max_length=150,default='')
    before = models.DecimalField(verbose_name='上期金额', decimal_places=2, max_digits=22, default=0.00)
    end = models.DecimalField(verbose_name='本期金额', decimal_places=2, max_digits=22, default=0.00)
    relat = models.CharField(verbose_name='与资产相关/与收益相关', max_length=30, choices=SUBJECT, default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '计入当期损益的政府补助：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class NonoperIncomExpens(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CommonBeforeAndEndName,on_delete=models.CASCADE, verbose_name='项目名称')
    end = models.DecimalField(verbose_name='本期金额', decimal_places=2, max_digits=22, default=0.00)
    before = models.DecimalField(verbose_name='上期金额', decimal_places=2, max_digits=22, default=0.00)
    nonrecur_gain_amount = models.DecimalField(verbose_name='计入当期非经常性损益的金额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep",  'name')

    def __str__(self):
        return '营业外收入与支出：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class ItemAmountReason(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    name = models.ForeignKey(CommonBeforeAndEndName, on_delete=models.CASCADE, verbose_name='项目名称')
    amount = models.DecimalField(verbose_name='金额', decimal_places=2, max_digits=22, default=0.00)
    reason = models.CharField(verbose_name='说明',default='',max_length=300)


    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'name')

    def __str__(self):
        return '项目金额说明：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class SubjectName(models.Model):
    name = models.CharField(verbose_name='科目名称', max_length=30, default='',unique=True)

class CurrencName(models.Model):
    name = models.CharField(verbose_name='外币名称', max_length=30, default='',unique=True)

class ForeignCurrencItem(CommonInfo):
    typ_rep = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name='报表类型')
    subject = models.ForeignKey(SubjectName,on_delete=models.CASCADE,verbose_name='科目名称')
    currenc = models.ForeignKey(CurrencName,on_delete=models.CASCADE,verbose_name='币种')
    foreign_bala = models.DecimalField(verbose_name='外币余额', decimal_places=2, max_digits=22, default=0.00)
    exchang_rate = models.DecimalField(verbose_name='汇率', decimal_places=2, max_digits=22, default=0.00)
    rmb_bala = models.DecimalField(verbose_name='人民币余额', decimal_places=2, max_digits=22, default=0.00)

    class Meta:
        unique_together = ("stk_cd", "acc_per", "typ_rep", 'subject','currenc')

    def __str__(self):
        return '外币货币性项目：{}于{}的{}'.format(self.stk_cd, self.acc_per, self.typ_rep)

class CompanyName(models.Model):
    NATURE = (
        ('s', 'subcompani'),#子公司
        ('j', 'joint_ventur'),#合营企业
        ('p', 'pool'),#联营企业
    )
    natur_of_the_unit = models.CharField(verbose_name='单位性质', max_length=30, choices=NATURE, default='s')
    name = models.CharField(verbose_name='公司名称', max_length=150, default='',unique=True)



