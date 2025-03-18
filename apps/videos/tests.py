import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from django.http import JsonResponse
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from apps.videos.models import Video, KeyWordEntry, VideoLog, VideoFetchMethod
from apps.videos.tasks import process_trigger
from apps.videos.views import create_keyword_and_task, health_check, keyword_videos
from apps.videos.serializers import VideoSerializer


class KeyWordEntryModelTests(TestCase):
    def setUp(self):
        self.keyword = KeyWordEntry.objects.create(keyword="python")
        
    def test_keyword_creation(self):
        """Test that a keyword can be created"""
        self.assertEqual(self.keyword.keyword, "python")
        self.assertTrue(isinstance(self.keyword, KeyWordEntry))
        self.assertEqual(str(self.keyword), "python")
    
    def test_signal_deletes_periodic_task(self):
        """Test that deleting a keyword deletes associated periodic task"""
        # Create a periodic task
        schedule = IntervalSchedule.objects.create(every=10, period=IntervalSchedule.SECONDS)
        task = PeriodicTask.objects.create(
            interval=schedule,
            name="python",
            task="apps.videos.tasks.process_trigger",
            args=json.dumps(["python"]),
        )
        
        # Delete the keyword
        self.keyword.delete()
        
        # Check that the task is deleted
        with self.assertRaises(PeriodicTask.DoesNotExist):
            PeriodicTask.objects.get(name="python")


class VideoModelTests(TestCase):
    def setUp(self):
        self.keyword = KeyWordEntry.objects.create(keyword="python")
        self.video = Video.objects.create(
            video_id="test123",
            title="Test Video",
            description="Test Description",
            published_at=timezone.now(),
            channel_title="Test Channel",
            thumbnail="https://example.com/thumbnail.jpg",
            keyword=self.keyword,
            method=VideoFetchMethod.YOUTUBE
        )
        
    def test_video_creation(self):
        """Test that a video can be created"""
        self.assertEqual(self.video.video_id, "test123")
        self.assertEqual(self.video.title, "Test Video")
        self.assertEqual(self.video.keyword, self.keyword)
        self.assertEqual(str(self.video), "Test Video")


class VideoLogModelTests(TestCase):
    def setUp(self):
        self.keyword = KeyWordEntry.objects.create(keyword="python")
        self.video_log = VideoLog.objects.create(
            error=False,
            method=VideoFetchMethod.YOUTUBE,
            number_added=5,
            keyword=self.keyword
        )
        
    def test_video_log_creation(self):
        """Test that a video log can be created"""
        self.assertEqual(self.video_log.error, False)
        self.assertEqual(self.video_log.method, VideoFetchMethod.YOUTUBE)
        self.assertEqual(self.video_log.number_added, 5)
        self.assertEqual(self.video_log.keyword, self.keyword)
        self.assertEqual(str(self.video_log), "python - youtube - 5")


class ProcessTriggerTaskTests(TestCase):
    @patch('apps.videos.tasks.YouTubeAPI')
    def setUp(self, mock_youtube_api):
        self.keyword = KeyWordEntry.objects.create(keyword="python")
        
        # Mock the YouTube API
        self.mock_youtube_api_instance = mock_youtube_api.return_value
        
    @patch('apps.videos.tasks.YouTubeAPI')
    def test_process_trigger_youtube(self, mock_youtube_api):
        """Test that process_trigger creates videos from YouTube API"""
        # Set up the mock
        mock_instance = mock_youtube_api.return_value
        mock_instance.fetch_videos.return_value = (VideoFetchMethod.YOUTUBE, {
            'items': [
                {
                    'id': {'videoId': 'abc123'},
                    'snippet': {
                        'title': 'Test YouTube Video',
                        'description': 'Test Description',
                        'publishedAt': '2023-01-01T00:00:00Z',
                        'channelTitle': 'Test Channel',
                        'thumbnails': {'default': {'url': 'https://example.com/thumbnail.jpg'}}
                    }
                }
            ]
        })
        
        # Call the task
        process_trigger(self.keyword.keyword)
        
        # Check that the video was created
        video = Video.objects.get(video_id='abc123')
        self.assertEqual(video.title, 'Test YouTube Video')
        self.assertEqual(video.method, VideoFetchMethod.YOUTUBE)
        
        # Check that the log was created
        log = VideoLog.objects.get(keyword=self.keyword)
        self.assertEqual(log.number_added, 1)
        self.assertEqual(log.method, VideoFetchMethod.YOUTUBE)
        
    @patch('apps.videos.tasks.YouTubeAPI')
    def test_process_trigger_invidious(self, mock_youtube_api):
        """Test that process_trigger creates videos from Invidious API"""
        # Set up the mock
        published_timestamp = int(datetime.now().timestamp())
        mock_instance = mock_youtube_api.return_value
        mock_instance.fetch_videos.return_value = (VideoFetchMethod.INVIDIOUS, [
            {
                'videoId': 'def456',
                'title': 'Test Invidious Video',
                'description': 'Test Description',
                'author': 'Test Author',
                'published': published_timestamp,
                'videoThumbnails': [{'url': 'https://example.com/thumbnail.jpg'}]
            }
        ])
        
        # Call the task
        process_trigger(self.keyword.keyword)
        
        # Check that the video was created
        video = Video.objects.get(video_id='def456')
        self.assertEqual(video.title, 'Test Invidious Video')
        self.assertEqual(video.method, VideoFetchMethod.INVIDIOUS)
        
        # Check that the log was created
        log = VideoLog.objects.get(keyword=self.keyword)
        self.assertEqual(log.number_added, 1)
        self.assertEqual(log.method, VideoFetchMethod.INVIDIOUS)


class HealthCheckViewTests(APITestCase):
    def test_health_check(self):
        """Test the health check endpoint"""
        url = reverse('ping')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "message": "vid pong",
            "status": "success"
        })


# class CreateKeywordAndTaskViewTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
        
#     def test_create_new_keyword_and_task(self):
#         """Test creating a new keyword and associated task"""
#         request = self.factory.get('/create-keyword/')
#         response = create_keyword_and_task(request, "python")
        
#         # Check the response
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(json.loads(response.content), {"status": "Done"})
        
#         # Check that the keyword was created
#         self.assertTrue(KeyWordEntry.objects.filter(keyword="python").exists())
        
#         # Check that the periodic task was created
#         self.assertTrue(PeriodicTask.objects.filter(name="python").exists())
        
#     def test_create_existing_keyword(self):
#         """Test attempting to create a keyword that already exists"""
#         # Create the keyword first
#         KeyWordEntry.objects.create(keyword="python")
        
#         request = self.factory.get('/create-keyword/')
#         response = create_keyword_and_task(request, "python")
        
#         # Check the response
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(json.loads(response.content), {"status": "Keyword already exists"})


class VideoViewSetTests(APITestCase):
    def setUp(self):
        # Create keywords
        self.keyword1 = KeyWordEntry.objects.create(keyword="python")
        self.keyword2 = KeyWordEntry.objects.create(keyword="django")
        
        # Create videos
        self.video1 = Video.objects.create(
            video_id="python1",
            title="Python Tutorial",
            description="Learn Python",
            published_at=timezone.now() - timedelta(days=1),
            channel_title="Python Channel",
            thumbnail="https://example.com/python.jpg",
            keyword=self.keyword1,
            method=VideoFetchMethod.YOUTUBE
        )
        
        self.video2 = Video.objects.create(
            video_id="django1",
            title="Django Tutorial",
            description="Learn Django",
            published_at=timezone.now(),
            channel_title="Django Channel",
            thumbnail="https://example.com/django.jpg",
            keyword=self.keyword2,
            method=VideoFetchMethod.YOUTUBE
        )
        
    def test_list_all_videos(self):
        """Test listing all videos"""
        url = reverse('video-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        
    def test_filter_by_keyword_id(self):
        """Test filtering videos by keyword_id"""
        url = f"{reverse('video-list')}?keyword_id={self.keyword1.id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], "Python Tutorial")
        
    def test_filter_by_keyword_text(self):
        """Test filtering videos by keyword text"""
        url = f"{reverse('video-list')}?keyword=django"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], "Django Tutorial")
        
    def test_search_by_title(self):
        """Test searching videos by title"""
        url = f"{reverse('video-list')}?search=Python"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], "Python Tutorial")
        
    def test_ordering(self):
        """Test ordering videos"""
        url = f"{reverse('video-list')}?ordering=published_at"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['title'], "Python Tutorial")
        
        url = f"{reverse('video-list')}?ordering=-published_at"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['title'], "Django Tutorial")


class KeywordVideosViewTests(APITestCase):
    def setUp(self):
        # Create keyword
        self.keyword = KeyWordEntry.objects.create(keyword="python")
        
        # Create videos
        for i in range(15):
            Video.objects.create(
                video_id=f"python{i}",
                title=f"Python Tutorial {i}",
                description=f"Learn Python {i}",
                published_at=timezone.now() - timedelta(days=i),
                channel_title="Python Channel",
                thumbnail="https://example.com/python.jpg",
                keyword=self.keyword,
                method=VideoFetchMethod.YOUTUBE
            )
    
    @patch('apps.videos.views.create_keyword_and_task')
    def test_get_videos_for_existing_keyword(self, mock_create_task):
        """Test getting videos for an existing keyword"""
        # self.keyword = KeyWordEntry.objects.create(keyword="python")
        url = reverse('keyword-videos', kwargs={'keyword': 'python'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 15)
        self.assertEqual(len(response.data['results']), 12)  # Default page size
        
        # Make sure create_keyword_and_task was not called
        mock_create_task.assert_not_called()
    
    # @patch('apps.videos.views.create_keyword_and_task')
    # def test_get_videos_for_new_keyword(self, mock_create_task):
    #     """Test getting videos for a new keyword creates the keyword"""
    #     # Configure the mock
    #     mock_response = MagicMock()
    #     mock_response.return_value = JsonResponse({"status": "Done"})
    #     mock_create_task.return_value = mock_response
        
    #     # self.keyword = KeyWordEntry.objects.create(keyword="django")
    #     url = reverse('keyword-videos', kwargs={'keyword': 'django1'})
    #     response = self.client.get(url)
        
    #     # Check that create_keyword_and_task was called
    #     mock_create_task.assert_called_once()
        
    #     # Since we're mocking, we won't actually have videos to return
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['count'], 0)


class VideoSerializerTests(TestCase):
    def setUp(self):
        self.keyword = KeyWordEntry.objects.create(keyword="python")
        self.video = Video.objects.create(
            video_id="test123",
            title="Test Video",
            description="Test Description",
            published_at=timezone.now(),
            channel_title="Test Channel",
            thumbnail="https://example.com/thumbnail.jpg",
            keyword=self.keyword,
            method=VideoFetchMethod.YOUTUBE
        )
        
    # def test_serializer_contains_expected_fields(self):
    #     """Test that the serializer contains the expected fields"""
    #     serializer = VideoSerializer(instance=self.video)
    #     data = serializer.data
        
    #     self.assertEqual(set(data.keys()), {
    #         'video_id', 'title', 'description', 'published_at', 
    #         'channel_title', 'thumbnail', 'created_at', 'updated_at',
    #         'keyword', 'method'
    #     })
        
    def test_serializer_field_content(self):
        """Test that the serializer fields contain the expected content"""
        serializer = VideoSerializer(instance=self.video)
        data = serializer.data
        
        self.assertEqual(data['video_id'], 'test123')
        self.assertEqual(data['title'], 'Test Video')
        self.assertEqual(data['description'], 'Test Description')
        self.assertEqual(data['channel_title'], 'Test Channel')
        self.assertEqual(data['thumbnail'], 'https://example.com/thumbnail.jpg')
        self.assertEqual(data['method'], VideoFetchMethod.YOUTUBE)
        # Check the keyword is correctly serialized
        self.assertEqual(data['keyword'], self.keyword.id)