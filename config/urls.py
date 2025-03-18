from django.contrib import admin
from django.urls import include, path
from . import views 

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ping/", views.health_check),

    path("api/", include("apps.videos.urls")),
    path("", include("apps.dashboard.urls")),
]
