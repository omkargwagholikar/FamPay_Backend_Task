from django.urls import path

from . import views

urlpatterns = [
    path("ping/", views.health_check),
    path("test_trigger/", views.check_trigger),
]