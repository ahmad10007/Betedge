# Generated by Django 4.2.4 on 2023-08-28 07:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app_control", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="products",
            name="tokens",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
