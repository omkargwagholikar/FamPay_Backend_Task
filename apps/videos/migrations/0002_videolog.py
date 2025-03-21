# Generated by Django 5.1.5 on 2025-03-18 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("videos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="VideoLog",
            fields=[
                (
                    "id",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("error", models.BooleanField(default=False)),
                (
                    "method",
                    models.CharField(
                        choices=[("youtube", "YOUTUBE"), ("invidious", "INVIDIOUS")],
                        default="youtube",
                        max_length=20,
                    ),
                ),
                ("number_added", models.IntegerField(default=0)),
                ("keyword", models.TextField(default=" -- no name provided --")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
