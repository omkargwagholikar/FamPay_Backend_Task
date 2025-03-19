import logging
from typing import Optional, List
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings
from apps.videos.models import VideoFetchMethod
import requests
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger("youtube_log")

INVIDIOUS_URL = os.getenv("INVIDIOUS_URL")
INVIDIOUS_API = f"http://{INVIDIOUS_URL}/api/v1/search"
YT_KEYS = os.getenv("YT_KEYS")

YT_KEYS = [key.strip() for key in YT_KEYS.split(",")]
if len(YT_KEYS) == 0 or (len(YT_KEYS) == 1 and YT_KEYS[0] == ""):
    YT_KEYS = []

class YouTubeAPIKeyManager:
    """
    Manages multiple YouTube API keys and automatically switches to the next available key
    if the current key's quota is exhausted.
    """
    def __init__(self, api_keys: List[str]):
        self.api_keys = api_keys
        self.current_key_index = 0

    def get_current_key(self) -> str:
        """Return the current API key."""
        return self.api_keys[self.current_key_index]

    def switch_to_next_key(self) -> str:
        """Switch to the next available API key."""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.info(f"Switched to the next YouTube API key. Now using key at index {self.current_key_index}")
        return self.get_current_key()

    def build_youtube_client(self) -> Optional[object]:
        """
        Build a YouTube API client with the current API key.
        If the build fails, try with the next key.
        """
        attempts = 0
        max_attempts = len(self.api_keys)
        
        while attempts < max_attempts:
            try:
                api_key = self.get_current_key()
                youtube = build('youtube', 'v3', developerKey=api_key)
                return youtube
            except HttpError as e:
                logger.error(f"Error building YouTube client with API key at index {self.current_key_index}: {str(e)}")
                self.switch_to_next_key()
                attempts += 1
        
        logger.critical("All YouTube API keys failed.")
        return None


class YouTubeAPI:
    """
    Service class to interact with the YouTube API v3.
    """
    def __init__(self):
        self.api_keys = YT_KEYS
        
        print("="*10)
        print(self.api_keys, type(self.api_keys))
        print("="*10)

        self.key_manager = YouTubeAPIKeyManager(self.api_keys)
        self.youtube = self.key_manager.build_youtube_client()


    def fetch_videos_from_invidious(self, query):
        try:
            invidious_response = requests.get(
                INVIDIOUS_API,
                params={
                    "q": query,
                    "sort_by": "upload_date",
                    "day":"today"
                    # "type": "videos",
                },
            )
            logger.info("Successful fetch from Invidious API")
            invidious_data = invidious_response.json()
            return invidious_data
        
        except Exception as e:
            logger.error(f"Failed to fetch videos from Invidious API: {str(e)}")
            return None

    def fetch_videos(self, query: str, max_results: int = 50, page_token: str = None) -> Optional[dict]:
        """
        Fetch videos for the given search query.
        
        Args:
            query (str): The search query.
            max_results (int): Maximum number of results to return.
            page_token (str, optional): Token for pagination.
        
        Returns:
            dict: API response containing video data.
        """
        if not self.youtube:
            logger.error("YouTube client is not available. Using INVIDIOUS_API")
            data = self.fetch_videos_from_invidious(query)
            if data is not None:
                return (VideoFetchMethod.INVIDIOUS, data)
            return None

        attempts = 0
        max_attempts = len(self.api_keys)
        
        while attempts < max_attempts:
            logger.info("Attempt:", attempts)
            try:
                response = self.youtube.search().list(
                    q=query,
                    part='snippet',
                    maxResults=max_results,
                    order='date',  # Sort by date (newest first)
                    type='video',
                    pageToken=page_token
                ).execute()
                
                # Get video IDs for additional details
                video_ids = [item['id']['videoId'] for item in response.get('items', [])]
                
                # Fetch additional video details (like view count)
                if video_ids:
                    details_response = self.youtube.videos().list(
                        part='statistics',
                        id=','.join(video_ids)
                    ).execute()
                    
                    # Create a mapping of video ID to statistics
                    stats_dict = {
                        item['id']: item['statistics'] 
                        for item in details_response.get('items', [])
                    }
                    
                    # Merge statistics into the search results
                    for item in response.get('items', []):
                        video_id = item['id']['videoId']
                        if video_id in stats_dict:
                            item['statistics'] = stats_dict[video_id]
                
                return (VideoFetchMethod.YOUTUBE, response)
                
            except HttpError as e:
                error_message = str(e)
                logger.error(f"YouTube API error: {error_message}")
                
                # If quota exceeded, switch to the next key
                if 'quotaExceeded' in error_message:
                    logger.warning("Quota exceeded. Switching to the next API key.")
                    self.key_manager.switch_to_next_key()
                    self.youtube = self.key_manager.build_youtube_client()
                    attempts += 1
                else:
                    # For other errors, raise the exception
                    logger.error(f"Unhandled YouTube API error: {error_message}")
                    return None
        
        logger.critical("All YouTube API keys have exhausted their quotas.")

        data = self.fetch_videos_from_invidious(query)
        if data is not None:
            return (VideoFetchMethod.INVIDIOUS, data)
        
        return None
    
# youtube_api = YouTubeAPI()
# search_query = QUERY
# max_results = 50
# logger.info(f"Fetching latest videos for query: {search_query}")
    
# response = youtube_api.fetch_videos(search_query, max_results)
# # for r in response:
# #     print(r['title'])

# print(response)