# Generated by Django 5.2.1 on 2025-05-23 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fuel', '0004_transaction_cost_price_per_liter_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='selling_price_per_liter',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
