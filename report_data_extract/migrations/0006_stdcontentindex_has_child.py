# Generated by Django 2.0.2 on 2018-04-14 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0005_auto_20180414_1054'),
    ]

    operations = [
        migrations.AddField(
            model_name='stdcontentindex',
            name='has_child',
            field=models.CharField(default='1', max_length=1, verbose_name='是否有下一级索引'),
        ),
    ]