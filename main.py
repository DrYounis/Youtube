"""
Main Automation Script
Orchestrates the entire video creation and upload process.
"""

import os
import sys
import json
import logging
import argparse
import traceback
from datetime import datetime

import yaml

# Import our modules
from modules.story_generator import StoryGenerator
from modules.tts_generator import TTSGenerator
from modules.footage_manager import FootageManager
from modules.video_creator import VideoCreator
from modules.youtube_uploader import YouTubeUploader

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class AutomationPipeline:
    """Main automation pipeline for Islamic story videos."""

    # Required environment variables for the pipeline to function
    REQUIRED_ENV_VARS = [
        'ANTHROPIC_API_KEY',
        'ELEVENLABS_API_KEY',
        'PEXELS_API_KEY',
    ]

    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize the automation pipeline."""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        logger.info("Initializing automation pipeline...")

        # Check required environment variables
        self._check_env_vars()

        # Initialize components
        try:
            self.story_generator = StoryGenerator(config_path)
            self.tts_generator = TTSGenerator(config_path)
            self.footage_manager = FootageManager(config_path)
            self.video_creator = VideoCreator(config_path)
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

        # YouTube uploader is optional (can run without upload for testing)
        try:
            self.youtube_uploader = YouTubeUploader(config_path)
            self.can_upload = True
        except (ValueError, FileNotFoundError) as e:
            logger.warning(f"YouTube upload not available: {e} — videos will be created but not uploaded.")
            self.youtube_uploader = None
            self.can_upload = False

        logger.info("All modules initialized.")

    def _check_env_vars(self) -> None:
        """Validate that all required environment variables are set."""
        missing = []
        for var in self.REQUIRED_ENV_VARS:
            val = os.getenv(var)
            if val and len(val) > 5:
                logger.info(f"  ENV {var}: OK")
            else:
                logger.warning(f"  ENV {var}: MISSING")
                missing.append(var)
        if missing:
            logger.warning(f"Missing env vars: {missing}. Pipeline may fail.")

    def _load_trending_hook(self, trend_manager) -> dict | None:
        """
        Pop the next hook from the R&D trending queue, if available.

        Returns:
            A hook dict or None if queue is empty / unavailable.
        """
        try:
            if not os.path.exists(trend_manager.queue_file):
                return None
            with open(trend_manager.queue_file, 'r', encoding='utf-8') as f:
                queue = json.load(f)
            if not queue:
                return None
            hook = queue.pop(0)
            with open(trend_manager.queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue, f, indent=2, ensure_ascii=False)
            logger.info(f"Using R&D trending hook: '{hook.get('rationale')}'")
            return hook
        except Exception as e:
            logger.warning(f"R&D Queue error: {e}")
            return None

    def create_video(
        self,
        topic: str | None = None,
        theme: str | None = None,
        upload: bool = True,
        dry_run: bool = False,
    ) -> dict:
        """
        Create and optionally upload a video.

        Args:
            topic: Story topic (None = random from config).
            theme: Story theme (None = random from config).
            upload: Whether to upload to YouTube.
            dry_run: If True, skip the upload step (for testing).

        Returns:
            Dict with keys: success (bool), story, video, upload.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # ── Step 1: Generate story ────────────────────────────────────────
            logger.info("Step 1/5: Generating Islamic story...")

            from modules.trend_manager import TrendManager
            trend_manager = TrendManager()
            story_data = None

            # Try trending hook first (if no explicit topic/theme given)
            if not topic and not theme:
                hook = self._load_trending_hook(trend_manager)
                if hook:
                    story_data = self.story_generator.generate_story(
                        topic=hook.get('topic'),
                        theme=hook.get('theme', '') + f" (Focus: {hook.get('hook_prompt', '')})",
                    )

            if not story_data:
                story_data = self.story_generator.generate_story(topic=topic, theme=theme)

            logger.info(f"  Story: {story_data['title']}")
            logger.info(f"  Topic: {story_data['topic']} | Theme: {story_data['theme']}")
            logger.info(f"  Est. duration: ~{story_data['duration_estimate']}s")

            # ── Step 2: Generate voiceover ────────────────────────────────────
            logger.info("Step 2/5: Generating Arabic voiceover...")
            audio_filename = f"voiceover_{timestamp}.mp3"
            audio_path = os.path.join(self.config['paths']['audio_dir'], audio_filename)

            tts_result = self.tts_generator.generate_voiceover(story_data['story'], audio_path)
            logger.info(f"  Voiceover: {audio_filename} ({tts_result['duration']:.1f}s)")

            # ── Step 3: Get footage ───────────────────────────────────────────
            logger.info("Step 3/5: Selecting background footage...")
            logger.info(f"  Visual keywords: {story_data.get('visual_keywords', 'N/A')}")

            footage_path = self.footage_manager.get_random_footage(
                category=story_data['topic'],
                min_duration=story_data['duration_estimate'],
                ai_keywords=story_data.get('visual_keywords'),
            )

            if not footage_path:
                raise RuntimeError("Failed to retrieve footage — check footage_manager config.")

            logger.info(f"  Footage: {os.path.basename(footage_path)}")

            # ── Step 4: Create video ──────────────────────────────────────────
            logger.info("Step 4/5: Creating video...")
            video_filename = f"islamic_story_{timestamp}.mp4"

            video_result = self.video_creator.create_video(
                footage_path=footage_path,
                audio_path=audio_path,
                story_text=story_data['story'],
                output_filename=video_filename,
                add_subtitles=True,
            )
            logger.info(f"  Video: {video_filename} ({video_result['file_size'] / (1024 * 1024):.1f} MB)")

            # ── Step 5: Upload ────────────────────────────────────────────────
            if upload and not dry_run:
                logger.info("Step 5/5: Uploading to YouTube...")

                # Validate client secrets JSON before attempting upload
                client_secrets_path = os.getenv('YOUTUBE_CLIENT_SECRETS')
                if client_secrets_path and os.path.exists(client_secrets_path):
                    try:
                        with open(client_secrets_path, 'r') as f:
                            json.load(f)
                        logger.info("  Client secrets JSON: valid")
                    except json.JSONDecodeError as e:
                        logger.error(f"  Client secrets JSON is invalid: {e}")
                        return {'success': False, 'error': 'Invalid YouTube client secrets JSON'}

                if not self.youtube_uploader:
                    logger.error("  YouTube uploader not initialized — cannot upload.")
                    return {'success': False, 'error': 'YouTube uploader not initialized'}

                title = self.config['youtube']['title_template'].format(
                    story_title=story_data['title']
                )
                description = self.story_generator.generate_description(story_data)
                tags = self.story_generator.generate_tags(story_data)

                upload_result = self.youtube_uploader.upload_video(
                    video_path=video_result['output_path'],
                    title=title,
                    description=description,
                    tags=tags,
                )

                if upload_result['success']:
                    logger.info(f"  Upload successful: {upload_result['url']}")
                else:
                    logger.error(f"  Upload failed: {upload_result['error']}")
                    return {'success': False, 'error': f"Upload failed: {upload_result['error']}"}

                result = {'success': True, 'story': story_data, 'video': video_result, 'upload': upload_result}
            else:
                reason = "dry-run mode" if dry_run else "upload disabled"
                logger.info(f"Step 5/5: Skipping upload ({reason})")
                result = {'success': True, 'story': story_data, 'video': video_result, 'upload': {'skipped': True}}

            # ── Summary ───────────────────────────────────────────────────────
            logger.info("=" * 50)
            logger.info("AUTOMATION COMPLETE")
            logger.info(f"  Story:  {story_data['title']}")
            logger.info(f"  Video:  {video_result['output_path']}")
            if upload and not dry_run and result['upload'].get('success'):
                logger.info(f"  YouTube: {result['upload']['url']}")
            logger.info("=" * 50)

            return result

        except Exception as e:
            logger.error(f"AUTOMATION FAILED: {e}")
            logger.debug(traceback.format_exc())
            return {'success': False, 'error': str(e)}


def main() -> None:
    """Main entry point for the automation pipeline."""
    parser = argparse.ArgumentParser(description='Islamic Stories YouTube Automation')
    parser.add_argument(
        '--topic',
        choices=['prophets', 'sahaba', 'moral_lessons', 'quran_stories'],
        help='Story topic (random if not specified)',
    )
    parser.add_argument('--theme', help='Story theme (e.g., faith, patience, gratitude)')
    parser.add_argument('--no-upload', action='store_true', help='Create video but skip YouTube upload')
    parser.add_argument('--dry-run', action='store_true', help='Full pipeline run without uploading (testing)')
    args = parser.parse_args()

    pipeline = AutomationPipeline()
    result = pipeline.create_video(
        topic=args.topic,
        theme=args.theme,
        upload=not args.no_upload,
        dry_run=args.dry_run,
    )
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
