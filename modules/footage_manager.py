"""
Footage Manager Module
Downloads and manages royalty-free stock footage from Pexels
"""

import os
import requests
import json
import random
from urllib.parse import urlparse
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv(dotenv_path='config/.env')


class FootageManager:
    """Manage stock footage from Pexels API"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize footage manager with configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.footage_config = self.config['footage']
        self.paths_config = self.config['paths']
        
        self.api_key = os.getenv('PEXELS_API_KEY')
        if not self.api_key:
            raise ValueError("PEXELS_API_KEY not found. Please add it to GitHub Secrets or .env file.")
        
        self.base_url = "https://api.pexels.com/videos"
        self.headers = {"Authorization": self.api_key}
        
        # Create footage directory
        self.footage_dir = self.paths_config['footage_dir']
        os.makedirs(self.footage_dir, exist_ok=True)
        
        # Cache file to track downloaded footage
        self.cache_file = os.path.join(self.footage_dir, 'footage_cache.json')
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load footage cache from file"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'videos': {}, 'keywords': {}}
    
    def _save_cache(self):
        """Save footage cache to file"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2)
    
    def search_videos(
        self,
        query: str,
        orientation: str = 'portrait',
        size: str = 'medium',
        per_page: int = 15
    ) -> List[Dict]:
        """
        Search for videos on Pexels
        
        Args:
            query: Search query
            orientation: 'portrait' for 9:16, 'landscape', or 'square'
            size: 'large', 'medium', or 'small'
            per_page: Results per page (max 80)
        
        Returns:
            List of video metadata dictionaries
        """
        params = {
            'query': query,
            'orientation': orientation,
            'size': size,
            'per_page': per_page
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('videos', [])
            
        except requests.RequestException as e:
            print(f"Error searching videos: {type(e).__name__}")
            return []
    
    def download_video(self, video_data: Dict, filename: Optional[str] = None) -> Optional[str]:
        """
        Download a video from Pexels
        
        Args:
            video_data: Video metadata from search_videos()
            filename: Optional custom filename
        
        Returns:
            Path to downloaded video file, or None if failed
        """
        # Get HD portrait video file
        video_files = video_data.get('video_files', [])
        
        # Find best quality portrait video
        portrait_files = [
            vf for vf in video_files
            if vf.get('width', 0) < vf.get('height', 0)  # Portrait orientation
        ]
        
        if not portrait_files:
            # Fallback to any file
            portrait_files = video_files
        
        if not portrait_files:
            print("No video files found")
            return None
        
        # Sort by quality (prefer 1080p or higher)
        portrait_files.sort(key=lambda x: x.get('height', 0), reverse=True)
        video_file = portrait_files[0]
        
        video_url = video_file.get('link')
        if not video_url:
            print("No download link found")
            return None

        # Validate URL domain to prevent SSRF
        parsed = urlparse(video_url)
        allowed_domains = ['player.vimeo.com', 'vod-progressive.akamaized.net', 'videos.pexels.com']
        if not any(parsed.hostname and parsed.hostname.endswith(d) for d in allowed_domains):
            print(f"Blocked download from untrusted domain: {parsed.hostname}")
            return None
        
        # Generate filename
        if filename is None:
            video_id = video_data.get('id')
            filename = f"pexels_{video_id}.mp4"
        
        filepath = os.path.join(self.footage_dir, filename)
        
        # Check if already downloaded
        if os.path.exists(filepath):
            print(f"Video already exists: {filename}")
            return filepath
        
        try:
            # Download video
            print(f"Downloading: {filename}...")
            response = requests.get(video_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Save to file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Update cache
            self.cache['videos'][filename] = {
                'id': video_data.get('id'),
                'url': video_data.get('url'),
                'downloaded_at': datetime.now().isoformat(),
                'width': video_file.get('width'),
                'height': video_file.get('height'),
                'duration': video_data.get('duration')
            }
            self._save_cache()
            
            print(f"✅ Downloaded: {filename}")
            return filepath
            
        except requests.RequestException as e:
            print(f"Error downloading video: {type(e).__name__}")
            return None
    
    def get_random_footage(
        self,
        category: str = 'islamic',
        min_duration: int = 10,
        ai_keywords: Optional[str] = None
    ) -> Optional[str]:
        """
        Get appropriate footage for the video
        
        Args:
            category: 'islamic' or 'nature'
            min_duration: Minimum video duration in seconds
            ai_keywords: Specific keywords from AI (comma separated)
        
        Returns:
            Path to video file
        """
        # Safety filter
        safety_config = self.footage_config.get('safety', {})
        strict_mode = safety_config.get('strict_mode', False)
        negative_query = safety_config.get('negative_query', '')
        banned_keywords = safety_config.get('banned_keywords', [])
        mandatory_modifiers = safety_config.get('mandatory_modifiers', '')
        
        # Determine keywords to use
        keywords_to_try = []
        
        if ai_keywords:
            # Check for banned words
            candidates = [k.strip().lower() for k in ai_keywords.split(',')]
            safe_candidates = []
            
            for k in candidates:
                is_banned = False
                for banned in banned_keywords:
                    if banned in k:
                        print(f"⚠️  BLOCKED unsafe keyword: '{k}' (contains '{banned}')")
                        is_banned = True
                        break
                if not is_banned:
                    safe_candidates.append(k)
            
            if safe_candidates:
                keywords_to_try = safe_candidates
            else:
                print("⚠️  All AI keywords were blocked. Falling back to category defaults.")
        
        # Add category defaults for variety (essential fallback)
        category_keywords = self.footage_config['keywords'].get(category, [])
        if category_keywords:
            # In strict mode, only add one fallback to ensure we try AI ones first
            keywords_to_try.append(random.choice(category_keywords))
        
        # Shuffle to try different ones
        random.shuffle(keywords_to_try)
        
        for keyword in keywords_to_try:
            # Check cache first
            cache_key = f"q_{keyword.replace(' ', '_')}"
            
            if cache_key in self.cache.get('keywords', {}):
                # Check for cached files...
                cached_files = self.cache['keywords'][cache_key]
                valid_files = []
                for filename in cached_files:
                    filepath = os.path.join(self.footage_dir, filename)
                    if os.path.exists(filepath):
                        video_info = self.cache['videos'].get(filename, {})
                        downloaded_at = datetime.fromisoformat(video_info.get('downloaded_at', '2020-01-01'))
                        cache_days = self.footage_config.get('cache_duration_days', 30)
                        if datetime.now() - downloaded_at < timedelta(days=cache_days):
                            valid_files.append(filepath)
                
                if valid_files:
                    return random.choice(valid_files)
            
            # Construct strict query
            # Format: "keyword phrase, no people, landscape, nature, -woman -bikini"
            search_terms = [keyword]
            
            if strict_mode and mandatory_modifiers:
                search_terms.append(mandatory_modifiers)
            
            full_query = f"{', '.join(search_terms)} {negative_query}".strip()
            
            print(f"Searching Pexels with strict query: '{full_query}'...")
            
            # Search Pexels
            videos = self.search_videos(full_query, orientation='portrait')
            
            if videos:
                suitable_videos = [v for v in videos if v.get('duration', 0) >= min_duration]
                if not suitable_videos:
                    suitable_videos = videos
                
                video = random.choice(suitable_videos[:10])
                filename = f"q_{keyword.replace(' ', '_')}_{video['id']}.mp4"
                filepath = self.download_video(video, filename)
                
                if filepath:
                    if cache_key not in self.cache['keywords']:
                        self.cache['keywords'][cache_key] = []
                    if filename not in self.cache['keywords'][cache_key]:
                        self.cache['keywords'][cache_key].append(filename)
                        self._save_cache()
                    return filepath
        
        # Ultimate fallback
        print("Falling back to nature footage...")
        return self.get_random_footage('nature', min_duration)
    
    def cleanup_old_footage(self, days: int = 30):
        """
        Remove footage older than specified days
        
        Args:
            days: Number of days to keep footage
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        removed_count = 0
        
        for filename, info in list(self.cache['videos'].items()):
            downloaded_at = datetime.fromisoformat(info.get('downloaded_at', '2020-01-01'))
            
            if downloaded_at < cutoff_date:
                filepath = os.path.join(self.footage_dir, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    removed_count += 1
                
                # Remove from cache
                del self.cache['videos'][filename]
        
        # Clean up keyword cache
        for cache_key in list(self.cache['keywords'].keys()):
            self.cache['keywords'][cache_key] = [
                f for f in self.cache['keywords'][cache_key]
                if f in self.cache['videos']
            ]
            if not self.cache['keywords'][cache_key]:
                del self.cache['keywords'][cache_key]
        
        self._save_cache()
        print(f"🗑️  Removed {removed_count} old footage files")


def test_footage_manager():
    """Test the footage manager"""
    print("Testing Footage Manager...")
    print("-" * 50)
    
    try:
        manager = FootageManager()
        
        # Test 1: Safe Search
        print("\n🔍 Test 1: Normal Search")
        manager.get_random_footage(ai_keywords="mosque, architecture")
        
        # Test 2: Unsafe Search (Should be completely blocked or sanitized)
        print("\n🔍 Test 2: Unsafe Keyword Search (woman, beach)")
        # This should trigger the block/sanitize logic
        manager.get_random_footage(ai_keywords="beautiful woman, beach, summer")
        
        # Test 3: Cache Stats
        print("\n📊 Cache Statistics:")
        print(f"   Cached videos: {len(manager.cache['videos'])}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Test Complete!")


if __name__ == "__main__":
    test_footage_manager()
