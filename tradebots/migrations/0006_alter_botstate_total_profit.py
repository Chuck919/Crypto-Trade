# Generated by Django 4.2.2 on 2023-08-08 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradebots', '0005_botstate_delete_tradingorders_martbotstate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='botstate',
            name='total_profit',
            field=models.FloatField(default=0.0),
        ),
    ]
