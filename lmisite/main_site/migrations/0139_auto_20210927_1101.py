# Generated by Django 3.2 on 2021-09-27 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0138_category_draft'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfig',
            name='instagram_token',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='instagram_token_expires',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]