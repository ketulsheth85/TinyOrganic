# Generated by Django 3.2 on 2022-04-13 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_auto_20220331_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalorder',
            name='synced_to_avalara',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='synced_to_avalara',
            field=models.BooleanField(default=False),
        ),
    ]