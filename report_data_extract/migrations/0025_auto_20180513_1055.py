# Generated by Django 2.0.2 on 2018-05-13 02:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0024_auto_20180512_1047'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetHeldForSale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acc_per', models.DateField(verbose_name='会计期间')),
                ('name', models.CharField(default='', max_length=150, verbose_name='项目名称')),
                ('book_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='期末账面价值')),
                ('fair_valu', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='公允价值')),
                ('estim_dispos_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='预计处置费用')),
                ('estim_dispos_time', models.CharField(default='', max_length=150, verbose_name='预计处置时间')),
                ('stk_cd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.CompanyList', verbose_name='股票代码')),
                ('typ_rep', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.ReportType', verbose_name='报表类型')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='assetheldforsale',
            unique_together={('stk_cd', 'acc_per', 'typ_rep', 'name')},
        ),
    ]
