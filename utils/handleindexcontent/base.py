# _author : litufu
# date : 2018/5/24
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()
from django.db import transaction
import pandas as pd
import re
from report_data_extract import models
from utils.mytools import cnToEn,comput_no,toFiledname
from utils.detectTable import detect_columns,detect_indexes
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class HandleIndexContent(object):

    def __init__(self,stk_cd_id,acc_per,indexno, indexcontent):
        self.indexno = indexno
        self.indexcontent = indexcontent
        self.stk_cd_id = stk_cd_id
        self.acc_per = acc_per

    def check(self):
        '''
        检查表是否正确
        :return:
        '''
        try:
            self.recognize()
            self.converse()
            self.logic()
            self.save()
        except Exception as e:
            self.error_info()
            raise Exception

    def recognize(self):
        '''
        识别表
        :return:
        '''
        raise Exception


    def converse(self):
        '''
        转化表
        :return:
        '''
        raise Exception

    def logic(self):
        '''
        表逻辑检验
        :return:
        '''
        raise Exception

    def save(self):
        '''
        存储表
        :return:
        '''
        raise Exception


    def error_info(self):
        print("%s.%s ******"%(self.__class__.__name__[1:], self.indexno))

def registr(no,name):
    '''
    登记索引及对应的处理函数名称
    :param no: 索引编号
    :param name: 处理函数
    :return:
    '''

    index_id = models.StdContentIndex.objects.get(no=no).id
    if models.IndexHandleMethod.objects.filter(indexno_id=index_id):
        obj = models.IndexHandleMethod.objects.get(indexno_id=index_id)
        obj.handle_classname = name
        obj.save()
    else:
        models.IndexHandleMethod.objects.create(indexno_id=index_id,handle_classname=name)

def registr_table(tablename,table_cn_name):
    if models.StandardTables.objects.filter(tablename=tablename):
        pass
    else:
        models.StandardTables.objects.create(tablename=tablename,table_cn_name=table_cn_name)

def save_subject(tablename):
    field_objs =models.FieldDesc.objects.filter(table__model_name=tablename).filter(f_type='DecimalField')
    names = [(field_obj.f_verbose_name,cnToEn(field_obj.f_verbose_name),field_obj.f_name)for field_obj in field_objs]
    exist_nos = [no_obj.no for no_obj in models.Subject.objects.filter(fatherno='',level=1)]
    selfnos,nos = comput_no(exist_nos,1,names,fatherno='',num_len=10)
    for key,(cn_name,en_name,en_ab_name) in enumerate(names):
        if models.Subject.objects.filter(cn_name=cn_name):
            obj = models.Subject.objects.filter(cn_name=cn_name,fatherno='',level=1)
            obj.selfno=selfnos[key]
            obj.no=nos[key]
        else:
            models.Subject.objects.create(
                cn_name=cn_name,
                en_name=en_name,
                en_ab_name=en_ab_name,
                level='1',
                fatherno='',
                selfno=selfnos[key],
                no=nos[key]
            )

def get_subject_obj(cn_name,father_subject=None):
    if isinstance(cn_name,str):
        names = [cn_name]
    else:
        raise Exception

    if models.Subject.objects.filter(cn_name=cn_name):
        subject_name = models.Subject.objects.get(cn_name=cn_name)
    else:
        if father_subject is not None:
            fatherno = models.Subject.objects.get(cn_name=father_subject).fatherno
            father_level = models.Subject.objects.get(cn_name=father_subject).level
        else:
            fatherno = ''
            father_level = 0
        exist_nos = [no_obj.no for no_obj in models.Subject.objects.filter(fatherno=fatherno, level=father_level + 1)]
        selfnos, nos = comput_no(exist_nos, 1, names, fatherno=fatherno, num_len=10)
        subject_name = models.Subject.objects.create(
                cn_name=cn_name,
                en_name=cnToEn(cn_name),
                en_ab_name=toFiledname(cnToEn(cn_name)),
                level=father_level+1,
                fatherno=fatherno,
                selfno=selfnos[0],
                no=nos[0]
            )
    return subject_name

def save_first_level_subject():
    tables = ['balancesheet', 'incomestatement', 'cashflow']
    for table in tables:
        save_subject(table)

def save_table_attr(table, indexno):
    columns = detect_columns(table)
    if columns is None:
        columns = ''
    indexes = detect_indexes(table)
    if indexes is None:
        indexes = ''
    obj = models.StdContentIndex.objects.get(no=indexno)
    if models.TableAttr.objects.filter(indexno_id=obj.id, columns=columns, indexes=indexes):
        pass
    else:
        models.TableAttr.objects.create(
            indexno_id=obj.id,
            columns=columns,
            indexes=indexes,
        )

def get_modelname(indexno):
    handleclassname_id = models.IndexHandleMethod.objects.get(indexno=indexno).id
    modelname = models.Handleclass2Table.objects.filter(handleclass_id=handleclassname_id)
    if len(modelname) == 1:
        return modelname

def create_and_update(model_name,**kwargs):
    model = getattr(models,model_name)
    table = models.TableDesc.objects.get(model_name=model_name.lower())
    unique_together_fields = re.split(',',table.unique_together)
    unique_together_fields = [re.sub('[\'"\s]*','',i) for i in unique_together_fields ]
    unique_together_fields = [i for i in unique_together_fields if i != '' ]

    table_fileds = models.FieldDesc.objects.filter(table_id=table.id)
    fileds_names = [table_filed.f_name for table_filed in table_fileds]
    fileds_types = [table_filed.f_type for table_filed in table_fileds]
    fileds_foreignkeys = [table_filed.foreignkey for table_filed in table_fileds]
    fileds_choices = [table_filed.choices for table_filed in table_fileds]

    new_unique_together_fields = []
    new_fileds_names = []
    for field in fileds_names:
        if fileds_types[fileds_names.index(field)] == 'ForeignKey':
            field = field+'_id'
            new_fileds_names.append(field)
        else:
            new_fileds_names.append(field)

    for field in unique_together_fields:
        if fileds_types[fileds_names.index(field)] == 'ForeignKey':
            field = field+'_id'
            new_unique_together_fields.append(field)
        else:
            new_unique_together_fields.append(field)
    no_unique_fields_names = list(set(new_fileds_names).difference(new_unique_together_fields))
    no_unique_fields_names.remove('id')
    unique_together_fields_dict = {field:kwargs[field] for field in new_unique_together_fields if field in kwargs}
    new_fileds_names.remove('id')
    all_fields_dict = {field:kwargs[field] for field in new_fileds_names if field in kwargs}
    if model.objects.filter(**unique_together_fields_dict):
        if len(model.objects.filter(**unique_together_fields_dict))==1:
            obj = model.objects.get(**unique_together_fields_dict)
        else:
            obj = model.objects.filter(**unique_together_fields_dict)[0]
        if len(no_unique_fields_names)>0:
            for field in no_unique_fields_names:
                if field in kwargs:
                    setattr(obj, field, kwargs[field])
                    obj.save()
        else:
            pass

    else:
        model.objects.create(**all_fields_dict)



