# Generated by Django 3.2 on 2022-01-22 20:52

from django.db import migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicallocation',
            name='state',
            field=localflavor.us.models.USStateField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='state',
            field=localflavor.us.models.USStateField(blank=True, max_length=2, null=True),
        ),
    ]