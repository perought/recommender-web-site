# Generated by Django 3.0.3 on 2020-08-28 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rcsystem', '0032_auto_20200828_1314'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='newbooksratings',
            unique_together={('book', 'user_id')},
        ),
    ]
