from django.db import models

# Create your models here.
class Video(models.Model):
    """Model to store YouTube video data."""
    id = models.CharField(primary_key=True, max_length=20)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    published_at = models.DateTimeField(db_index=True)
    channel_id = models.CharField(max_length=100)
    channel_title = models.CharField(max_length=255)
    thumbnail_default = models.URLField()
    thumbnail_medium = models.URLField()
    thumbnail_high = models.URLField()
    tags = models.JSONField(default=list, blank=True)
    view_count = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['channel_id']),
        ]

    def __str__(self):
        return self.title