# Generated by Django 4.1 on 2022-08-21 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raids", "0005_remove_raid_optional_log_optional"),
    ]

    operations = [
        migrations.AddField(
            model_name="raid",
            name="optional",
            field=models.BooleanField(default=True),
        ),
    ]
