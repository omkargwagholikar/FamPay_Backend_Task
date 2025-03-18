from django.http import JsonResponse
from rest_framework.views import APIView, status

def health_check(request):
    data = {
        "message": "vid pong",
        "status": "success"
    }
    return JsonResponse(data, status=status.HTTP_200_OK)


