from django.utils import timezone
from django.http import JsonResponse
from rest_framework.views import APIView, status
from . import tasks
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .models import VideoLog, Video, VideoFetchMethod, KeyWordEntry
schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.SECONDS)

def health_check(request):
    data = {
        "message": "vid pong",
        "status": "success"
    }
    return JsonResponse(data, status=status.HTTP_200_OK)

def check_trigger(request):
    task_name = "FamPay"
    
    if KeyWordEntry.objects.filter(keyword=task_name).exists():
        return JsonResponse({"status":"Keyword already exists"})
    
    keyword = KeyWordEntry.objects.create(keyword=task_name)

    task = PeriodicTask.objects.create(
        interval=schedule,  # Use the interval schedule
        name=task_name,  # Name of the task
        task="apps.videos.tasks.process_trigger",  # Task to schedule
        start_time=timezone.now() # Set the start time
    )


    tasks.process_trigger.delay(
        keyword = keyword
    )

    return JsonResponse({"status":"Done"})