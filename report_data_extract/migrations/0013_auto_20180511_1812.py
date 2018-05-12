# Generated by Django 2.0.2 on 2018-05-11 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0012_auto_20180511_1800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasandsale',
            name='transact_type',
            field=models.CharField(choices=[('s', 'sale'), ('p', 'purchase'), ('atdr', 'asset_transfer_debt_restructur')], default='s', max_length=30, verbose_name='交易类型'),
        ),
    ]