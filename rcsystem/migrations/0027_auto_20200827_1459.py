# Generated by Django 3.0.3 on 2020-08-27 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rcsystem', '0026_auto_20200827_1329'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='newbooksratings',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='newbooksratings',
            name='book_id',
        ),
        migrations.DeleteModel(
            name='NewBooks',
        ),
        migrations.DeleteModel(
            name='NewBooksRatings',
        ),
    ]
