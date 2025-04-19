import json
from typing import Dict
from utils.youtube_utils import download_video, extract_metadata
from utils.video_processing import extract_key_segments

class YouTubeScraper:
    def __init__(self):
        self.min_views = 10000  # Quality threshold
        
    def process_video(self, query: str) -> Dict:
        """Main pipeline: search -> download -> analyze"""
        # 1. Download best matching video
        video_path = download_video(
            query=query,
            quality="720p",
            duration_max="15m"
        )
        
        # 2. Extract metadata and content
        metadata = extract_metadata(video_path)
        key_segments = extract_key_segments(video_path)
        
        return {
            "video_path": video_path,
            "metadata": metadata,
            "key_segments": key_segments[:3]  # Top 3 moments
        }