# Generated by Django 2.2.1 on 2019-05-27 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0048_designinsiderpost_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='designinsiderpost',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='facebook_token',
            field=models.TextField(blank=True, null=True),
        ),
    ]
