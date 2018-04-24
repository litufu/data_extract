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

    compare_name = models.CharField(verbose_name='索引名称',max_length=100)
    index_name = models.ForeignKey(StdContentIndex,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('compare_name', 'index_name',)


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