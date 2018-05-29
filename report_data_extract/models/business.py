from django.db import models
from .standard import CommonInfo,StandardTables,StdContentIndex
# Create your models here.

class StoragRegistrForm(CommonInfo):
    '''
    表信息存储记录表
    '''
    table = models.ForeignKey(StandardTables,on_delete=models.CASCADE,verbose_name='标准表')
    is_exist = models.BooleanField(verbose_name='表是否存在')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','table')

class TableAttr(models.Model):
    indexno = models.ForeignKey(StdContentIndex, verbose_name='标准索引', on_delete=models.CASCADE)
    columns = models.TextField(verbose_name='列字段',default='')
    indexes = models.TextField(verbose_name='行字段',default='')

    class Meta:
        unique_together = ("indexno", "columns", "indexes")

    def __str__(self):
        return '提取标准索引:{}列名{}行名{}'.format(self.indexno.name, self.columns, self.indexes)






