# Generated by Django 3.2 on 2022-03-06 22:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('discounts', '0015_auto_20220306_2005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='referrer',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='referrer', to=settings.AUTH_USER_MODEL),
        ),
    ]
