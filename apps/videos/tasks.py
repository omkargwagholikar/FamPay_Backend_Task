import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import VideoLog, Video, VideoFetchMethod


@shared_task(bind = True)
def process_trigger(self):
    VideoLog.objects.create(
        error = False,
        method = VideoFetchMethod.YOUTUBE,
        number_added = -12,
        keyword = "Some value"
    )
    for i in range(10):
        print(i)