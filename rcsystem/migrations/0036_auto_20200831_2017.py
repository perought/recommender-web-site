# Generated by Django 3.0.3 on 2020-08-31 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcsystem', '0035_auto_20200831_2016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moviedatabase',
            name='runtime',
            field=models.FloatField(),
        ),
    ]
