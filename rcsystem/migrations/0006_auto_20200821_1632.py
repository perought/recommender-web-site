# Generated by Django 3.0.3 on 2020-08-21 13:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rcsystem', '0005_auto_20200821_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookcomment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_comments', to='rcsystem.DBBook'),
        ),
    ]
