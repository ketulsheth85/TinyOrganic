# Generated by Django 3.2 on 2022-01-12 20:38

import apps.orders.models.order
from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20220103_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalorder',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalorder',
            name='fulfillment_status',
            field=django_fsm.FSMField(choices=[('pending', 'pending'), ('partial', 'partial'), ('fulfilled', 'fulfilled'), ('cancelled', 'cancelled')], default=apps.orders.models.order.OrderFulfillmentStatusEnum['pending'], max_length=50),
        ),
        migrations.AlterField(
            model_name='order',
            name='fulfillment_status',
            field=django_fsm.FSMField(choices=[('pending', 'pending'), ('partial', 'partial'), ('fulfilled', 'fulfilled'), ('cancelled', 'cancelled')], default=apps.orders.models.order.OrderFulfillmentStatusEnum['pending'], max_length=50),
        ),
    ]
