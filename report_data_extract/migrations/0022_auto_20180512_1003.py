# Generated by Django 2.0.2 on 2018-05-12 02:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0021_remove_compositofenterprisgroup_natur_of_the_unit'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestInSubsidiari',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acc_per', models.DateField(verbose_name='会计期间')),
                ('before', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='期初余额')),
                ('increase', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='本期增加')),
                ('cut_back', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='本期减少')),
                ('end', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='期末余额')),
                ('impair', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='本期计提减值准备')),
                ('impair_balanc', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='减值准备期末余额')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.CompanyName', verbose_name='公司名称')),
                ('stk_cd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.CompanyList', verbose_name='股票代码')),
                ('typ_rep', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.ReportType', verbose_name='报表类型')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='investinsubsidiari',
            unique_together={('stk_cd', 'acc_per', 'typ_rep', 'name')},
        ),
    ]
