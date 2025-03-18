# Generated by Django 4.2.10 on 2025-03-18 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Video",
            fields=[
                (
                    "id",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("published_at", models.DateTimeField(db_index=True)),
                ("channel_id", models.CharField(max_length=100)),
                ("channel_title", models.CharField(max_length=255)),
                ("thumbnail_default", models.URLField()),
                ("thumbnail_medium", models.URLField()),
                ("thumbnail_high", models.URLField()),
                ("tags", models.JSONField(blank=True, default=list)),
                ("view_count", models.BigIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-published_at"],
                "indexes": [
                    models.Index(
                        fields=["-published_at"], name="videos_vide_publish_c5c637_idx"
                    ),
                    models.Index(
                        fields=["channel_id"], name="videos_vide_channel_918466_idx"
                    ),
                ],
            },
        ),
    ]
