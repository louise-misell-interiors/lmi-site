# Generated by Django 3.2 on 2021-08-03 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0128_auto_20210801_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfig',
            name='shop_terms_and_conditions',
            field=models.FileField(blank=True, upload_to=''),
        ),
    ]