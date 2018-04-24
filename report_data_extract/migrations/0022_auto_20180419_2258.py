# Generated by Django 2.0.2 on 2018-04-19 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0021_auto_20180419_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='companiprofil',
            name='account_firm_name',
            field=models.CharField(default='', max_length=150, verbose_name='会计师事务所名称'),
        ),
        migrations.AddField(
            model_name='companiprofil',
            name='account_offic_addres',
            field=models.CharField(default='', max_length=150, verbose_name='会计师事务所办公地址'),
        ),
        migrations.AddField(
            model_name='companiprofil',
            name='chang_in_control_sha',
            field=models.CharField(default='', max_length=400, verbose_name='控股股东变更情况'),
        ),
        migrations.AddField(
            model_name='companiprofil',
            name='chang_in_main_busi',
            field=models.CharField(default='', max_length=400, verbose_name='主营业务变更情况'),
        ),
        migrations.AddField(
            model_name='companiprofil',
            name='continu_supervis_per',
            field=models.CharField(default='', max_length=10, verbose_name='持续督导的期间'),
        ),
        migrations.AddField(
            model_name='companiprofil',
            name='organ_code',
            field=models.CharField(default='', max_length=100, verbose_name='组织机构代码'),
        ),
        migrations.AddField(
            model_name='companiprofil',
            name='sign_accountant_nam',
            field=models.CharField(default='', max_length=100, verbose_name='签字注册会计师'),
        ),
        migrations.AddField(
            model_name='companiprofil',
            name='sponsor_addres',
            field=models.CharField(default='', max_length=100, verbose_name='保荐机构地址'),
        ),
        migrations.AddField(
            model_name='companiprofil',
            name='sponsor_name',
            field=models.CharField(default='', max_length=100, verbose_name='保荐机构名称'),
        ),
        migrations.AddField(
            model_name='companiprofil',
            name='sponsor_repr',
            field=models.CharField(default='', max_length=100, verbose_name='保荐代表人'),
        ),
    ]