# Generated by Django 3.2 on 2022-03-29 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0018_auto_20220329_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalorder',
            name='refund_reason',
            field=models.TextField(blank=True, choices=[('', ''), ('Order Cancellation', 'Order Cancellation'), ('Order Issue', 'Order Issue')], default=''),
        ),
        migrations.AlterField(
            model_name='order',
            name='refund_reason',
            field=models.TextField(blank=True, choices=[('', ''), ('Order Cancellation', 'Order Cancellation'), ('Order Issue', 'Order Issue')], default=''),
        ),
    ]