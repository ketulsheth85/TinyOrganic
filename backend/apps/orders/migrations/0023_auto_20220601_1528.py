# Generated by Django 3.2 on 2022-06-01 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_order_tax_sync'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalorder',
            name='synced_to_yotpo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='synced_to_yotpo',
            field=models.BooleanField(default=False),
        ),
    ]
