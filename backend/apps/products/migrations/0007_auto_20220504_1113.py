# Generated by Django 3.2 on 2022-05-04 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_auto_20220128_2332'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproduct',
            name='is_recurring',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_recurring',
            field=models.BooleanField(default=True),
        ),
    ]
