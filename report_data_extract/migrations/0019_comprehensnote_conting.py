# Generated by Django 2.0.2 on 2018-05-11 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0018_comprehensnote_import_commit'),
    ]

    operations = [
        migrations.AddField(
            model_name='comprehensnote',
            name='conting',
            field=models.TextField(default='', verbose_name='或有事项'),
        ),
    ]
