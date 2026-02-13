"""
Trend Manager Module
Fetches trending Islamic content from YouTube and generates safe, relevant story hooks.
"""

import os
import json
import yaml
from typing import List, Dict, Optional
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from openai import OpenAI
import anthropic

# Load environment variables
load_dotenv(dotenv_path='config/.env')

class TrendManager:
    """Manages R&D: Fetches trends and generates content ideas"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize TrendManager"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        # Fallback to secrets file if needed, but API key is preferred for search
        
        # Initialize AI
        self.provider = self.config['story'].get('ai_provider', 'anthropic')
        if self.provider == 'anthropic':
            self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307')
        else:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
            
        self.queue_file = 'data/content_queue.json'
        os.makedirs('data', exist_ok=True)

    def fetch_trending_topics(self) -> List[str]:
        """Fetch trending Islamic topics from YouTube"""
        if not self.youtube_api_key:
            print("⚠️ YOUTUBE_API_KEY not found. Skipping trend fetch.")
            return []
            
        print("🔍 Scanning YouTube for Islamic trends...")
        try:
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            
            # Search for specific generic terms to find what's popular NOW
            queries = [
                "قصص إسلامية مؤثرة", 
                "محاضرات دينية مؤثرة", 
                "قصة نبي", 
                "تفسير آية مؤثرة"
            ]
            
            titles = []
            for q in queries:
                request = youtube.search().list(
                    part="snippet",
                    q=q,
                    order="viewCount",  # Get most popular
                    publishedAfter=(datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')), # Today/Recent - logic needed for "Last 7 days"
                    maxResults=5,
                    type="video"
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    title = item['snippet']['title']
                    print(f"   📈 Found Trend: {title}")
                    titles.append(title)
            
            return titles
            
        except HttpError as e:
            print(f"❌ YouTube API Error: {e}")
            return []

    def generate_safe_hooks(self, trends: List[str]) -> List[Dict]:
        """Use AI to convert trends into SAFE story hooks"""
        if not trends:
            return []
            
        print("🧠 Analyzing trends and generating safe hooks...")
        
        system_prompt = """
        You are the 'Content Strategy Head' for a strict Islamic storytelling channel.
        
        Your Goal:
        1. Analyze the provided list of TRENDING YOUTUBE TITLES.
        2. Extract the core spiritual/moral theme.
        3. Generate 3 UNIQUE Story Ideas (Hooks) based on these trends.
        
        CRITICAL SAFETY RULES (Self-Correction):
        - NO VISUAL DEPICTION of people allowed. Ideas must be visualizable using symbols (mosque, desert, light, book).
        - REJECT any trend that relies on acting, drama, or women showing faces.
        - FOCUS on: Moral lessons, spiritual reflections, non-human stories (e.g., history of a mosque, a specific Dua).
        
        Output Format (JSON):
        [
            {
                "topic": "moral_lessons",
                "theme": "patience",
                "hook_prompt": "Tell a story about the patience of the palm tree in the desert...",
                "rationale": "Trending topic was 'Patience in Hardship'"
            }
        ]
        """
        
        user_prompt = f"Here are the trending titles from YouTube today:\n{json.dumps(trends, ensure_ascii=False)}\n\nGenerate 3 safe, high-potential story hooks."
        
        try:
            if self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                content = response.content[0].text
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                
            # Parse JSON
            import re
            json_str = re.search(r'\[.*\]', content, re.DOTALL).group()
            hooks = json.loads(json_str)
            
            return hooks
            
        except Exception as e:
            print(f"❌ AI Generation Error: {e}")
            return []

    def update_queue(self):
        """Main daily task"""
        trends = self.fetch_trending_topics()
        using_fallback = False
        
        if not trends:
            # Fallback for testing if API fails or no key
            print("⚠️  No live trends found (or missing API key). Using static fallback topics.")
            trends = ["Patience in Islam", "Story of Prophet Yusuf", "Importance of Prayer"]
            using_fallback = True
            
        hooks = self.generate_safe_hooks(trends)
        
        if hooks:
            # Load existing
            try:
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    queue = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                queue = []
            
            # Append new (avoid duplicates check could be added)
            queue.extend(hooks)
            
            # Save
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue, f, indent=2, ensure_ascii=False)
                
            print(f"✅ Added {len(hooks)} new ideas to the content queue.")
            if using_fallback:
                print("⚠️  NOTE: R&D ran in FALLBACK MODE (Static Topics). Add YOUTUBE_API_KEY to search real trends.")
            else:
                print("🚀 SUCCESS: R&D ran with LIVE YOUTUBE TRENDS.")
        else:
            print("⚠️ No new hooks generated.")

if __name__ == "__main__":
    tm = TrendManager()
    tm.update_queue()
