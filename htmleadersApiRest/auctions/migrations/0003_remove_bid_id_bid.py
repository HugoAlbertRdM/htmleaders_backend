# Generated by Django 5.1.7 on 2025-04-02 07:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_bid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bid',
            name='id_bid',
        ),
    ]
