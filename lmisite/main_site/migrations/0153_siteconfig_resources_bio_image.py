# Generated by Django 4.2.3 on 2023-09-05 13:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main_site", "0152_alter_faq_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteconfig",
            name="resources_bio_image",
            field=models.ImageField(blank=True, upload_to=""),
        ),
    ]