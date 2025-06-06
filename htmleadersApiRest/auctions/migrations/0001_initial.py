# Generated by Django 5.1.7 on 2025-04-01 09:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('rating', models.DecimalField(decimal_places=2, max_digits=3)),
                ('stock', models.IntegerField()),
                ('brand', models.CharField(max_length=100)),
                ('thumbnail', models.URLField()),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('closing_date', models.DateTimeField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auctions', to='auctions.category')),
            ],
            options={
                'ordering': ('id',),
            },
        ),
    ]
