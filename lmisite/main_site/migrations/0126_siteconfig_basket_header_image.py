# Generated by Django 3.2 on 2021-07-25 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0125_auto_20210725_1217'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfig',
            name='basket_header_image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]
