# Generated by Django 5.1.1 on 2025-03-10 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0162_alter_siteconfig_notification_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteconfig',
            name='banner_enabled',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
