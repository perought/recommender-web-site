# Generated by Django 3.0.3 on 2020-08-31 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rcsystem', '0041_auto_20200831_2102'),
    ]

    operations = [
        migrations.AddField(
            model_name='moviedatabase',
            name='movie_index',
            field=models.IntegerField(default=-1),
        ),
    ]
