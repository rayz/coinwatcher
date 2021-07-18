# Generated by Django 3.0.1 on 2020-02-22 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("display", "0005_coin_owner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coin",
            name="amount_holding",
            field=models.DecimalField(
                blank=True, decimal_places=10, default=0, max_digits=20
            ),
        ),
    ]
