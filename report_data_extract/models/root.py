# _author : litufu
# date : 2018/4/15

from django.db import models
from .standard import StdContentIndex,IndexHandleMethod

# Create your models here.
class TableDesc(models.Model):
    app_label = models.CharField(verbose_name='app名称',max_length=150,default='')
    model_name =  models.CharField(verbose_name='模型名称',max_length=150,default='')
    table_name = models.CharField(verbose_name='数据库表名',max_length=150,default='',unique=True)
    part = models.CharField(verbose_name='所述部分',max_length=150,default='')
    unique_together = models.CharField(verbose_name='联合唯一',max_length=300,default='')
    table_desc = models.CharField(verbose_name='表文件描述',max_length=200,blank=True,default='')

    def __str__(self):
        return '报告存储表:{}'.format(self.table_name)

class FieldDesc(models.Model):
    table = models.ForeignKey(TableDesc, on_delete=models.CASCADE, verbose_name='表名')
    f_name = models.CharField(verbose_name='字段名称',max_length=150,default='')
    f_type = models.CharField(verbose_name='字段类型',max_length=150,default='')
    f_verbose_name = models.CharField(verbose_name='中文名称',max_length=150,default='')
    f_detail_name = models.CharField(verbose_name='详细中文名称',max_length=200,default='')
    f_desc = models.CharField(verbose_name='字段描述',max_length=200,blank=True,default='')
    foreignkey = models.CharField(verbose_name='外键',blank=True,max_length=150,default='')
    choices = models.TextField(verbose_name='选项', blank=True,default='')
    is_unique = models.CharField(verbose_name='是否唯一', max_length=150,blank=True,default='')


    class Meta:
        unique_together = ("table", "f_name")

    def __str__(self):
        return '字段描述:{}表的字段{}'.format(self.table.model_name,self.f_name)

class VerboseName2Field(models.Model):
    verbose = models.CharField(verbose_name='verbose_name',max_length=200,default='',unique=True)
    field = models.CharField(verbose_name='field_name',max_length=200,default='')

class Indexno2Table(models.Model):
    indexno = models.ForeignKey(StdContentIndex, verbose_name='标准索引', on_delete=models.CASCADE)
    table = models.ForeignKey(TableDesc, on_delete=models.CASCADE, verbose_name='表')
    table_name = models.CharField(verbose_name='表名',max_length=150,default='')

    class Meta:
        unique_together = ("indexno", "table")

class Handleclass2Table(models.Model):
    handleclass =  models.ForeignKey(IndexHandleMethod, verbose_name='类处理名称', on_delete=models.CASCADE)
    table = models.ForeignKey(TableDesc, on_delete=models.CASCADE, verbose_name='表')
    table_name = models.CharField(verbose_name='表名', max_length=150, default='')

    class Meta:
        unique_together = ("handleclass", "table")

class Text2Field(models.Model):
    indexno = models.ForeignKey(StdContentIndex,verbose_name='标准索引',on_delete=models.CASCADE)
    table = models.ForeignKey(TableDesc, on_delete=models.CASCADE, verbose_name='表名')
    text = models.CharField(verbose_name='原始字段文本',max_length=150,default='')
    field = models.ForeignKey(VerboseName2Field,verbose_name='标准字段',on_delete=models.CASCADE)

    class Meta:
        unique_together = ("indexno", "table","text")

    def __str__(self):
        return '标准索引:{}表名{}的字段{}'.format(self.indexno.name,self.table.model_name,self.text)

class RootTableDesc(models.Model):
    tablename = models.CharField(verbose_name='表英文名',max_length=100,blank=True)
    table_cn_name = models.CharField(verbose_name='表中文名',max_length=100,blank=True)
    class_str = models.CharField(verbose_name='表文件描述',max_length=200,blank=True,default='')
    functions = models.TextField(verbose_name='表内函数',blank=True,default='')
    meta= models.TextField(verbose_name='表相关信息',blank=True,default='')

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


