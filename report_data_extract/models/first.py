# _author : litufu
# date : 2018/4/18
from django.db import models
from .standard import CommonInfo
# Create your models here.

class Interpret(CommonInfo):
    interpret_item = models.CharField(verbose_name='释义项',max_length=150,default='')
    definit = models.CharField(verbose_name='释义内容',max_length=300,default='')

    class Meta:
        unique_together = ("stk_cd", "acc_per","interpret_item")
