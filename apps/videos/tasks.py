import logging
from datetime import timedelta, datetime

from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from core.youtube_api import YouTubeAPI

from .models import VideoLog, Video, VideoFetchMethod, KeyWordEntry

@shared_task(bind = True)
def process_trigger(self, keyword):
    youtube_api = YouTubeAPI()
    search_query = keyword
    keyword_obj = KeyWordEntry.objects.get(keyword=keyword)
    max_results = 50    

    method, response = youtube_api.fetch_videos(search_query, max_results)

    if method == VideoFetchMethod.INVIDIOUS:
        for r in response:
            print(r)
            video, created = Video.objects.update_or_create(
                video_id=r["videoId"],  # Unique identifier for the video
                defaults={
                    'title': r["title"],
                    'description': r["description"],
                    'published_at': datetime.fromtimestamp(r["published"]),
                    'channel_title': r["author"],
                    'thumbnail': r["videoThumbnails"][0]["url"],
                    'keyword': keyword_obj
                }
            )

    else:
        pass
    print(response)

    VideoLog.objects.create(
        error = False,
        method = VideoFetchMethod.YOUTUBE,
        number_added = len(response),
        keyword = keyword_obj
    )
