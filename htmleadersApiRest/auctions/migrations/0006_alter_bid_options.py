# Generated by Django 5.1.7 on 2025-04-04 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_bid_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bid',
            options={'ordering': ('-price', 'creation_date')},
        ),
    ]
