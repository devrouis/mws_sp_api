# Generated by Django 3.0.7 on 2020-07-29 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20200729_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='paid',
            field=models.BooleanField(default=True),
        ),
    ]