# Generated by Django 3.2 on 2022-01-28 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_auto_20220126_2009'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproduct',
            name='from_production_shopify_store',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='from_production_shopify_store',
            field=models.BooleanField(default=False),
        ),
    ]
