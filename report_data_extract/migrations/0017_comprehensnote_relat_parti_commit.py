# Generated by Django 2.0.2 on 2018-05-11 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0016_auto_20180511_2134'),
    ]

    operations = [
        migrations.AddField(
            model_name='comprehensnote',
            name='relat_parti_commit',
            field=models.TextField(default='', verbose_name='关联方承诺'),
        ),
    ]