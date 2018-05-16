# Generated by Django 2.0.2 on 2018-05-13 05:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0026_auto_20180513_1330'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailForSaleFinanciAssetImpair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acc_per', models.DateField(verbose_name='会计期间')),
                ('name', models.CharField(default='', max_length=150, verbose_name='可供出售金融资产分类')),
                ('before', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='年初已计提减值余额')),
                ('accrual', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='本年计提')),
                ('transfer_from_other_comprehens_incom', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='其中：从其他综合收益转入')),
                ('cut_back', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='本年减少')),
                ('fair_valu_rebound', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='其中：期后公允价值回升转回')),
                ('end', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='年末已计提减值余额')),
                ('stk_cd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.CompanyList', verbose_name='股票代码')),
                ('typ_rep', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.ReportType', verbose_name='报表类型')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='availforsalefinanciassetimpair',
            unique_together={('stk_cd', 'acc_per', 'typ_rep', 'name')},
        ),
    ]
