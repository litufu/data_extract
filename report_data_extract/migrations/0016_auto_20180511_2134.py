# Generated by Django 2.0.2 on 2018-05-11 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0015_comprehensnote_other_relat_transact'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelatReceivPayabl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acc_per', models.DateField(verbose_name='会计期间')),
                ('before_end', models.CharField(choices=[('b', 'before'), ('e', 'end')], default='e', max_length=30, verbose_name='期初期末')),
                ('natur_of_payment', models.CharField(choices=[('r', 'receiv'), ('p', 'payabl')], default='s', max_length=30, verbose_name='款项性质')),
                ('name', models.CharField(default='', max_length=150, verbose_name='科目名称')),
                ('relat_parti_name', models.CharField(default='', max_length=150, verbose_name='关联方名称')),
                ('book_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='账面余额')),
                ('bad_debt_prepar', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='坏账准备')),
                ('stk_cd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.CompanyList', verbose_name='股票代码')),
                ('typ_rep', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.ReportType', verbose_name='报表类型')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='relatreceivpayabl',
            unique_together={('stk_cd', 'acc_per', 'typ_rep', 'before_end', 'name', 'natur_of_payment', 'name', 'relat_parti_name')},
        ),
    ]