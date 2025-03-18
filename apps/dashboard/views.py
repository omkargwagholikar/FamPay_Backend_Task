from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from ..videos.models import *
from ..videos.serializers import *
# Create your views here.
def index(request):
    key_word_obj = KeyWordEntry.objects.all()
    key_words = KeyWordEntrySerializer(key_word_obj, many=True)
    print(key_words.data)
    return render(request, "index.html", {"key_words": key_words.data})    

def health_check(request):
    data = {
        "message": "dash pong",
        "status": "success"
    }
    return JsonResponse(data, status=status.HTTP_200_OK)
