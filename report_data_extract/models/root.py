# _author : litufu
# date : 2018/4/15

from django.db import models

# Create your models here.
class RootTableDesc(models.Model):
    tablename = models.CharField(verbose_name='表英文名',max_length=100,blank=True)
    table_cn_name = models.CharField(verbose_name='表中文名',max_length=100,blank=True)
    class_str = models.CharField(verbose_name='表文件描述',max_length=200,blank=True)
    functions = models.TextField(verbose_name='表内函数',blank=True)
    meta= models.TextField(verbose_name='表相关信息',blank=True)

class RootTables(models.Model):
    TABLE_CLASS = (
        ('temp', 'temp'),
        ('business', 'business'),
    )
    tableclass = models.CharField(verbose_name='表类别',choices=TABLE_CLASS,max_length=10,blank=True)
    tablename = models.ForeignKey(RootTableDesc,on_delete=models.CASCADE)
    fieldname = models.CharField(verbose_name='字段名',max_length=100,blank=True)
    fieldtype = models.CharField(verbose_name='字段类型',max_length=100,blank=True)
    maxlengeth = models.IntegerField(verbose_name='字段长度',blank=True,null=True)
    isunique = models.BooleanField(verbose_name='是否唯一')
    ispk = models.BooleanField(verbose_name='是否为关键索引')
    isblank = models.BooleanField(verbose_name='是否可以输入空值')
    isnull = models.BooleanField(verbose_name='数据库显示为空')
    isunique_together = models.BooleanField(verbose_name='是否联合唯一',blank=True)
    choices = models.TextField(verbose_name='下拉选项',blank=True)
    default = models.TextField(verbose_name='默认值',blank=True)
    verbosename= models.TextField(verbose_name='字段别名',blank=True)
    foreignkey= models.TextField(verbose_name='外键',blank=True)


