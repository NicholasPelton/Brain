# Generated by Django 2.1.4 on 2019-01-03 00:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('garden', '0017_picture_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outlet',
            name='uvb_end_date',
            field=models.DateField(default=datetime.date(2019, 4, 2)),
        ),
        migrations.AlterField(
            model_name='picture',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
