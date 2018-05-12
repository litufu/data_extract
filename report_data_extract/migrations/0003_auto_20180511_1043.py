# Generated by Django 2.0.2 on 2018-05-11 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0002_remove_majornonwhollyownsubsidiaryfinanciinform_liquid_asset'),
    ]

    operations = [
        migrations.AddField(
            model_name='majornonwhollyownsubsidiaryfinanciinform',
            name='company_type',
            field=models.CharField(choices=[('s', 'subsidiari'), ('j', 'joint_ventur'), ('p', 'pool')], default='s', max_length=30, verbose_name='公司类型'),
        ),
        migrations.AlterField(
            model_name='majornonwhollyownsubsidiaryfinanciinform',
            name='subcompani_name',
            field=models.CharField(default='', max_length=150, verbose_name='公司名称'),
        ),
        migrations.AlterUniqueTogether(
            name='majornonwhollyownsubsidiaryfinanciinform',
            unique_together={('stk_cd', 'acc_per', 'typ_rep', 'company_type', 'before_end', 'subcompani_name', 'subject')},
        ),
    ]