# Generated by Django 3.2 on 2021-07-09 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0120_basket_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='payment_intent_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='basket',
            name='postage_service_bins',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
