# Generated by Django 2.0.2 on 2018-04-16 00:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report_data_extract', '0013_auto_20180415_1146'),
    ]

    operations = [
        migrations.CreateModel(
            name='RootTableDesc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tablename', models.CharField(blank=True, max_length=100, verbose_name='表英文名')),
                ('table_cn_name', models.CharField(blank=True, max_length=100, verbose_name='表中文名')),
                ('class_str', models.CharField(blank=True, max_length=200, verbose_name='表文件描述')),
                ('functions', models.TextField(blank=True, verbose_name='表内函数')),
                ('meta', models.TextField(blank=True, verbose_name='表相关信息')),
            ],
        ),
        migrations.CreateModel(
            name='StdCompareIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('compare_name', models.CharField(max_length=100, verbose_name='索引名称')),
                ('index_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.StdContentIndex')),
            ],
        ),
        migrations.RemoveField(
            model_name='roottables',
            name='class_str',
        ),
        migrations.RemoveField(
            model_name='roottables',
            name='functions',
        ),
        migrations.RemoveField(
            model_name='roottables',
            name='meta',
        ),
        migrations.AlterField(
            model_name='roottables',
            name='tableclass',
            field=models.CharField(blank=True, choices=[('temp', 'temp'), ('business', 'business')], max_length=10, verbose_name='表类别'),
        ),
        migrations.AlterField(
            model_name='roottables',
            name='tablename',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_data_extract.RootTableDesc'),
        ),
        migrations.AlterUniqueTogether(
            name='stdcompareindex',
            unique_together={('compare_name', 'index_name')},
        ),
    ]