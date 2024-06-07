# Generated by Django 4.1.4 on 2022-12-21 16:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0143_siteconfig_blog_sidebar_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactFormQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(blank=True, default=0)),
                ('question', models.CharField(max_length=255)),
                ('required', models.BooleanField()),
                ('question_type', models.CharField(choices=[('T', 'One Line'), ('M', 'Multi-line'), ('S', 'Select')], max_length=1)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='ContactFormQuestionOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(blank=True, default=0)),
                ('option', models.CharField(max_length=255)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='main_site.contactformquestion')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]