import json
import logging
from django.utils import timezone
from django.http import JsonResponse
from rest_framework.views import status
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .models import Video, KeyWordEntry
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Video, KeyWordEntry
from .serializers import VideoSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

schedule, created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)

logger = logging.getLogger("task_log")

@swagger_auto_schema(
    method='get',
    operation_description="Health check endpoint for the video service",
    responses={200: openapi.Response(
        description="Success",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description="Service message"),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description="Service status"),
            }
        )
    )}
)
@api_view(['GET'])
def health_check(request):
    data = {
        "message": "vid pong",
        "status": "success"
    }
    return JsonResponse(data, status=status.HTTP_200_OK)

def create_keyword_and_task(request, task_name):
    logger.info(task_name)

    if KeyWordEntry.objects.filter(keyword=task_name).exists(): # Checking if keyword already exists
        return JsonResponse({"status":"Keyword already exists"})
    keyword = KeyWordEntry.objects.create(keyword=task_name)

    task = PeriodicTask.objects.create(
        interval=schedule,  # Use the interval schedule
        name=task_name,  # Name of the task
        task="apps.videos.tasks.process_trigger",  # Task to schedule
        start_time=timezone.now(), # Set the start time
        args=json.dumps([task_name]),
    )

    return JsonResponse({"status":"Done"})


class StandardResultsPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for listing videos with pagination.
    Can be filtered by keyword.
    """
    serializer_class = VideoSerializer
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'channel_title']
    ordering_fields = ['published_at', 'created_at']
    ordering = ['-published_at']  # Default ordering

    def get_queryset(self):
        """
        Optionally restricts the returned videos to a given keyword,
        by filtering against a `keyword` query parameter in the URL.
        """
        queryset = Video.objects.all()
        keyword_id = self.request.query_params.get('keyword_id', None)
        keyword_text = self.request.query_params.get('keyword', None)
        
        print("keyword_id: ", keyword_id)
        print("keyword_text: ", keyword_text)

        if keyword_id is not None:
            queryset = queryset.filter(keyword_id=keyword_id)
        elif keyword_text is not None:
            # Find the keyword entry or return empty queryset if not found
            keyword_entries = KeyWordEntry.objects.filter(keyword=keyword_text)
            if keyword_entries.exists():
                queryset = queryset.filter(keyword=keyword_entries.first())
            else:
                queryset = Video.objects.none()
                
        return queryset


@api_view(['GET'])
def keyword_videos(request, keyword):
    """
    API endpoint to retrieve paginated videos for a specific keyword.
    """
    print(keyword)
    # First, get the keyword entry or return 404 if not found
    # keyword_entry = get_object_or_404(KeyWordEntry, keyword=keyword)
    if not KeyWordEntry.objects.filter(keyword=keyword).exists():
        resp = create_keyword_and_task(request, keyword)
        print("Create new keyword and task for", keyword)
        print(resp)
    keyword_entry = KeyWordEntry.objects.get(keyword=keyword)

    # Then, get all videos for this keyword
    videos = Video.objects.filter(keyword=keyword_entry)
    
    # Apply pagination
    paginator = StandardResultsPagination()
    paginated_videos = paginator.paginate_queryset(videos, request)
    
    # Serialize the data
    serializer = VideoSerializer(paginated_videos, many=True)
    
    # Return paginated response
    return paginator.get_paginated_response(serializer.data)
