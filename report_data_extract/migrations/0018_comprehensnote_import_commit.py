# Generated by Django 2.0.2 on 2018-05-11 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0017_comprehensnote_relat_parti_commit'),
    ]

    operations = [
        migrations.AddField(
            model_name='comprehensnote',
            name='import_commit',
            field=models.TextField(default='', verbose_name='重要承诺事项'),
        ),
    ]
