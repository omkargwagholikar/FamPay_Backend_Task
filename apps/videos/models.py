from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask

class VideoFetchMethod(models.TextChoices):
    YOUTUBE = "youtube", "YOUTUBE"
    INVIDIOUS = "invidious", "INVIDIOUS"



class KeyWordEntry(models.Model):
    keyword = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.keyword
    
@receiver(pre_delete, sender=KeyWordEntry)
def delete_related_data(sender, instance, **kwargs):
    # Delete PeriodicTask when the keyword is deleted
    PeriodicTask.objects.filter(name=instance.keyword).delete()

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

    keyword = models.ForeignKey("KeyWordEntry", on_delete=models.CASCADE, null=True, blank=True)
    
    method = models.CharField(
        max_length=20,
        choices=VideoFetchMethod.choices,
        default=VideoFetchMethod.YOUTUBE,
    )

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['channel_id']),
        ]

    def __str__(self):
        return self.title

class VideoLog(models.Model):
    id = models.AutoField(primary_key=True)
    error = models.BooleanField(default=False)
    method = models.CharField(
        max_length=20,
        choices=VideoFetchMethod.choices,
        default=VideoFetchMethod.YOUTUBE,
    )
    number_added = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    keyword = models.ForeignKey("KeyWordEntry", on_delete=models.CASCADE, null=True, blank=True)
    

    def __str__(self) -> str:
        return self.keyword + " - "