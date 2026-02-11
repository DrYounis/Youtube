"""
Text-to-Speech Generator Module
Converts Arabic text to natural-sounding voiceover using Google Cloud TTS
"""

import os
from typing import Dict, Optional
from google.cloud import texttospeech
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv(dotenv_path='config/.env')


class TTSGenerator:
    """Generate Arabic voiceovers using Google Cloud Text-to-Speech"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize TTS generator with configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.tts_config = self.config['tts']
        self.provider = self.tts_config['provider']
        
        # Initialize Google Cloud TTS client
        if self.provider == 'google':
            self.client = texttospeech.TextToSpeechClient()
            self.google_config = self.tts_config['google']
        else:
            raise NotImplementedError(f"Provider '{self.provider}' not yet implemented")
    
    def generate_voiceover(
        self, 
        text: str, 
        output_path: str,
        voice_name: Optional[str] = None,
        speaking_rate: Optional[float] = None,
        pitch: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Generate voiceover from Arabic text
        
        Args:
            text: Arabic text to convert to speech
            output_path: Path to save the audio file (MP3)
            voice_name: Override default voice (optional)
            speaking_rate: Override default speaking rate (optional)
            pitch: Override default pitch (optional)
        
        Returns:
            Dict with 'audio_path', 'duration', 'character_count'
        """
        if self.provider == 'google':
            return self._generate_google_tts(
                text, output_path, voice_name, speaking_rate, pitch
            )
        else:
            raise NotImplementedError(f"Provider '{self.provider}' not implemented")
    
    def _generate_google_tts(
        self,
        text: str,
        output_path: str,
        voice_name: Optional[str] = None,
        speaking_rate: Optional[float] = None,
        pitch: Optional[float] = None
    ) -> Dict[str, any]:
        """Generate voiceover using Google Cloud TTS"""
        
        # Use config defaults if not specified
        voice_name = voice_name or self.google_config['voice_name']
        speaking_rate = speaking_rate or self.google_config['speaking_rate']
        pitch = pitch or self.google_config['pitch']
        language_code = self.google_config['language_code']
        
        try:
            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name
            )
            
            # Select the audio file type and configuration
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=pitch,
                effects_profile_id=['small-bluetooth-speaker-class-device']  # Optimize for mobile
            )
            
            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write the response to the output file
            with open(output_path, 'wb') as out:
                out.write(response.audio_content)
            
            # Get audio duration (approximate based on character count)
            # Google Cloud doesn't return duration directly
            char_count = len(text)
            # Arabic: ~15-18 characters per second at normal speed
            chars_per_second = 16 / speaking_rate
            estimated_duration = char_count / chars_per_second
            
            return {
                'audio_path': output_path,
                'duration': estimated_duration,
                'character_count': char_count,
                'voice_name': voice_name,
                'speaking_rate': speaking_rate,
                'language': language_code
            }
            
        except Exception as e:
            raise Exception(f"Error generating voiceover: {str(e)}")
    
    def list_available_voices(self, language_code: str = 'ar') -> list:
        """
        List all available Arabic voices
        
        Args:
            language_code: Language code (default: 'ar' for Arabic)
        
        Returns:
            List of available voice names
        """
        if self.provider == 'google':
            try:
                # Performs the list voices request
                voices = self.client.list_voices(language_code=language_code)
                
                voice_list = []
                for voice in voices.voices:
                    # Filter for the specified language
                    if language_code in voice.language_codes:
                        voice_info = {
                            'name': voice.name,
                            'gender': texttospeech.SsmlVoiceGender(voice.ssml_gender).name,
                            'language_codes': voice.language_codes
                        }
                        voice_list.append(voice_info)
                
                return voice_list
                
            except Exception as e:
                print(f"Error listing voices: {str(e)}")
                return []
        else:
            return []


def test_tts_generator():
    """Test the TTS generator"""
    print("Testing Text-to-Speech Generator...")
    print("-" * 50)
    
    generator = TTSGenerator()
    
    # List available voices
    print("\n🎤 Available Arabic Voices:")
    voices = generator.list_available_voices('ar')
    for i, voice in enumerate(voices[:5], 1):  # Show first 5
        print(f"{i}. {voice['name']} ({voice['gender']})")
    
    # Test voiceover generation
    test_text = """
    بسم الله الرحمن الرحيم. 
    هذه قصة قصيرة عن الصبر والإيمان. 
    كان هناك رجل صالح يعيش في قرية صغيرة، وكان معروفاً بصبره وحسن خلقه.
    في يوم من الأيام، ابتلاه الله بمصيبة كبيرة، فلم يجزع ولم ييأس.
    بل قال: إنا لله وإنا إليه راجعون، وحمد الله على كل حال.
    """
    
    print("\n🎙️  Generating test voiceover...")
    print(f"Text: {test_text[:100]}...")
    
    output_path = "assets/audio/test_voiceover.mp3"
    
    try:
        result = generator.generate_voiceover(test_text, output_path)
        
        print("\n✅ Voiceover Generated Successfully!")
        print(f"📁 Audio Path: {result['audio_path']}")
        print(f"⏱️  Estimated Duration: {result['duration']:.1f}s")
        print(f"📊 Character Count: {result['character_count']}")
        print(f"🎤 Voice: {result['voice_name']}")
        print(f"🔊 Speaking Rate: {result['speaking_rate']}")
        
        # Check file size
        file_size = os.path.getsize(output_path)
        print(f"💾 File Size: {file_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure you have:")
        print("1. Set GOOGLE_APPLICATION_CREDENTIALS in .env")
        print("2. Downloaded your Google Cloud service account JSON")
        print("3. Enabled Text-to-Speech API in Google Cloud Console")
    
    print("\n" + "=" * 50)
    print("Test Complete!")


if __name__ == "__main__":
    test_tts_generator()
