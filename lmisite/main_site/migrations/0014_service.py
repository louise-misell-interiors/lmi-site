# Generated by Django 2.0.5 on 2018-05-06 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0013_auto_20180506_1919'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('M', 'Main'), ('O', 'Other')], default='M', max_length=1)),
                ('icon', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
        ),
    ]
