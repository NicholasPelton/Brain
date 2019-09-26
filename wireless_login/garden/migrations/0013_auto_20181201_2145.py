# Generated by Django 2.1.3 on 2018-12-01 21:45

import datetime
from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('garden', '0012_auto_20181129_0005'),
    ]

    operations = [
        migrations.AddField(
            model_name='outlet',
            name='pump_data',
            field=jsonfield.fields.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='outlet',
            name='uvb_end_date',
            field=models.DateField(default=datetime.date(2019, 3, 1)),
        ),
    ]