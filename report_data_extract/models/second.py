# _author : litufu
# date : 2018/4/18

from django.db import models
from .standard import CommonInfo

class CompaniProfil(CommonInfo):
    chines_name = models.CharField(verbose_name='公司的中文名称', max_length=150, default='')
    chines_abbrevi = models.CharField(verbose_name='公司的中文简称', max_length=150, default='')
    foreign_name = models.CharField(verbose_name='公司的外文名称', max_length=150, default='')
    foreign_abbrevi = models.CharField(verbose_name='公司的外文名称缩写', max_length=150, default='')
    legal_repres = models.CharField(verbose_name='公司的法定代表人', max_length=150, default='')
    board_secretary_nam = models.CharField(verbose_name='董秘姓名', max_length=150, default='')
    board_secretary_addr = models.CharField(verbose_name='董秘联系地址', max_length=150, default='')
    board_secretary_tel = models.CharField(verbose_name='董秘联系电话', max_length=150, default='')
    board_secretary_fax = models.CharField(verbose_name='董秘传真', max_length=150, default='')
    board_secretary_email = models.CharField(verbose_name='董秘邮箱', max_length=150, default='')
    compani_regist_addre = models.CharField(verbose_name='公司注册地址', max_length=150, default='')
    postal_regist = models.CharField(verbose_name='公司注册地址的邮政编码', max_length=150, default='')
    compani_offic_addres = models.CharField(verbose_name='公司办公地址', max_length=150, default='')
    postal_offic = models.CharField(verbose_name='公司办公地址的邮政编码', max_length=150, default='')
    compani_websit = models.CharField(verbose_name='公司网址', max_length=150, default='')
    compani_email = models.CharField(verbose_name='公司电子信箱', max_length=150, default='')
    organ_code = models.CharField(verbose_name='组织机构代码', max_length=100, default='')
    chang_in_main_busi = models.CharField(verbose_name='主营业务变更情况', max_length=400, default='')
    chang_in_control_sha = models.CharField(verbose_name='控股股东变更情况', max_length=400, default='')
    account_firm_name = models.CharField(verbose_name='会计师事务所名称', max_length=150, default='')
    account_offic_addres = models.CharField(verbose_name='会计师事务所办公地址', max_length=150, default='')
    sign_accountant_nam = models.CharField(verbose_name='签字注册会计师', max_length=100, default='')
    sponsor_name = models.CharField(verbose_name='保荐机构名称', max_length=100, default='')
    sponsor_addres = models.CharField(verbose_name='保荐机构地址', max_length=100, default='')
    sponsor_repr = models.CharField(verbose_name='保荐代表人', max_length=100, default='')
    continu_supervis_per = models.CharField(verbose_name='持续督导的期间', max_length=10, default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per')

