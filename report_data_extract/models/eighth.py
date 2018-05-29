# _author : litufu
# date : 2018/4/27

from django.db import models
from .standard import CommonInfo

class ChangInShareholdAndRemuner(CommonInfo):
    name = models.CharField(verbose_name='姓名',max_length=150,default='')
    job_titl = models.CharField(verbose_name='职务',max_length=150,default='')
    sex = models.CharField(verbose_name='性别',max_length=1,default='')
    age = models.DecimalField(verbose_name='年龄',max_digits=22,decimal_places=2,default=0.00,blank=True,null=True)
    term_start_date = models.CharField(verbose_name='任期起始日期',max_length=30,default='')
    term_end_date = models.CharField(verbose_name='任期终止日期',max_length=30,default='')
    share_held_num_begin = models.DecimalField(verbose_name='期初持股数',max_digits=22,decimal_places=2,default=0.00,blank=True,null=True)
    share_held_num_end = models.DecimalField(verbose_name='期末持股数',max_digits=22,decimal_places=2,default=0.00,blank=True,null=True)
    increas_or_decreas_num = models.DecimalField(verbose_name='股份增减变动量',max_digits=22,decimal_places=2,default=0.00,blank=True,null=True)
    change_reason = models.TextField(verbose_name='增减变动原因',default='')
    pre_tax_compens = models.DecimalField(verbose_name='报告期内从公司获得的税前报酬总额',max_digits=22,decimal_places=2,default=0.00,blank=True,null=True)
    is_get_compens_from_relat = models.CharField(verbose_name='是否在公司关联方获取报酬',default='',max_length=1)
    work_experi = models.TextField(verbose_name='主要工作经历',default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','name','job_titl','age')

class WorkInSharehold(CommonInfo):
    name = models.ForeignKey(ChangInShareholdAndRemuner,on_delete=models.CASCADE)
    name_of_sharehold = models.CharField(verbose_name='股东单位名称', default='', max_length=150)
    job_titl_in_sharehold_com = models.CharField(verbose_name='在股东单位担任的职务', default='', max_length=150)
    start_date_in_sharehold_com = models.CharField(verbose_name='在股东单位任期起始日期', default='', max_length=150)
    end_date_in_sharehold_com = models.CharField(verbose_name='在股东单位任期终止日期', default='', max_length=150)
    job_titl_chang_reason = models.TextField(verbose_name='任职变动原因', default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','name','name_of_sharehold','job_titl_in_sharehold_com')


class WorkInOtherUnit(CommonInfo):
    name = models.ForeignKey(ChangInShareholdAndRemuner,on_delete=models.CASCADE)
    company = models.CharField(verbose_name='其他单位名称', default='', max_length=150)
    job_titl = models.CharField(verbose_name='在其他单位担任的职务', default='', max_length=150)
    start_date = models.CharField(verbose_name='在其他单位任期起始日期', default='', max_length=150)
    end_date = models.CharField(verbose_name='在其他单位任期终止日期', default='', max_length=150)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','name','company','job_titl')

class NumberOfEmploye(CommonInfo):
    parent_compani = models.IntegerField(verbose_name='母公司在职员工的数量',default=0)
    subsidiari = models.IntegerField(verbose_name='主要子公司在职员工的数量',default=0)
    total = models.IntegerField(verbose_name='在职员工的数量合计',default=0)
    retir_num = models.IntegerField(verbose_name='母公司及主要子公司需承担费用的离退休职工人数',default=0)
    remuner_polici = models.TextField(verbose_name='薪酬政策',default='')
    train_program = models.TextField(verbose_name='培训计划',default='')
    outsourc = models.TextField(verbose_name='劳务外包',default='')

    class Meta:
        unique_together = ('stk_cd', 'acc_per')

class  ProfessionOfEmploye(CommonInfo):
    MAJOR_CLASS = (
        ('product', 'product'),
        ('sale', 'sale'),
        ('technic', 'technic'),
        ('financi', 'financi'),
        ('administr', 'administr'),
        ('other', 'other'),
        ('total', 'total'),

    )
    employe_type = models.CharField(verbose_name='人员类别', choices=MAJOR_CLASS, max_length=15, blank=True)
    num = models.IntegerField(verbose_name='人员数量', default=0)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','employe_type')


class  EduOfEmploye(CommonInfo):
    level = models.CharField(verbose_name='学历水平', max_length=100,default='')
    num = models.IntegerField(verbose_name='人员数量', default=0)

    class Meta:
        unique_together = ('stk_cd', 'acc_per','level')