# _author : litufu
# date : 2018/4/18

from django.db import models
from .standard import CommonInfo

class CompaniBusiOverview(CommonInfo):
    major_busi_model_indu = models.TextField(verbose_name='主要业务、经营模式及行业情况', default='')
    major_chang_in_major_asset = models.TextField(verbose_name='主要资产发生重大变化', default='')
    core_competit = models.TextField(verbose_name='核心竞争力', default='')
    major_asset = models.CharField(verbose_name='主要资产', max_length=150, default='')
    change_reason = models.TextField(verbose_name='变动原因说明', default='')
    major_oversea_asset = models.TextField(verbose_name='主要境外资产情况', default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per')


class MajorOverseaAsset(CommonInfo):
    asset_contents = models.CharField(verbose_name='资产的具体内容', max_length=150, default='')
    caus_of_format = models.CharField(verbose_name='形成原因', max_length=150, default='')
    asset_size = models.CharField(verbose_name='资产规模', max_length=150, default='')
    locat = models.CharField(verbose_name='所在地', max_length=150, default='')
    oper_mode = models.CharField(verbose_name='运营模式', max_length=150, default='')
    control_measur = models.CharField(verbose_name='保障资产安全性的控制措施', max_length=300, default='')
    revenu_statu = models.CharField(verbose_name='收益状况', max_length=150, default='')
    proport_of_oversea = models.CharField(verbose_name='境外资产占公司净资产的比重', max_length=150, default='')
    impair_risk = models.CharField(verbose_name='是否存在重大减值风险', max_length=150, default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per')
