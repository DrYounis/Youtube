"""
Video Creator Module
Compiles final video from footage, voiceover, and subtitles
"""

import os
from typing import Dict, List, Optional, Tuple
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip
)
from moviepy.video.fx.all import crop, resize
from PIL import ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import yaml
import math

class VideoCreator:
    """Create YouTube Shorts videos with footage, voiceover, and Arabic subtitles"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize video creator with configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.video_config = self.config['video']
        self.paths_config = self.config['paths']
        
        # Target resolution (9:16 for Shorts)
        self.width = self.video_config['resolution']['width']
        self.height = self.video_config['resolution']['height']
        self.fps = self.video_config['fps']
        
        # Create output directory
        os.makedirs(self.paths_config['output_dir'], exist_ok=True)
        os.makedirs(self.paths_config['temp_dir'], exist_ok=True)
    
    def prepare_footage(self, footage_path: str, duration: float) -> VideoFileClip:
        """
        Prepare background footage for the video
        
        Args:
            footage_path: Path to footage file
            duration: Required duration in seconds
        
        Returns:
            Prepared VideoFileClip
        """
        clip = VideoFileClip(footage_path)
        
        # Get clip dimensions
        clip_width, clip_height = clip.size
        
        # Calculate target aspect ratio (9:16)
        target_ratio = self.width / self.height
        clip_ratio = clip_width / clip_height
        
        # Crop to 9:16 if needed
        if abs(clip_ratio - target_ratio) > 0.01:
            if clip_ratio > target_ratio:
                # Clip is wider, crop width
                new_width = int(clip_height * target_ratio)
                x_center = clip_width / 2
                x1 = int(x_center - new_width / 2)
                clip = crop(clip, x1=x1, width=new_width)
            else:
                # Clip is taller, crop height
                new_height = int(clip_width / target_ratio)
                y_center = clip_height / 2
                y1 = int(y_center - new_height / 2)
                clip = crop(clip, y1=y1, height=new_height)
        
        # Resize to target resolution
        clip = resize(clip, (self.width, self.height))
        
        # Handle duration
        if clip.duration < duration:
            # Loop the clip if too short
            num_loops = math.ceil(duration / clip.duration)
            clip = concatenate_videoclips([clip] * num_loops)
        
        # Trim to exact duration
        clip = clip.subclip(0, min(duration, clip.duration))
        
        return clip
    
    def create_subtitle_clip(
        self,
        text: str,
        start_time: float,
        duration: float
    ) -> TextClip:
        """
        Create an Arabic subtitle clip
        
        Args:
            text: Arabic text to display
            start_time: When subtitle appears (seconds)
            duration: How long subtitle shows (seconds)
        
        Returns:
            TextClip positioned and styled
        """
        subtitle_config = self.video_config['subtitles']
        
        # Reshape Arabic text for proper display
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        
        # Create text clip
        txt_clip = TextClip(
            bidi_text,
            fontsize=subtitle_config['font_size'],
            color=subtitle_config['color'],
            font='Arial',  # Fallback font, will use system Arabic font
            stroke_color=subtitle_config['outline_color'],
            stroke_width=subtitle_config['outline_width'],
            method='caption',
            size=(self.width - 100, None),  # Leave margin
            align='center'
        )
        
        # Position subtitle
        position_map = {
            'center': ('center', 'center'),
            'bottom': ('center', self.height - 200),
            'top': ('center', 150)
        }
        
        position = position_map.get(
            subtitle_config['position'],
            ('center', 'center')
        )
        
        txt_clip = txt_clip.set_position(position)
        txt_clip = txt_clip.set_start(start_time)
        txt_clip = txt_clip.set_duration(duration)
        
        return txt_clip
    
    def generate_subtitles(
        self,
        text: str,
        audio_duration: float
    ) -> List[TextClip]:
        """
        Generate timed subtitles from text
        
        Args:
            text: Full Arabic text
            audio_duration: Duration of audio in seconds
        
        Returns:
            List of TextClip subtitles
        """
        subtitle_config = self.video_config['subtitles']
        max_chars = subtitle_config['max_chars_per_line']
        
        # Split text into sentences
        sentences = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                # Split by periods and other punctuation
                parts = line.replace('،', '.').split('.')
                for part in parts:
                    part = part.strip()
                    if part:
                        sentences.append(part)
        
        if not sentences:
            return []
        
        # Calculate time per sentence
        time_per_sentence = audio_duration / len(sentences)
        
        # Create subtitle clips
        subtitle_clips = []
        current_time = 0
        
        for sentence in sentences:
            # Split long sentences into multiple lines
            words = sentence.split()
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                word_length = len(word)
                if current_length + word_length + 1 > max_chars and current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:
                    current_line.append(word)
                    current_length += word_length + 1
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Create subtitle for sentences (show all lines together)
            subtitle_text = '\n'.join(lines)
            
            subtitle_clip = self.create_subtitle_clip(
                subtitle_text,
                current_time,
                time_per_sentence
            )
            
            subtitle_clips.append(subtitle_clip)
            current_time += time_per_sentence
        
        return subtitle_clips
    
    def create_video(
        self,
        footage_path: str,
        audio_path: str,
        story_text: str,
        output_filename: str,
        add_subtitles: bool = True
    ) -> Dict[str, any]:
        """
        Create final video with footage, audio, and subtitles
        
        Args:
            footage_path: Path to background footage
            audio_path: Path to voiceover audio
            story_text: Story text for subtitles
            output_filename: Name for output file
            add_subtitles: Whether to add subtitles
        
        Returns:
            Dict with video info
        """
        print("🎬 Creating video...")
        
        # Load audio to get duration
        audio_clip = AudioFileClip(audio_path)
        video_duration = audio_clip.duration
        
        print(f"   Audio duration: {video_duration:.1f}s")
        
        # Prepare footage
        print("   Preparing footage...")
        video_clip = self.prepare_footage(footage_path, video_duration)
        
        # Add audio
        video_clip = video_clip.set_audio(audio_clip)
        
        # Generate and add subtitles
        if add_subtitles and self.video_config['subtitles']['enabled']:
            print("   Generating subtitles...")
            try:
                subtitle_clips = self.generate_subtitles(story_text, video_duration)
                
                if subtitle_clips:
                    # Composite video with subtitles
                    video_clip = CompositeVideoClip([video_clip] + subtitle_clips)
                    print(f"   Added {len(subtitle_clips)} subtitle segments")
            except Exception as e:
                print(f"   ⚠️  Subtitle generation failed: {str(e)}")
                print("   Continuing without subtitles...")
        
        # Output path
        output_path = os.path.join(self.paths_config['output_dir'], output_filename)
        
        # Write video file
        print(f"   Rendering video to: {output_filename}")
        video_clip.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=os.path.join(self.paths_config['temp_dir'], 'temp_audio.m4a'),
            remove_temp=True,
            preset='medium',  # Faster encoding
            threads=4
        )
        
        # Clean up
        video_clip.close()
        audio_clip.close()
        
        # Get file info
        file_size = os.path.getsize(output_path)
        
        print(f"✅ Video created successfully!")
        print(f"   File: {output_path}")
        print(f"   Size: {file_size / (1024*1024):.1f} MB")
        
        return {
            'output_path': output_path,
            'duration': video_duration,
            'resolution': f"{self.width}x{self.height}",
            'file_size': file_size,
            'fps': self.fps
        }


def test_video_creator():
    """Test the video creator with sample files"""
    print("Testing Video Creator...")
    print("-" * 50)
    
    # This test requires sample footage and audio files
    print("\n⚠️  This test requires:")
    print("1. Sample footage in assets/footage/")
    print("2. Sample audio in assets/audio/")
    print("\nTo fully test, please run the main automation script.")
    print("Or manually create test files using other modules.")
    
    # Check if sample files exist
    import os
    
    footage_dir = "assets/footage"
    audio_dir = "assets/audio"
    
    if os.path.exists(footage_dir):
        footage_files = [f for f in os.listdir(footage_dir) if f.endswith('.mp4')]
        if footage_files:
            print(f"\n✅ Found {len(footage_files)} footage files")
    
    if os.path.exists(audio_dir):
        audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
        if audio_files:
            print(f"✅ Found {len(audio_files)} audio files")
    
    print("\n" + "=" * 50)
    print("Test Complete!")


if __name__ == "__main__":
    test_video_creator()
