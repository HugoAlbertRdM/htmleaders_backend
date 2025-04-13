# Generated by Django 5.1.7 on 2025-04-02 07:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_bid', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('closing_date', models.DateTimeField()),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='auctions.auction')),
            ],
            options={
                'ordering': ('id',),
            },
        ),
    ]
