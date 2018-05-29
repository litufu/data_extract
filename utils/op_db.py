# _author : litufu
# date : 2018/4/15
from report_data_extract.models import root

import subprocess
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
filepath = os.path.join(os.path.join(BASE_DIR,'report_data_extract'),'models')

def add_roottabledesc():
    root.RootTableDesc.objects.create(
        tablename='StdContentIndex',
        table_cn_name = '标准索引表',
        class_str=json.dumps(['def __str__(self):','return self.name']),
        functions='',
        meta = {"verbose_name" : "标准索引表"}
    )


def add_root():
    root.RootTables.objects.create(
        tableclass='std',
        tablename='StdContentIndex',
        fieldname='market',
        fieldtype='CharField',
        maxlengeth=2,
        isunique=False,
        ispk=False,
        isblank=True,
        isnull = False,
        isunique_together = True,
        choices = '',
        default = '',
        verbosename = '证券市场',
        foreignkey = '',

    )

# filepath = os.path.join(filepath,'__init__.py')
# print(open(filepath,'r').read())
# with open(filepath,'w') as f:
#     f.write('''
# from .root import RootTables
# from .standard import StdContentIndex
# from .temp import TempIndexCellCount
# from .temp import TempParseHtml''')

p = subprocess.Popen('python manage.py makemigrations',stdout=subprocess.PIPE,shell=True,cwd='H:\data_extract')
print(p.stdout.read())
p = subprocess.Popen('python manage.py migrate',stdout=subprocess.PIPE,shell=True,cwd='H:\data_extract')
print(p.stdout.read())




