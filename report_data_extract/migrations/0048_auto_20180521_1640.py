# Generated by Django 2.0.2 on 2018-05-21 08:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0047_auto_20180521_1636'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='changinshareholdandremuner',
            name='end_date_in_sharehold_com',
        ),
        migrations.RemoveField(
            model_name='changinshareholdandremuner',
            name='job_titl_chang_reason',
        ),
        migrations.RemoveField(
            model_name='changinshareholdandremuner',
            name='job_titl_in_sharehold_com',
        ),
        migrations.RemoveField(
            model_name='changinshareholdandremuner',
            name='name_of_sharehold',
        ),
        migrations.RemoveField(
            model_name='changinshareholdandremuner',
            name='start_date_in_sharehold_com',
        ),
    ]
