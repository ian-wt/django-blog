# Generated by Django 5.1.5 on 2025-01-29 19:27

import core.models.user
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='timezone',
            field=models.CharField(default='UTC', max_length=32, validators=[core.models.user.validate_timezone]),
        ),
    ]
