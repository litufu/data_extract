#!/usr/bin/python
# -*- coding: utf-8 -*-

# _author : litufu
# date : 2018/5/23
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_extract.settings")
django.setup()

from django.db import transaction
import os
import re
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from django.apps import apps
from sqlalchemy import create_engine
engine = create_engine(r'sqlite:///H:\data_extract\newsdata.sqlite3')

from report_data_extract import models

def get_model_field(appname,modelname,exclude=None):
    """
    获取model的verbose_name和name的字段
    """
    modelobj = apps.get_model(appname, modelname)
    filed = modelobj._meta.fields
    fieldlist = []

    params = [f for f in filed if f.name not in exclude] if (type(exclude) is list) else [f for f in filed ]

    for i in params:
        value = ((type(i).__name__),i.name,i.verbose_name)
        fieldlist.append(value)
    return fieldlist

def get_table_name(appname):
    df = pd.read_sql('django_content_type',engine)
    df_app = df[df.app_label==appname]
    model_names = list(df_app.model)
    parts = ['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth','eleventh','twelve']
    table_parts = []
    new_model_names = []
    for model_name in model_names:
        for part in parts:
            part_name = part+'.py'
            path = os.path.join(os.path.join(os.path.join(BASE_DIR,appname),'models'),part_name)
            with open(path,'r',encoding='utf-8') as f:
                if model_name+'(commoninfo)' in f.read().lower() or (model_name+'(models.model)' in f.read().lower()):
                    table_parts.append(part)
                    new_model_names.append(model_name)
                    break
    for model_name,part in zip(new_model_names,table_parts):
        table_name = appname+model_name
        if models.TableDesc.objects.filter(table_name=table_name):
            obj = models.TableDesc.objects.get(table_name=table_name)
            obj.part = part
            obj.save()
        else:
            models.TableDesc.objects.create(
                app_label=appname,
                model_name=model_name,
                table_name=table_name,
                part=part,
            )

def get_table_fields(appname):
    tables = models.TableDesc.objects.filter(app_label=appname)
    for table in tables:
        model_name = table.model_name
        for f_type,f_name,f_verbose_name in get_model_field(appname,model_name):
            if models.FieldDesc.objects.filter(table_id=table.id,f_name=f_name):
                obj = models.FieldDesc.objects.get(table_id=table.id,f_name=f_name)
                obj.f_verbose_name = f_verbose_name
                obj.f_type = f_type
                obj.f_detail_name = f_verbose_name
                obj.save()
            else:
                models.FieldDesc.objects.create(
                    table_id=table.id,
                    f_name=f_name,
                    f_type=f_type,
                    f_verbose_name=f_verbose_name,
                    f_detail_name=f_verbose_name,
                )

def get_foreignkey(field,line):
    pattern = re.compile('^.*?{}.*?ForeignKey\((.*?),.*?$'.format(field))
    if pattern.match(line) is not None:
        return re.sub('\s+','',pattern.match(line).groups()[0])
    else:
        return None

def get_is_unique(field,line):
    pattern = re.compile('.*?{}.*?unique\s*=\s*(\S*?)'.format(field))
    if pattern.match(line):
        if pattern.match(line).groups()[0] == 'True':
            return 'True'
        else:
            return 'False'
    else:
        return 'False'

def get_unique_together(line):
    pattern = re.compile('.*?unique_together.*?\((.*?)\)')
    if pattern.match(line) is not None:
        return pattern.match(line).groups()[0]
    else:
        return None

def get_choices(field,line):
    pattern = re.compile('^.*?{}.*?choices\s*=\s*(\S*?)[,\)].*?$'.format(field))
    if pattern.match(line):
        return pattern.match(line).groups()[0]
    else:
        return None

def get_class_name(line):
    pattern = re.compile('^.*?class\s+(.*?)\(.*?\):.*?$')
    if pattern.match(line):
        return pattern.match(line).groups()[0]
    else:
        return None

def get_field_name(line):
    pattern = re.compile('^\s*(\S*?)\s*=\s*models.*?$')
    if pattern.match(line):
        return pattern.match(line).groups()[0]
    else:
        return None

def get_part_class_text(name1,name2,partname):
    '''
    获取第几部分所有类的文本，使用类名：[line,line]标示
    :param appname: report_data_extract
    :param partname: first,second,third...
    :return:
    '''
    part_name = partname + '.py'
    temp_dict = {}
    path = os.path.join(os.path.join(os.path.join(BASE_DIR, name1), name2), part_name)
    with open(path, 'r', encoding='utf-8') as f:
        temp_lines = f.readlines()
        class_name = None
        for line in temp_lines:
            if re.sub('\s+','',line) == '':
                continue
            temp_class_name = get_class_name(line)
            if temp_class_name is not None:
                class_name = temp_class_name
                temp_dict[class_name] = []

            if class_name is None:
                pass
            else:
                temp_dict[class_name].append(line)
    return temp_dict

@transaction.atomic
def get_table_field_attr():
    parts = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh',
             'twelve']
    for part in parts:
        class_text = get_part_class_text('report_data_extract','models',part)
        for class_name in class_text:
            print(class_name.lower())
            table_obj = models.TableDesc.objects.get(model_name=class_name.lower())
            for line in class_text[class_name]:
                field_name = get_field_name(line)
                unique_together = get_unique_together(line)
                if field_name is not None:
                    print(part)
                    print(field_name)
                    print(class_name)
                    field_obj = models.FieldDesc.objects.get(table_id=table_obj.id,f_name=field_name)
                    foreignkey = get_foreignkey(field_name,line)
                    is_unique = get_is_unique(field_name,line)
                    choice = get_choices(field_name,line)
                    if foreignkey is not None:
                        field_obj.foreignkey = foreignkey
                    if is_unique is not None:
                        field_obj.is_unique = is_unique
                    if choice is not None:
                        field_obj.choices = choice
                    field_obj.save()
                if unique_together is  not None:
                    table_obj.unique_together = unique_together
                    table_obj.save()

def get_handleclass_table():
    table_pattern = re.compile('^.*?models\.(\w+?)\..*?$')

    parts = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh',
             'twelve']
    for part in parts:
        print(part)
        class_text = get_part_class_text('utils', 'handleindexcontent', part)
        for class_name in class_text:
            handleindex_obj = models.IndexHandleMethod.objects.filter(handle_classname=class_name)[0]
            for line in class_text[class_name]:
                if table_pattern.match(line):
                    tablename = table_pattern.match(line).groups()[0]
                    print(tablename)
                    if models.TableDesc.objects.filter(model_name=tablename.lower()):
                        table = models.TableDesc.objects.get(model_name=tablename.lower())
                        if models.Handleclass2Table.objects.filter(handleclass_id=handleindex_obj.id,table_id=table.id):
                            pass
                        else:
                            models.Handleclass2Table.objects.create(
                                handleclass_id=handleindex_obj.id,
                                table_id=table.id,
                                table_name=tablename,
                            )



@transaction.atomic
def get_table_and_field(appname):
    models.FieldDesc.objects.all().delete()
    models.TableDesc.objects.all().delete()
    get_table_name(appname)
    get_table_fields(appname)

@transaction.atomic
def get_verbosename2field():
    objs = models.FieldDesc.objects.all()
    errors_field = []
    for obj in objs:
        if models.VerboseName2Field.objects.filter(verbose=obj.f_verbose_name):
            v2f_obj = models.VerboseName2Field.objects.get(verbose=obj.f_verbose_name)
            if v2f_obj.field ==  obj.f_name:
                pass
            else:
                errors_field.append((obj.f_verbose_name,v2f_obj.field,obj.f_name))
        else:
            models.VerboseName2Field.objects.create(
                verbose=obj.f_verbose_name,
                field=obj.f_name,
            )
    if len(errors_field) >0:
        print(errors_field)
        raise Exception





if __name__ == '__main__':
    # get_table_and_field('report_data_extract')
    # get_verbosename2field()
    get_table_field_attr()
    # get_handleclass_table()
