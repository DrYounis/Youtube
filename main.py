"""
Main Automation Script
Orchestrates the entire video creation and upload process
"""

import os
import sys
from datetime import datetime
import yaml
import argparse

# Import our modules
from modules.story_generator import StoryGenerator
from modules.tts_generator import TTSGenerator
from modules.footage_manager import FootageManager
from modules.video_creator import VideoCreator
from modules.youtube_uploader import YouTubeUploader


class AutomationPipeline:
    """Main automation pipeline for Islamic story videos"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize the automation pipeline"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize all modules
        print("🚀 Initializing automation pipeline...")
        # Initialize components
        self.story_generator = StoryGenerator(config_path)
        self.tts_generator = TTSGenerator(config_path)
        self.footage_manager = FootageManager(config_path)
        self.video_creator = VideoCreator(config_path)
        
        # YouTube uploader is optional (for testing without upload)
        try:
            self.youtube_uploader = YouTubeUploader(config_path)
            self.can_upload = True
        except (ValueError, FileNotFoundError) as e:
            print(f"⚠️  YouTube upload not available: {str(e)}")
            print("   Videos will be created but not uploaded.")
            self.youtube_uploader = None
            self.can_upload = False
        
        print("✅ All modules initialized!\n")
    
    def create_video(
        self,
        topic=None,
        theme=None,
        upload=True,
        dry_run=False
    ):
        """
        Create and optionally upload a video
        
        Args:
            topic: Story topic (None = random)
            theme: Story theme (None = random)
            upload: Whether to upload to YouTube
            dry_run: If True, don't actually upload
        
        Returns:
            Dict with results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Step 1: Generate story
            print("📖 Step 1/5: Generating Islamic story...")
            story_data = self.story_generator.generate_story(topic=topic, theme=theme)
            
            print(f"   ✅ Generated: {story_data['title']}")
            print(f"   📝 Topic: {story_data['topic']}, Theme: {story_data['theme']}")
            print(f"   ⏱️  Duration: ~{story_data['duration_estimate']}s\n")
            
            # Step 2: Generate voiceover
            print("🎙️  Step 2/5: Generating Arabic voiceover...")
            audio_filename = f"voiceover_{timestamp}.mp3"
            audio_path = os.path.join(
                self.config['paths']['audio_dir'],
                audio_filename
            )
            
            tts_result = self.tts_generator.generate_voiceover(
                story_data['story'],
                audio_path
            )
            
            print(f"   ✅ Voiceover created: {audio_filename}")
            print(f"   ⏱️  Duration: {tts_result['duration']:.1f}s\n")
            
            # Step 3: Get footage
            print("🎬 Step 3/5: Selecting background footage...")
            footage_category = 'islamic' if story_data['topic'] in ['prophets', 'sahaba', 'quran_stories'] else 'nature'
            
            footage_path = self.footage_manager.get_random_footage(
                category=footage_category,
                min_duration=int(tts_result['duration'])
            )
            
            if not footage_path:
                raise Exception("Failed to get footage")
            
            print(f"   ✅ Footage selected: {os.path.basename(footage_path)}\n")
            
            # Step 4: Create video
            print("🎥 Step 4/5: Creating video...")
            video_filename = f"islamic_story_{timestamp}.mp4"
            
            video_result = self.video_creator.create_video(
                footage_path=footage_path,
                audio_path=audio_path,
                story_text=story_data['story'],
                output_filename=video_filename,
                add_subtitles=True
            )
            
            print(f"   ✅ Video created: {video_filename}")
            print(f"   💾 Size: {video_result['file_size'] / (1024*1024):.1f} MB\n")
            
            # Step 5: Upload to YouTube
            if upload and not dry_run:
                print("📤 Step 5/5: Uploading to YouTube...")
                
                # Generate title and description
                title_template = self.config['youtube']['title_template']
                title = title_template.format(story_title=story_data['title'])
                
                description = self.story_generator.generate_description(story_data)
                tags = self.story_generator.generate_tags(story_data)
                
                upload_result = self.youtube_uploader.upload_video(
                    video_path=video_result['output_path'],
                    title=title,
                    description=description,
                    tags=tags
                )
                
                if upload_result['success']:
                    print(f"   ✅ Uploaded successfully!")
                    print(f"   🔗 URL: {upload_result['url']}\n")
                else:
                    print(f"   ❌ Upload failed: {upload_result['error']}\n")
                
                result = {
                    'success': True,
                    'story': story_data,
                    'video': video_result,
                    'upload': upload_result
                }
            else:
                if dry_run:
                    print("⏭️  Step 5/5: Skipping upload (dry run mode)\n")
                else:
                    print("⏭️  Step 5/5: Upload disabled\n")
                
                result = {
                    'success': True,
                    'story': story_data,
                    'video': video_result,
                    'upload': {'skipped': True}
                }
            
            # Summary
            print("=" * 60)
            print("✅ AUTOMATION COMPLETE!")
            print("=" * 60)
            print(f"📖 Story: {story_data['title']}")
            print(f"🎥 Video: {video_result['output_path']}")
            
            if upload and not dry_run and result['upload'].get('success'):
                print(f"🔗 YouTube: {result['upload']['url']}")
            
            print("=" * 60 + "\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ AUTOMATION FAILED: {str(e)}\n")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Islamic Stories YouTube Automation'
    )
    
    parser.add_argument(
        '--topic',
        choices=['prophets', 'sahaba', 'moral_lessons', 'quran_stories'],
        help='Story topic (random if not specified)'
    )
    
    parser.add_argument(
        '--theme',
        help='Story theme (e.g., faith, patience, gratitude)'
    )
    
    parser.add_argument(
        '--no-upload',
        action='store_true',
        help='Create video but do not upload to YouTube'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run full pipeline without uploading (for testing)'
    )
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = AutomationPipeline()
    
    # Run automation
    result = pipeline.create_video(
        topic=args.topic,
        theme=args.theme,
        upload=not args.no_upload,
        dry_run=args.dry_run
    )
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
