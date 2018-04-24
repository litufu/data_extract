from django.db import models
from .standard import CommonInfo,StandardTables
# Create your models here.

class StoragRegistrForm(CommonInfo):
    '''
    表信息存储记录表
    '''
    table = models.ForeignKey(StandardTables,on_delete=models.CASCADE,verbose_name='标准表')
    is_exist = models.BooleanField(verbose_name='表是否存在')

    class Meta:
        unique_together = ('stk_cd', 'acc_per','table')






