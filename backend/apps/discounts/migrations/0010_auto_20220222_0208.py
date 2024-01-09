# Generated by Django 3.2 on 2022-02-22 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discounts', '0010_alter_customerdiscount_customer_child'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerdiscount',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customerdiscount',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalcustomerdiscount',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalcustomerdiscount',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
