# Generated by Django 5.0 on 2023-12-20 09:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("daifuwu", "0005_task_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="last_chat_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
