# Generated by Django 4.1 on 2022-08-18 02:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('raiders', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('logsCode', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('timestamp', models.IntegerField()),
                ('zone', models.CharField(default='', max_length=255, null=True)),
                ('raidHelperEventId', models.CharField(default='', max_length=255, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'gxp_logs',
            },
        ),
        migrations.CreateModel(
            name='Raid',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.IntegerField()),
                ('zone', models.CharField(default='', max_length=255, null=True)),
                ('optional', models.BooleanField(default=True)),
                ('log', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='raid', to='raids.log')),
                ('raiders', models.ManyToManyField(db_table='gxp_raids_raiders', related_name='raids', to='raiders.raider')),
            ],
            options={
                'db_table': 'gxp_raids',
            },
        ),
    ]
