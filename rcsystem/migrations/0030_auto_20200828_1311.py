# Generated by Django 3.0.3 on 2020-08-28 10:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rcsystem', '0029_auto_20200828_1241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newbooksratings',
            name='book_id',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='rcsystem.NewBooks'),
        ),
    ]
