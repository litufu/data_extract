# Generated by Django 2.0.2 on 2018-05-24 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0058_auto_20180524_2317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='en_ab_name',
            field=models.CharField(default='', max_length=150, verbose_name='英文缩写'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='en_name',
            field=models.CharField(default='', max_length=300, verbose_name='英文名称'),
        ),
    ]
