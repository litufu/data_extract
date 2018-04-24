# _author : litufu
# date : 2018/4/20
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
from report_data_extract.models import *

def isTableExist(tablename,stk_cd_id,acc_per):
    Table = eval(tablename)
    table_id = Table.objects.get(tablename=tablename.lower()).id
    if Table.objects.filter(stk_cd_id=stk_cd_id, acc_per=acc_per):
        if StoragRegistrForm.objects.filter(stk_cd_id=stk_cd_id, acc_per=acc_per,
                                                   table_id=table_id):
            obj1 = StoragRegistrForm.objects.get(stk_cd_id=stk_cd_id, acc_per=acc_per,
                                                        table_id=table_id)
            obj1.is_exist = True
            obj1.save()
        else:
            StoragRegistrForm.objects.create(stk_cd_id=stk_cd_id, acc_per=acc_per,
                                                    table_id=table_id, is_exist=True)

    else:
        if StoragRegistrForm.objects.filter(stk_cd_id=stk_cd_id, acc_per=acc_per,
                                               table_id=table_id):
            obj1 = StoragRegistrForm.objects.get(stk_cd_id=stk_cd_id, acc_per=acc_per,
                                                        table_id=table_id)
            obj1.is_exist = False
            obj1.save()
        else:
            StoragRegistrForm.objects.create(stk_cd_id=stk_cd_id, acc_per=acc_per,
                                                    table_id=table_id, is_exist=False)


