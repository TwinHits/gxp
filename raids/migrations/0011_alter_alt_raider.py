# Generated by Django 4.1 on 2022-08-05 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('raids', '0010_alter_alt_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alt',
            name='raider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alts', to='raids.raider'),
        ),
    ]
