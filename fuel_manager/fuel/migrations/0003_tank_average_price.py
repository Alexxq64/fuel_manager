# Generated by Django 5.2.1 on 2025-05-23 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fuel', '0002_client_transaction_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='tank',
            name='average_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
