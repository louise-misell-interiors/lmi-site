# Generated by Django 3.2 on 2021-09-13 09:43

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0136_siteconfig_contact_submitted_texts'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='shop_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='shop_header_image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='shop_text',
            field=ckeditor.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='shop_title',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
