# Generated by Django 4.1 on 2023-08-15 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raids", "0008_remove_raid_reserve_raiders_log_reserve_raiders"),
    ]

    operations = [
        migrations.AddField(
            model_name="log",
            name="split_run",
            field=models.BooleanField(default=False),
        ),
    ]