from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status

# Create your views here.
def index(request):
    return render(request, "index.html")    

def health_check(request):
    data = {
        "message": "dash pong",
        "status": "success"
    }
    return JsonResponse(data, status=status.HTTP_200_OK)
