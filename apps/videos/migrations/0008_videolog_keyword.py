# Generated by Django 5.1.5 on 2025-03-18 13:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("videos", "0007_video_keyword"),
    ]

    operations = [
        migrations.AddField(
            model_name="videolog",
            name="keyword",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="videos.keywordentry",
            ),
        ),
    ]
