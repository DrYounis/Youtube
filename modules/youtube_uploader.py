"""
YouTube Uploader Module
Handles authentication and uploading videos to YouTube
"""

import os
import stat
import json
from typing import Dict, Optional
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv(dotenv_path='config/.env')

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


class YouTubeUploader:
    """Upload videos to YouTube using YouTube Data API v3"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize YouTube uploader with configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.youtube_config = self.config['youtube']
        self.paths_config = self.config['paths']
        
        self.client_secrets_file = os.getenv('YOUTUBE_CLIENT_SECRETS')
        if not self.client_secrets_file or not os.path.exists(self.client_secrets_file):
            raise ValueError(
                "YOUTUBE_CLIENT_SECRETS not found or file doesn't exist. "
                "Download OAuth 2.0 credentials from Google Cloud Console."
            )
        
        self.token_file = 'config/youtube_token.json'
        self.youtube = None
        
        # Load video history
        self.history_file = self.paths_config['history_file']
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """Load upload history"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'uploads': []}
    
    def _save_history(self):
        """Save upload history"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def authenticate(self):
        """Authenticate with YouTube API using OAuth 2.0"""
        creds = None
        
        # Load saved credentials
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # If no valid credentials, login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing access token...")
                creds.refresh(Request())
            else:
                print("Starting OAuth 2.0 flow...")
                print("A browser window will open for authentication.")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, SCOPES
                )
                creds = flow.run_local_server(port=8080)
            
            # Save credentials with restricted permissions (owner read/write only)
            fd = os.open(self.token_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, 'w') as token:
                token.write(creds.to_json())
            
            print("✅ Authentication successful!")
        
        # Build YouTube service
        self.youtube = build('youtube', 'v3', credentials=creds)
        return True
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list,
        category_id: Optional[str] = None,
        privacy_status: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Upload a video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID
            privacy_status: 'public', 'private', or 'unlisted'
        
        Returns:
            Dict with upload result
        """
        if not self.youtube:
            if not self.authenticate():
                raise Exception("Authentication failed")
        
        # Use config defaults if not specified
        category_id = category_id or self.youtube_config['category_id']
        privacy_status = privacy_status or self.youtube_config['privacy_status']
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'madeForKids': self.youtube_config['made_for_kids'],
                'selfDeclaredMadeForKids': self.youtube_config['made_for_kids']
            }
        }
        
        # Prepare upload
        media = MediaFileUpload(
            video_path,
            chunksize=-1,  # Upload in a single request
            resumable=True,
            mimetype='video/mp4'
        )
        
        print(f"📤 Uploading video to YouTube...")
        print(f"   Title: {title}")
        print(f"   Privacy: {privacy_status}")
        
        try:
            # Execute upload
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"   Upload progress: {progress}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            print(f"✅ Upload successful!")
            print(f"   Video ID: {video_id}")
            print(f"   URL: {video_url}")
            
            # Save to history
            upload_record = {
                'video_id': video_id,
                'url': video_url,
                'title': title,
                'uploaded_at': datetime.now().isoformat(),
                'file_path': video_path,
                'privacy_status': privacy_status,
                'tags': tags
            }
            
            self.history['uploads'].append(upload_record)
            self._save_history()
            
            return {
                'success': True,
                'video_id': video_id,
                'url': video_url,
                'response': response
            }
            
        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_upload_stats(self) -> Dict:
        """Get upload statistics"""
        total_uploads = len(self.history['uploads'])
        
        if total_uploads == 0:
            return {
                'total_uploads': 0,
                'first_upload': None,
                'last_upload': None
            }
        
        uploads = self.history['uploads']
        first = uploads[0]['uploaded_at']
        last = uploads[-1]['uploaded_at']
        
        return {
            'total_uploads': total_uploads,
            'first_upload': first,
            'last_upload': last,
            'recent_videos': uploads[-5:]  # Last 5 uploads
        }


def test_youtube_uploader():
    """Test YouTube uploader (authentication only, no actual upload)"""
    print("Testing YouTube Uploader...")
    print("-" * 50)
    
    try:
        uploader = YouTubeUploader()
        
        # Test authentication
        print("\n🔐 Testing authentication...")
        uploader.authenticate()
        print("✅ Authentication successful!")
        
        # Show stats
        print("\n📊 Upload Statistics:")
        stats = uploader.get_upload_stats()
        print(f"   Total uploads: {stats['total_uploads']}")
        
        if stats['total_uploads'] > 0:
            print(f"   First upload: {stats['first_upload']}")
            print(f"   Last upload: {stats['last_upload']}")
            
            if stats['recent_videos']:
                print("\n   Recent uploads:")
                for video in stats['recent_videos']:
                    print(f"   - {video['title']}")
                    print(f"     {video['url']}")
        
        print("\n⚠️  To test actual upload, use the main automation script.")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure you have:")
        print("1. Created OAuth 2.0 credentials in Google Cloud Console")
        print("2. Downloaded client_secrets.json")
        print("3. Set YOUTUBE_CLIENT_SECRETS in .env to point to the file")
        print("4. Enabled YouTube Data API v3 in your Google Cloud project")
        print("\nSetup guide: https://developers.google.com/youtube/v3/getting-started")
    
    print("\n" + "=" * 50)
    print("Test Complete!")


if __name__ == "__main__":
    test_youtube_uploader()
