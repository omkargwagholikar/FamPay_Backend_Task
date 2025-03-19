from django.contrib import admin
from django.urls import include, path
from . import views 
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="FamPay backend assignment",
        default_version="FamPay Backend Assignment",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="omkarrwagholikar@gmail.com"),
        license=openapi.License(name="Test License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    path("admin/", admin.site.urls),
    path("ping/", views.health_check),

    path("api/", include("apps.videos.urls")),
    path("", include("apps.dashboard.urls")),
]
