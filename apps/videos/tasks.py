import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from .models import VideoLog, Video, VideoFetchMethod


@shared_task(bind = True)
def process_trigger(self, keyword):

    VideoLog.objects.create(
        error = False,
        method = VideoFetchMethod.YOUTUBE,
        number_added = -12,
        keyword = keyword
    )