# Generated by Django 4.1 on 2022-08-09 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experience', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='experienceevent',
            name='key',
            field=models.CharField(default='KEY', max_length=100, unique=True),
            preserve_default=False,
        ),
    ]
