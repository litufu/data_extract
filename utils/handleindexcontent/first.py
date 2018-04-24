# _author : litufu
# date : 2018/4/18
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
from utils.mytools import HandleIndexContent,NotFoundHandleClassException
from report_data_extract import models
import pandas as pd

class Interpret(HandleIndexContent):
    def __init__(self,stk_cd_id,acc_per ,indexno, indexcontent):
        super(Interpret, self).__init__(stk_cd_id,acc_per,indexno,indexcontent)

    def recognize(self):
        df = None
        if self.indexno in ['0101000000','01000000']:
            for content in self.indexcontent:
                for classify,item in content.items():
                    if classify == 'c' and len(item)>0:
                        df = item[0][0]
                    else:
                        pass
        else:
            pass
        return df

    def converse(self):

        df = self.recognize()
        if df is not None:
            if df.iloc[0,:].str.contains('释义').any():
                df_new = df.drop([0,])
            else:
                df_new = df
        else:
            df_new = None
        return df_new


    def logic(self):
        pass

    def save(self):
        df  = self.converse()
        table_id = models.StandardTables.objects.get(tablename='interpret').id
        if df is not None:
            # 将第一列赋值给字段interpret_item，将第二列赋值给字段definit
            interpret_items = list(df.iloc[:, 0])
            definits = list(df.iloc[:, 2])
            for interpret_item, definit in zip(interpret_items, definits):
                if models.Interpret.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, interpret_item=interpret_item,
                                                definit=definit):
                    obj = models.Interpret.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, interpret_item=interpret_item,
                                                definit=definit)
                    obj.interpret_item = interpret_item
                    obj.definit = definit
                    obj.save()
                else:
                    models.Interpret.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per, interpret_item=interpret_item,
                                                    definit=definit)
            if models.StoragRegistrForm.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       table_id=table_id):
                obj1 = models.StoragRegistrForm.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       table_id=table_id)
                obj1.is_exist = True
                obj1.save()
            else:
                models.StoragRegistrForm.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                    table_id=table_id, is_exist=True)
        else:
            if models.StoragRegistrForm.objects.filter(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                       table_id=table_id):
                obj1 = models.StoragRegistrForm.objects.get(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                            table_id=table_id)
                obj1.is_exist = False
                obj1.save()
            else:
                models.StoragRegistrForm.objects.create(stk_cd_id=self.stk_cd_id, acc_per=self.acc_per,
                                                    table_id=table_id, is_exist=False)

