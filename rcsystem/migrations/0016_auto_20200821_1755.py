# Generated by Django 3.0.3 on 2020-08-21 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcsystem', '0015_auto_20200821_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dbbook',
            name='book_overall_favorite',
            field=models.FloatField(default=0),
        ),
    ]
