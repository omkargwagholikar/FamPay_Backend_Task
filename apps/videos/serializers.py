from rest_framework import serializers
from .models import Video, KeyWordEntry, VideoLog

class KeyWordEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyWordEntry
        fields = ['id', 'keyword', 'created_at']


class VideoSerializer(serializers.ModelSerializer):
    keyword_text = serializers.CharField(source='keyword.keyword', read_only=True)
    
    class Meta:
        model = Video
        fields = ['video_id', 'title', 'description', 'published_at', 
                  'channel_title', 'thumbnail', 'created_at', 
                  'updated_at', 'keyword', 'keyword_text', 'method']
