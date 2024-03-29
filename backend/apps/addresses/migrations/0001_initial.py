# Generated by Django 3.2 on 2021-12-12 04:30

import dirtyfields.dirtyfields
from django.db import migrations, models
import localflavor.us.models
import simple_history.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalLocation',
            fields=[
                ('modified_at', models.DateTimeField(auto_created=True, blank=True, db_index=True, editable=False, verbose_name='last modified at')),
                ('created_at', models.DateTimeField(auto_created=True, blank=True, db_index=True, editable=False)),
                ('id', models.UUIDField(auto_created=True, db_index=True, default=uuid.uuid4, editable=False, verbose_name='ID')),
                ('street_address', models.TextField(default='')),
                ('city', models.TextField()),
                ('state', localflavor.us.models.USStateField(max_length=2)),
                ('zipcode', localflavor.us.models.USZipCodeField(max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical location',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('modified_at', models.DateTimeField(auto_created=True, auto_now=True, db_index=True, verbose_name='last modified at')),
                ('created_at', models.DateTimeField(auto_created=True, auto_now_add=True, db_index=True)),
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_address', models.TextField(default='')),
                ('city', models.TextField()),
                ('state', localflavor.us.models.USStateField(max_length=2)),
                ('zipcode', localflavor.us.models.USZipCodeField(max_length=10)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
    ]
