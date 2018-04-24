# Generated by Django 2.0.2 on 2018-04-21 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0028_auto_20180421_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rdinvest',
            name='proport_of_incom',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=26, verbose_name='研发投入总额占营业收入比例'),
        ),
        migrations.AlterField(
            model_name='rdinvest',
            name='proport_of_staff',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=26, verbose_name='研发人员数量占公司总人数的比例'),
        ),
        migrations.AlterField(
            model_name='rdinvest',
            name='staff_number',
            field=models.IntegerField(default=0, verbose_name='公司研发人员的数量'),
        ),
    ]