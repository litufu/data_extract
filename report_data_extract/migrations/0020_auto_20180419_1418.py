# Generated by Django 2.0.2 on 2018-04-19 06:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0019_auto_20180419_1147'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='indexhandlemethod',
            unique_together={('indexno', 'handle_classname')},
        ),
        migrations.AlterUniqueTogether(
            name='storagregistrform',
            unique_together={('stk_cd', 'acc_per', 'table')},
        ),
    ]