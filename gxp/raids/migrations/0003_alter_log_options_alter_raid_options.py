# Generated by Django 4.1 on 2022-08-18 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raids', '0002_alter_log_options_alter_raid_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='log',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterModelOptions(
            name='raid',
            options={'ordering': ['-timestamp']},
        ),
    ]