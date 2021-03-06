# Generated by Django 2.0.2 on 2018-05-23 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0048_auto_20180521_1640'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldDesc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f_name', models.CharField(default='', max_length=150, verbose_name='字段名称')),
                ('f_type', models.CharField(default='', max_length=150, verbose_name='字段类型')),
                ('f_verbose_name', models.CharField(default='', max_length=150, verbose_name='中文名称')),
                ('f_detail_name', models.CharField(default='', max_length=200, verbose_name='详细中文名称')),
                ('f_desc', models.CharField(blank=True, default='', max_length=200, verbose_name='字段描述')),
            ],
        ),
        migrations.CreateModel(
            name='TableDesc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_label', models.CharField(default='', max_length=150, verbose_name='app名称')),
                ('model_name', models.CharField(default='', max_length=150, verbose_name='模型名称')),
                ('table_name', models.CharField(default='', max_length=150, unique=True, verbose_name='数据库表名')),
                ('part', models.CharField(default='', max_length=150, verbose_name='所述部分')),
                ('table_desc', models.CharField(blank=True, default='', max_length=200, verbose_name='表文件描述')),
            ],
        ),
        migrations.AddField(
            model_name='fielddesc',
            name='table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.TableDesc', verbose_name='表名'),
        ),
        migrations.AlterUniqueTogether(
            name='fielddesc',
            unique_together={('table', 'f_name')},
        ),
    ]
