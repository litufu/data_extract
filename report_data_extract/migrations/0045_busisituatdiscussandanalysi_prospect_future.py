# Generated by Django 2.0.2 on 2018-04-22 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0044_auto_20180422_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='busisituatdiscussandanalysi',
            name='prospect_future',
            field=models.TextField(default='', verbose_name='公司未来发展的展望'),
        ),
    ]