# Generated by Django 4.1 on 2022-08-09 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experience', '0006_alter_experiencegain_tokens'),
    ]

    operations = [
        migrations.AddField(
            model_name='experienceevent',
            name='template',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
