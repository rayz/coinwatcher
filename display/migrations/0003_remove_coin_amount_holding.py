# Generated by Django 3.0.1 on 2020-01-04 00:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("display", "0002_coin"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="coin",
            name="amount_holding",
        ),
    ]
