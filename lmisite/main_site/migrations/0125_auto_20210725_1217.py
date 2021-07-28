# Generated by Django 3.2 on 2021-07-25 12:17

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0124_basket_rm_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='extended_description',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='basket',
            name='rm_order_id',
            field=models.JSONField(blank=True, max_length=255, null=True, verbose_name='Royal Mail order ID'),
        ),
    ]