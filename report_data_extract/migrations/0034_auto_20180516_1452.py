# Generated by Django 2.0.2 on 2018-05-16 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0033_auto_20180516_1431'),
    ]

    operations = [
        migrations.RenameField(
            model_name='busisituatdiscussandanalysi',
            old_name='cfa_instructi',
            new_name='chang_in_cash_flow_statement',
        ),
        migrations.RenameField(
            model_name='busisituatdiscussandanalysi',
            old_name='ea_instructi',
            new_name='chang_in_expense',
        ),
        migrations.RenameField(
            model_name='busisituatdiscussandanalysi',
            old_name='ca_instructi',
            new_name='cost_analysi',
        ),
        migrations.RenameField(
            model_name='busisituatdiscussandanalysi',
            old_name='ioia_instructi',
            new_name='industri_busi_inform',
        ),
        migrations.RenameField(
            model_name='busisituatdiscussandanalysi',
            old_name='ipr_instructi',
            new_name='industry_product_region',
        ),
        migrations.RenameField(
            model_name='busisituatdiscussandanalysi',
            old_name='psi_instructi',
            new_name='product_and_sale',
        ),
        migrations.RenameField(
            model_name='busisituatdiscussandanalysi',
            old_name='la_instructi',
            new_name='restrict_asset',
        ),
        migrations.RenameField(
            model_name='busisituatdiscussandanalysi',
            old_name='mfcs_instructi',
            new_name='top_5_custom_and_supplier',
        ),
        migrations.RemoveField(
            model_name='busisituatdiscussandanalysi',
            name='al_instructi',
        ),
        migrations.AddField(
            model_name='busisituatdiscussandanalysi',
            name='balanc_sheet_chang',
            field=models.TextField(default='', verbose_name='资产负债表变动分析'),
        ),
    ]
