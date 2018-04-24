# Generated by Django 2.0.2 on 2018-04-19 02:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0015_companylist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interpret',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acc_per', models.DateField(verbose_name='会计期间')),
                ('interpret_item', models.CharField(default='', max_length=150, verbose_name='释义项')),
                ('definit', models.CharField(default='', max_length=300, verbose_name='释义内容')),
                ('stk_cd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.CompanyList', verbose_name='股票代码')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]