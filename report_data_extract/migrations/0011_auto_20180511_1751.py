# Generated by Django 2.0.2 on 2018-05-11 09:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0010_auto_20180511_1717'),
    ]

    operations = [
        migrations.CreateModel(
            name='MoneyLend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acc_per', models.DateField(verbose_name='会计期间')),
                ('transact_type', models.CharField(choices=[('from', 'lend_from'), ('to', 'lend_to')], default='s', max_length=30, verbose_name='交易类型')),
                ('name', models.CharField(default='', max_length=150, verbose_name='关联方')),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='拆借金额')),
                ('start_date', models.CharField(default='', max_length=150, verbose_name='起始日')),
                ('expiri_date', models.CharField(default='', max_length=150, verbose_name='到期日')),
                ('desc', models.CharField(default='', max_length=300, verbose_name='说明')),
                ('stk_cd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.CompanyList', verbose_name='股票代码')),
                ('typ_rep', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.ReportType', verbose_name='报表类型')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='moneylend',
            unique_together={('stk_cd', 'acc_per', 'typ_rep', 'transact_type', 'name')},
        ),
    ]