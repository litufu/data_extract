# Generated by Django 2.0.2 on 2018-04-19 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0014_auto_20180416_0821'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyList',
            fields=[
                ('code', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='公司代码')),
                ('name', models.CharField(max_length=10, verbose_name='公司名称')),
                ('area', models.CharField(default='北京', max_length=10, verbose_name='所属地区')),
                ('industry', models.CharField(max_length=10, verbose_name='所属行业')),
                ('timeToMarket', models.DateField(verbose_name='上市时间')),
            ],
            options={
                'verbose_name': '公司列表',
                'verbose_name_plural': '公司列表清单',
            },
        ),
    ]
