# Generated by Django 4.2.2 on 2023-07-25 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradebots', '0003_cryptobots'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cryptobots',
            name='bot_instance_json',
        ),
        migrations.AddField(
            model_name='cryptobots',
            name='bot_instance',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
