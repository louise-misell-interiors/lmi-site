# Generated by Django 3.2 on 2021-08-19 19:42

from django.db import migrations, models
import main_site.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0132_siteconfig_email_shop'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='reference',
            field=models.CharField(default=main_site.models.get_basket_id, max_length=64),
        ),
    ]
