# Generated by Django 3.2 on 2022-01-29 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0005_auto_20220104_2116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerchild',
            name='sex',
            field=models.TextField(blank=True, choices=[('male', 'male'), ('female', 'female'), ('none', 'none')], null=True),
        ),
        migrations.AlterField(
            model_name='historicalcustomerchild',
            name='sex',
            field=models.TextField(blank=True, choices=[('male', 'male'), ('female', 'female'), ('none', 'none')], null=True),
        ),
    ]
