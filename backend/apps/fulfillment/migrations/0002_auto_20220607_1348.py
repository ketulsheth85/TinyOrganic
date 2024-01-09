# Generated by Django 3.2 on 2022-06-07 17:48

from django.db import migrations, models
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('fulfillment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fulfillmentcenter',
            name='location',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='fulfillmentcenterzipcode',
            name='zipcode',
            field=localflavor.us.models.USZipCodeField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='historicalfulfillmentcenter',
            name='location',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='historicalfulfillmentcenterzipcode',
            name='zipcode',
            field=localflavor.us.models.USZipCodeField(db_index=True, max_length=10),
        ),
    ]
