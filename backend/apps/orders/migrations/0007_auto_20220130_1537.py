# Generated by Django 3.2 on 2022-01-30 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_alter_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalorder',
            name='order_number',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='order_number',
            field=models.TextField(blank=True, null=True),
        ),
    ]