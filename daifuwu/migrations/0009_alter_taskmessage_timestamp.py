# Generated by Django 5.0 on 2023-12-21 02:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("daifuwu", "0008_alter_taskmessage_sender"),
    ]

    operations = [
        migrations.AlterField(
            model_name="taskmessage",
            name="timestamp",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
