# Generated by Django 2.0.5 on 2018-05-07 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0015_auto_20180506_1954'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servicesummary',
            options={'verbose_name_plural': 'Serivce Summaries'},
        ),
        migrations.AlterField(
            model_name='service',
            name='price',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
