# Generated by Django 2.0.7 on 2018-10-08 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0043_shortpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfig',
            name='homify_url',
            field=models.URLField(blank=True, default=''),
        ),
    ]