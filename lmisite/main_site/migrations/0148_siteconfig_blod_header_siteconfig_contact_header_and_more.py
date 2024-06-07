# Generated by Django 4.2.3 on 2023-07-07 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0147_siteconfig_contact_cta_siteconfig_contact_cta_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfig',
            name='blod_header',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='contact_header',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='portfolio_header',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='services_header',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='testimonials_header',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]