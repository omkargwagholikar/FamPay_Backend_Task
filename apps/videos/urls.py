from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'videos', views.VideoViewSet, basename='video')


urlpatterns = [
    path("ping/", views.health_check, name="ping"),
    path('', include(router.urls)),
    path('keyword/<str:keyword>/videos/', views.keyword_videos, name='keyword-videos'),
]