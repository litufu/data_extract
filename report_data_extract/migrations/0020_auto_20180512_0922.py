# Generated by Django 2.0.2 on 2018-05-12 01:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0019_comprehensnote_conting'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('natur_of_the_unit', models.CharField(choices=[('s', 'subcompani'), ('j', 'joint_ventur'), ('p', 'pool')], default='s', max_length=30, verbose_name='单位性质')),
                ('name', models.CharField(default='', max_length=150, unique=True, verbose_name='公司名称')),
            ],
        ),
        migrations.AlterField(
            model_name='compositofenterprisgroup',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.CompanyName', verbose_name='公司名称'),
        ),
        # migrations.RemoveField(
        #     model_name='compositofenterprisgroup',
        #     name='natur_of_the_unit',
        # ),
        migrations.AlterUniqueTogether(
            name='compositofenterprisgroup',
            unique_together={('stk_cd', 'acc_per', 'typ_rep', 'name')},
        ),
    ]
