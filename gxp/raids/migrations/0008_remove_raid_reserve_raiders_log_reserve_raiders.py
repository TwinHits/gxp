# Generated by Django 4.1 on 2023-02-23 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raiders", "0011_alter_specialistrole_raider"),
        ("raids", "0007_raid_reserve_raiders"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="raid",
            name="reserve_raiders",
        ),
        migrations.AddField(
            model_name="log",
            name="reserve_raiders",
            field=models.ManyToManyField(
                db_table="gxp_logs_reserve_raiders",
                related_name="reserve_logs",
                to="raiders.raider",
            ),
        ),
    ]
