# Generated by Django 2.0.2 on 2018-05-12 01:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0020_auto_20180512_0922'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='compositofenterprisgroup',
            name='natur_of_the_unit',
        ),
    ]