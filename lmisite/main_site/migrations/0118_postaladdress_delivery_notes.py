# Generated by Django 3.2 on 2021-07-09 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0117_product_delivery_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='postaladdress',
            name='delivery_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
