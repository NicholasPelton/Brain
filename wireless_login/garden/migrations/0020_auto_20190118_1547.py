# Generated by Django 2.1.4 on 2019-01-18 22:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('garden', '0019_auto_20190113_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outlet',
            name='uvb_end_date',
            field=models.DateField(default=datetime.date(2019, 4, 18)),
        ),
        migrations.AlterField(
            model_name='picture',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
