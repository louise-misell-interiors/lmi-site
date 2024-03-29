# Generated by Django 3.2 on 2021-08-19 20:11

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0133_basket_reference'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfig',
            name='banner_enabled',
            field=models.BooleanField(blank=True, default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='banner_text',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
