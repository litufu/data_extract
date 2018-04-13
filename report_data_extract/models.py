from django.db import models

# Create your models here.

class TempParseHtml(models.Model):

    pageNum = models.IntegerField(verbose_name='文件页码',default=0)
    cellText = models.CharField(verbose_name='页面元素内容',max_length=200,blank=True)
    cellCategory = models.CharField(verbose_name='页面元素分类',max_length=1)


class ContentIndex(models.Model):

    name = models.CharField(verbose_name='索引名称',max_length=100)
    fatherid = models.IntegerField(verbose_name='父索引id')
    no = models.CharField(verbose_name='索引编号',max_length=10)

class TempIndexCellCount(models.Model):

    name = models.CharField(verbose_name='索引名称',max_length=100)
    no = models.CharField(verbose_name='索引编号',max_length=10)
    start_id = models.IntegerField(verbose_name='元素开始位置')
    end_id = models.IntegerField(verbose_name='元素结束位置')

