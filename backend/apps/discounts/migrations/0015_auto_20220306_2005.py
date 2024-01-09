# Generated by Django 3.2 on 2022-03-06 20:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('discounts', '0014_merge_20220223_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='discount',
            name='referrer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='referrer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicaldiscount',
            name='referrer',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
