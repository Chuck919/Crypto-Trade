# Generated by Django 4.2.1 on 2023-08-11 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradebots', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='martbotstate',
            name='id',
        ),
        migrations.AlterField(
            model_name='martbotstate',
            name='bot_name',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]