# Generated by Django 5.1.7 on 2025-04-04 09:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_bid_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='stock',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
