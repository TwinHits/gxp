# Generated by Django 4.1 on 2022-08-04 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raids', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='raid',
            options={},
        ),
        migrations.AlterField(
            model_name='raid',
            name='id',
            field=models.UUIDField(editable=False, primary_key=True, serialize=False),
        ),
    ]
