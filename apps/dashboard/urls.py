from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index),
    path('ping/', views.health_check),
]