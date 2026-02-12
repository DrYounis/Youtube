"""
Story Generator Module
Generates original Islamic stories in Arabic using OpenAI or Anthropic API
"""

import os
import random
from typing import Dict, List, Optional
from openai import OpenAI
import anthropic
from dotenv import load_dotenv
import yaml
import re
import json

# Load environment variables
load_dotenv(dotenv_path='config/.env')

class StoryGenerator:
    """Generate authentic Islamic stories in Arabic"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize the story generator with configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.story_config = self.config['story']
        
        # Determine which AI provider to use
        self.provider = self.story_config.get('ai_provider', 'openai')  # Default to OpenAI
        
        if self.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=api_key)
            self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        elif self.provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found. Please add it to GitHub Secrets or .env file.")
            self.client = anthropic.Anthropic(api_key=api_key)
            # Handle empty string from env
            self.model = os.getenv('ANTHROPIC_MODEL') or 'claude-3-haiku-20240307'
        else:
            raise ValueError(f"Unknown AI provider: {self.provider}. Use 'openai' or 'anthropic'")
        
        # Story templates by topic
        self.topic_prompts = {
            'prophets': 'قصة قصيرة عن أحد الأنبياء والدروس المستفادة من حياته',
            'sahaba': 'قصة ملهمة عن أحد الصحابة الكرام وموقف من حياته',
            'moral_lessons': 'قصة إسلامية قصيرة تحتوي على درس أخلاقي وعبرة',
            'quran_stories': 'قصة من القرآن الكريم مع التفسير والعبر'
        }
    
    def generate_story(self, topic: Optional[str] = None, theme: Optional[str] = None) -> Dict[str, str]:
        """
        Generate an Islamic story
        
        Args:
            topic: Story topic (prophets, sahaba, moral_lessons, quran_stories)
                   If None, randomly selected from config
            theme: Story theme (faith, patience, gratitude, etc.)
                   If None, randomly selected from config
        
        Returns:
            Dict with 'title', 'story', 'topic', 'theme', 'duration_estimate'
        """
        # Select random topic if not specified
        if topic is None:
            topic = random.choice(self.story_config['topics'])
        
        # Select random theme if not specified
        if theme is None:
            theme = random.choice(self.story_config['themes'])
        
        # Get the topic prompt
        topic_prompt = self.topic_prompts.get(topic, self.topic_prompts['moral_lessons'])
        
        # Calculate target word count for desired duration
        # Arabic speech: ~120-150 words per minute
        target_seconds = self.story_config['length_seconds']
        words_per_second = 2.2  # ~132 words per minute
        target_words = int(target_seconds * words_per_second)
        
        # Create the system prompt
        system_prompt = f"""أنت راوي قصص إسلامية محترف. مهمتك كتابة قصص إسلامية أصلية باللغة العربية الفصحى.

المتطلبات:
- القصة يجب أن تكون أصلية (ليست منسوخة)
- باللغة العربية الفصحى الواضحة
- مناسبة لجميع الأعمار
- تحتوي على درس أو عبرة واضحة
- طول القصة: {target_words} كلمة تقريباً ({target_seconds} ثانية عند القراءة)
- الموضوع: {topic_prompt}
- الثيمة الرئيسية: {theme}

يجب أن تكون القصة:
- ملهمة ومؤثرة
- صحيحة من الناحية الإسلامية
- سهلة الفهم
- مناسبة لمقاطع يوتيوب شورتس

ملاحظة هامة جداً:
- لا تذكر النساء في القصة إلا للضرورة القصوى وباحترام تام.
- القصة يجب أن تكون ملتزمة بالقيم الإسلامية المحافظة.

المخرجات المطلوبة (تنسيق JSON):
{{
  "title": "العنوان التلقائي",
  "story": "نص القصة هنا...",
  "visual_keywords": "كلمات مفتاحية بالإنجليزية لوصف المشاهد المناسبة (مثال: desert, mosque, prayer, stars)"
}}"""

        user_prompt = f"اكتب قصة إسلامية قصيرة مؤثرة حول موضوع: {topic_prompt}، مع التركيز على ثيمة '{theme}'."
        
        try:
            # Call AI API based on provider
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.8,
                    max_tokens=1000
                )
                import json
                story_json = json.loads(response.choices[0].message.content.strip())
                
            elif self.provider == 'anthropic':
                # Anthropic doesn't have a strict json_object mode like OpenAI in this version
                # so we append a JSON instruction to the user prompt
                user_prompt += "\n\nPlease provide the output in JSON format with keys: 'title', 'story', 'visual_keywords'."
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                import json
                import re
                content = response.content[0].text.strip()
                # Clean up potential markdown code blocks
                json_str = re.search(r'{.*}', content, re.DOTALL).group()
                story_json = json.loads(json_str)
            
            story_text = story_json.get('story', '')
            title = story_json.get('title', '')
            visual_keywords = story_json.get('visual_keywords', '')
            
            if not title:
                title = self._generate_title(story_text, topic, theme)
            
            # Clean title
            title = self._clean_title(title)
            
            # Estimate actual duration
            word_count = len(story_text.split())
            duration_estimate = int(word_count / words_per_second)
            
            return {
                'title': title,
                'story': story_text,
                'topic': topic,
                'theme': theme,
                'word_count': word_count,
                'duration_estimate': duration_estimate,
                'visual_keywords': visual_keywords,
                'language': 'ar'
            }
            
        except Exception as e:
            raise Exception(f"Error generating story: {str(e)}")

    def _clean_title(self, title: str) -> str:
        """Clean title from prefixes, quotes and extra labels"""
        
        # Remove common prefixes and labels
        prefixes = [
            r'^عنوان مقترح:\s*',
            r'^العنوان:\s*',
            r'^مقترح لعنوان:\s*',
            r'^Title:\s*',
            r'^Suggested Title:\s*',
            r'^العنوان المقترح:\s*',
            r'^\s*-\s*'
        ]
        
        cleaned = title.strip()
        for p in prefixes:
            cleaned = re.sub(p, '', cleaned, flags=re.IGNORECASE).strip()
            
        # Remove surrounding quotes and brackets
        cleaned = cleaned.strip('"').strip("'").strip('«').strip('»').strip('(').strip(')')
        
        # Remove trailing/leading spaces one last time
        return cleaned.strip()
    
    def _generate_title(self, story_text: str, topic: str, theme: str) -> str:
        """Generate an engaging title for the story"""
        
        system_prompt = "أنت خبير في صياغة عناوين جذابة للقصص الإسلامية. مخرجاتك يجب أن تكون (نص العنوان فقط) بدون أي كلمات إضافية مثل 'عنوان مقترح' أو 'نص العنوان' وبدون علامات تنصيص."
        user_prompt = f"اقترح عنواناً جذاباً ومؤثراً لهذه القصة الإسلامية:\n\n{story_text[:500]}..."
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=50
                )
                title = response.choices[0].message.content.strip()
                
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=50,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                title = response.content[0].text.strip()
            
            # Remove quotes if present
            title = title.strip('"').strip("'").strip('«').strip('»')
            return title
            
        except Exception as e:
            # Fallback to generic title
            topic_titles = {
                'prophets': 'قصة نبي',
                'sahaba': 'قصة صحابي',
                'moral_lessons': 'عبرة وعظة',
                'quran_stories': 'قصة قرآنية'
            }
            return topic_titles.get(topic, 'قصة إسلامية')
    
    def generate_description(self, story_data: Dict[str, str]) -> str:
        """
        Generate YouTube description for the story
        
        Args:
            story_data: Story dictionary from generate_story()
        
        Returns:
            Formatted description text
        """
        # Extract first 2-3 sentences as summary
        story_text = story_data['story']
        sentences = story_text.split('.')[:3]
        summary = '. '.join(sentences).strip() + '.'
        
        # Use template from config
        description_template = self.config['youtube']['description_template']
        
        description = description_template.format(
            story_summary=summary
        )
        
        return description
    
    def generate_tags(self, story_data: Dict[str, str]) -> List[str]:
        """
        Generate relevant tags for the video
        
        Args:
            story_data: Story dictionary from generate_story()
        
        Returns:
            List of tags
        """
        base_tags = self.config['youtube']['tags'].copy()
        
        # Add topic-specific tags
        topic_tags = {
            'prophets': ['الأنبياء', 'prophets', 'سيرة'],
            'sahaba': ['الصحابة', 'companions', 'السيرة النبوية'],
            'moral_lessons': ['عبرة', 'lesson', 'أخلاق', 'wisdom'],
            'quran_stories': ['القرآن', 'quran', 'تفسير']
        }
        
        if story_data['topic'] in topic_tags:
            base_tags.extend(topic_tags[story_data['topic']])
        
        # Add theme tag
        base_tags.append(story_data['theme'])
        
        return base_tags


def test_story_generator():
    """Test the story generator"""
    print("Testing Story Generator...")
    print("-" * 50)
    
    generator = StoryGenerator()
    
    # Test story generation
    print("\nGenerating story...")
    story = generator.generate_story()
    
    print(f"\n📖 Title: {story['title']}")
    print(f"📝 Topic: {story['topic']}")
    print(f"🎯 Theme: {story['theme']}")
    print(f"📊 Word Count: {story['word_count']}")
    print(f"⏱️  Estimated Duration: {story['duration_estimate']}s")
    print(f"\n📄 Story:\n{story['story']}")
    
    # Test description generation
    print("\n" + "-" * 50)
    print("\n📝 YouTube Description:")
    description = generator.generate_description(story)
    print(description)
    
    # Test tags generation
    print("\n" + "-" * 50)
    print("\n🏷️  Tags:")
    tags = generator.generate_tags(story)
    print(", ".join(tags))
    
    print("\n" + "=" * 50)
    print("✅ Story Generator Test Complete!")


if __name__ == "__main__":
    test_story_generator()
