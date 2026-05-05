"""
YouTube API Service for fetching car diagnostic videos
Handles searching and caching YouTube videos based on diagnostic issues
"""

import json
import requests
from typing import List, Optional
from config import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class VideoCache:
    """Simple in-memory cache for YouTube video results"""
    _cache: dict = {}
    _cache_duration = timedelta(days=7)  # Cache videos for 7 days
    
    @classmethod
    def get(cls, key: str) -> Optional[dict]:
        """Get cached videos by search key"""
        if key in cls._cache:
            cached_data, timestamp = cls._cache[key]
            if datetime.now() - timestamp < cls._cache_duration:
                return cached_data
            else:
                del cls._cache[key]
        return None
    
    @classmethod
    def set(cls, key: str, data: dict) -> None:
        """Cache videos with timestamp"""
        cls._cache[key] = (data, datetime.now())
    
    @classmethod
    def clear(cls) -> None:
        """Clear all cache"""
        cls._cache.clear()


class YouTubeService:
    """Service to fetch and manage YouTube videos for car diagnostics"""
    
    YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"
    
    # Map diagnostic issues to YouTube search keywords
    SEARCH_KEYWORDS = {
        "check engine light": "check engine light diagnosis repair",
        "timing belt": "timing belt replacement cost",
        "engine knock": "engine knocking noise repair",
        "abs warning": "abs warning light fix",
        "battery": "car battery replacement guide",
        "oil pressure": "oil pressure warning light",
        "coolant": "coolant temperature warning fix",
        "transmission": "transmission problems diagnosis",
        "brake": "brake system repair guide",
        "alternator": "alternator replacement cost",
    }
    
    @staticmethod
    def get_search_query(issue: str) -> str:
        """
        Get the best search query for a diagnostic issue
        Returns a keyword phrase for YouTube search
        """
        issue_lower = issue.lower()
        
        # Try to find a direct match
        for key, query in YouTubeService.SEARCH_KEYWORDS.items():
            if key in issue_lower:
                return query
        
        # Default: use the issue as-is with 'car repair' added
        return f"{issue} car repair DIY"
    
    @staticmethod
    async def fetch_videos(
        issue: str,
        max_results: int = 3,
        use_cache: bool = True
    ) -> List[dict]:
        """
        Fetch YouTube videos for a car diagnostic issue
        
        Args:
            issue: The diagnostic issue (e.g., "Timing Belt Noise")
            max_results: Number of videos to return
            use_cache: Whether to use cached results
            
        Returns:
            List of video objects with title and url
        """
        
        if not settings.youtube_api_key:
            logger.warning("YouTube API key not configured")
            return []
        
        # Check cache first
        cache_key = f"{issue}:{max_results}"
        if use_cache:
            cached_videos = VideoCache.get(cache_key)
            if cached_videos:
                logger.info(f"Returning cached videos for: {issue}")
                return cached_videos
        
        try:
            search_query = YouTubeService.get_search_query(issue)
            
            params = {
                "part": "snippet",
                "q": search_query,
                "type": "video",
                "maxResults": max_results,
                "videoEmbeddable": "true",  # Only embeddable videos
                "safeSearch": "strict",  # Family-safe content
                "relevanceLanguage": "en",
                "key": settings.youtube_api_key,
                "order": "relevance"
            }
            
            logger.info(f"Searching YouTube for: {search_query}")
            response = requests.get(YouTubeService.YOUTUBE_API_URL, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            videos = []
            
            if "items" in data:
                for item in data["items"][:max_results]:
                    if item["id"]["kind"] == "youtube#video":
                        video_id = item["id"]["videoId"]
                        title = item["snippet"]["title"]
                        
                        videos.append({
                            "title": title,
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "video_id": video_id,
                            "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                            "fetched_at": datetime.now().isoformat()
                        })
            
            # Cache the results
            if videos:
                VideoCache.set(cache_key, videos)
                logger.info(f"Fetched {len(videos)} videos for: {issue}")
            
            return videos
        
        except requests.exceptions.Timeout:
            logger.error("YouTube API request timed out")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching YouTube videos: {e}")
            return []
    
    @staticmethod
    async def get_or_create_video_links(issue: str, db_session=None) -> List[dict]:
        """
        Get video links for an issue, checking database first
        If not in database, fetch from YouTube and cache them
        
        Args:
            issue: The diagnostic issue
            db_session: Optional database session for persistence
            
        Returns:
            List of video links
        """
        
        # Try to get from database if session provided
        if db_session:
            try:
                from models import VideoCache as DBVideoCache
                cached = db_session.query(DBVideoCache).filter(
                    DBVideoCache.issue_name == issue.lower()
                ).first()
                
                if cached:
                    logger.info(f"Using cached videos from database for: {issue}")
                    return json.loads(cached.video_links)
            except Exception as e:
                logger.warning(f"Could not fetch from database cache: {e}")
        
        # Fetch from YouTube API
        videos = await YouTubeService.fetch_videos(issue, max_results=3)
        
        # Cache in database if session provided
        if db_session and videos:
            try:
                from models import VideoCache as DBVideoCache
                # Check if already exists
                existing = db_session.query(DBVideoCache).filter(
                    DBVideoCache.issue_name == issue.lower()
                ).first()
                
                if existing:
                    existing.video_links = json.dumps(videos)
                    existing.updated_at = datetime.now()
                else:
                    cache_entry = DBVideoCache(
                        issue_name=issue.lower(),
                        video_links=json.dumps(videos)
                    )
                    db_session.add(cache_entry)
                
                db_session.commit()
                logger.info(f"Cached {len(videos)} videos in database for: {issue}")
            except Exception as e:
                logger.warning(f"Could not cache videos in database: {e}")
                # Continue anyway, videos are already fetched
        
        return videos
