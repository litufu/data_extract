# _author : litufu
# date : 2018/4/15
from django.db import models

class StdContentIndex(models.Model):

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

    compare_name = models.CharField(verbose_name='索引名称',max_length=100)
    index_name = models.ForeignKey(StdContentIndex,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('compare_name', 'index_name',)
