# Generated by Django 4.1 on 2022-08-09 23:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experience', '0007_experienceevent_template'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='experiencegain',
            options={'ordering': ['-timestamp']},
        ),
    ]
