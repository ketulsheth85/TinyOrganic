# Generated by Django 3.2 on 2022-01-29 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_auto_20220111_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpaymentmethod',
            name='is_valid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='is_valid',
            field=models.BooleanField(default=False),
        ),
    ]
