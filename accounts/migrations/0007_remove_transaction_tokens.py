# Generated by Django 4.2.4 on 2023-08-28 07:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_transaction_tokens_tokens"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transaction",
            name="tokens",
        ),
    ]
