# Generated by Django 3.0.3 on 2020-08-31 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcsystem', '0036_auto_20200831_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moviedatabase',
            name='runtime',
            field=models.CharField(max_length=250),
        ),
    ]
