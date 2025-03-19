import logging
from datetime import timedelta, datetime

from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from core.youtube_api import YouTubeAPI

from .models import VideoLog, Video, VideoFetchMethod, KeyWordEntry
import logging

logger = logging.getLogger("tasks_log")

@shared_task(bind = True)
def process_trigger(self, keyword):
    youtube_api = YouTubeAPI()
    search_query = keyword
    keyword_obj = KeyWordEntry.objects.get(keyword=keyword)
    max_results = 50    

    method, response = youtube_api.fetch_videos(search_query, max_results)

    if method == VideoFetchMethod.INVIDIOUS:
        logger.info("IN VideoFetchMethod.INVIDIOUS")
        for r in response:
            videoId = ""
            title = ""
            description = ""
            author = ""
            publish = timezone.now()
            thumbnail = "https://placehold.co/600x400"

            try:
                videoId = r["videoId"]
                title = r["title"] 
                description = r["description"]
                author = r["author"]
                publish = datetime.fromtimestamp(r["published"])
                thumbnail = r["videoThumbnails"][0]["url"]

            except KeyError:
                logger.critical(f"KeyError: {r}")

            logger.info(f'{videoId} - {r["title"]}')
            video, created = Video.objects.update_or_create(
                video_id=videoId,  # Unique identifier for the video
                defaults={
                    'title': title,
                    'description': description,
                    'published_at': publish,
                    'channel_title': author,
                    'thumbnail': thumbnail,
                    'keyword': keyword_obj,
                    'method': method,
                }
            )
    else:
        logger.info("IN VideoFetchMethod.YOUTUBE")
        for r in response["items"]:
            logger.info(f"{r['id']['videoId']} - {r['snippet']['title']}")
            video, created = Video.objects.update_or_create(
                video_id=r['id']['videoId'],  # Unique identifier for the video
                defaults={
                    'title': r['snippet']['title'],
                    'description': r['snippet'].get('description', ''),
                    'published_at': r['snippet']['publishedAt'],
                    'channel_title': r['snippet']['channelTitle'],
                    'thumbnail': r['snippet']['thumbnails']['default']['url'],
                    'keyword': keyword_obj,
                    'method': method,
                }
            )

    VideoLog.objects.create(
        error = False,
        method = method,
        number_added = len(response),
        keyword = keyword_obj
    )
