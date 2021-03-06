# Generated by Django 2.0.2 on 2018-05-12 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0022_auto_20180512_1003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commonbeforeandendname',
            name='subject',
            field=models.CharField(choices=[('interest_receiv', 'interest_receiv'), ('dividend_receiv', 'dividend_receiv'), ('other_receiv_natur', 'other_receiv_natur'), ('other_current_asset', 'other_current_asset'), ('engin_materi', 'engin_materi'), ('fix_asset_clean_up', 'fix_asset_clean_up'), ('unconfirm_defer_incom_tax', 'unconfirm_defer_incom_tax'), ('expir_in_the_follow_year', 'expir_in_the_follow_year'), ('other_noncurr_asset', 'other_noncurr_asset'), ('shortterm_loan', 'shortterm_loan'), ('financi_liabil_measur_at_fair_valu', 'financi_liabil_measur_at_fair_valu'), ('bill_payabl', 'bill_payabl'), ('account_payabl', 'account_payabl'), ('advanc_receipt', 'advanc_receipt'), ('tax_payabl', 'tax_payabl'), ('interest_payabl', 'interest_payabl'), ('other_payabl', 'other_payabl'), ('noncurr_liabil_due_within_one_year', 'noncurr_liabil_due_within_one_year'), ('bond_payabl', 'bond_payabl'), ('undistributed_profit', 'undistributed_profit'), ('tax_and_surcharg', 'tax_and_surcharg'), ('sale_expens', 'sale_expens'), ('manag_cost', 'manag_cost'), ('financi_expens', 'financi_expens'), ('asset_impair_loss', 'asset_impair_loss'), ('chang_in_fair_valu', 'chang_in_fair_valu'), ('invest_incom', 'invest_incom'), ('nonoper_incom', 'nonoper_incom'), ('nonoper_expens', 'nonoper_expens'), ('incom_tax_expens', 'incom_tax_expens'), ('profit_to_incometax', 'profit_to_incometax'), ('receipt_other_busi', 'receipt_other_busi'), ('payment_other_busi', 'payment_other_busi'), ('receipt_other_invest', 'receipt_other_invest'), ('payment_other_invest', 'payment_other_invest'), ('receipt_other_financ', 'receipt_other_financ'), ('payment_other_financ', 'payment_other_financ'), ('addit_materi', 'addit_materi'), ('composit_of_cash_and_cash_equival', 'composit_of_cash_and_cash_equival'), ('asset_with_limit_ownership', 'asset_with_limit_ownership'), ('govern_subsidi', 'govern_subsidi'), ('nonrecur_gain_and_loss', 'nonrecur_gain_and_loss')], default='', max_length=30, verbose_name='科目名称'),
        ),
    ]
