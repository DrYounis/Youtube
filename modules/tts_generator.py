"""
Text-to-Speech Generator Module
Converts Arabic text to natural-sounding voiceover using Google Cloud TTS or ElevenLabs
"""

import os
import requests
from typing import Dict, Optional
from google.cloud import texttospeech
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv(dotenv_path='config/.env')


class TTSGenerator:
    """Generate Arabic voiceovers using Google Cloud TTS or ElevenLabs"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize TTS generator with configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.tts_config = self.config['tts']
        self.provider = self.tts_config['provider']
        
        # Initialize provider-specific client
        if self.provider == 'google':
            self.client = texttospeech.TextToSpeechClient()
            self.google_config = self.tts_config['google']
        elif self.provider == 'elevenlabs':
            self.api_key = os.getenv('ELEVENLABS_API_KEY')
            if not self.api_key:
                raise ValueError("ELEVENLABS_API_KEY not found. Please add it to GitHub Secrets or .env file.")
            self.elevenlabs_config = self.tts_config['elevenlabs']
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
            speaking_rate: Override default speaking rate (optional, ElevenLabs uses stability)
            pitch: Override default pitch (optional, ElevenLabs uses similarity_boost)
        
        Returns:
            Dict with 'audio_path', 'duration', 'character_count'
        """
        if self.provider == 'google':
            return self._generate_google_tts(
                text, output_path, voice_name, speaking_rate, pitch
            )
        elif self.provider == 'elevenlabs':
            return self._generate_elevenlabs_tts(
                text, output_path, voice_name
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
    
    def _generate_elevenlabs_tts(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str] = None
    ) -> Dict[str, any]:
        """Generate voiceover using ElevenLabs API"""
        
        # Use config defaults if not specified
        voice_id = voice_id or self.elevenlabs_config['voice_id']
        model_id = self.elevenlabs_config.get('model_id', 'eleven_multilingual_v2')
        stability = self.elevenlabs_config.get('stability', 0.5)
        similarity_boost = self.elevenlabs_config.get('similarity_boost', 0.75)
        
        try:
            # Debug: Check API Key format (Masked)
            if self.api_key:
                masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}"
                print(f"   🔑 ElevenLabs Key Debug: Length={len(self.api_key)}, Prefix={self.api_key[:4]}, Suffix={self.api_key[-4:]}")
                if self.api_key.strip() != self.api_key:
                    print(f"   ❌ WARNING: API Key has leading/trailing whitespace! Length stripped: {len(self.api_key.strip())}")
            else:
                print("   ❌ ERROR: ElevenLabs API Key is missing or empty!")

            # ElevenLabs API endpoint
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            # Headers
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            # Request payload
            data = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost
                }
            }
            
            # Make API request
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"ElevenLabs API error: HTTP {response.status_code}")
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write the audio content to file
            with open(output_path, 'wb') as out:
                out.write(response.content)
            
            # Estimate duration (Arabic: ~15-18 characters per second)
            char_count = len(text)
            chars_per_second = 16
            estimated_duration = char_count / chars_per_second
            
            return {
                'audio_path': output_path,
                'duration': estimated_duration,
                'character_count': char_count,
                'voice_id': voice_id,
                'model_id': model_id,
                'provider': 'elevenlabs'
            }
            
        except Exception as e:
            raise Exception(f"Error generating ElevenLabs voiceover: {str(e)}")
    
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
        elif self.provider == 'elevenlabs':
            try:
                # Get available voices from ElevenLabs
                url = "https://api.elevenlabs.io/v1/voices"
                headers = {"xi-api-key": self.api_key}
                
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    voices_data = response.json()
                    voice_list = []
                    
                    for voice in voices_data.get('voices', []):
                        # Filter for multilingual voices (that support Arabic)
                        voice_info = {
                            'voice_id': voice['voice_id'],
                            'name': voice['name'],
                            'description': voice.get('description', ''),
                            'category': voice.get('category', 'N/A')
                        }
                        voice_list.append(voice_info)
                    
                    return voice_list
                else:
                    print(f"Error fetching ElevenLabs voices: {response.status_code}")
                    return []
                    
            except Exception as e:
                print(f"Error listing ElevenLabs voices: {str(e)}")
                return []
        else:
            return []


def test_tts_generator():
    """Test the TTS generator"""
    print("Testing Text-to-Speech Generator...")
    print("-" * 50)
    
    generator = TTSGenerator()
    
    print(f"\n🎤 Using Provider: {generator.provider.upper()}")
    
    # List available voices
    print("\n📋 Available Voices:")
    voices = generator.list_available_voices('ar')
    
    if generator.provider == 'google':
        for i, voice in enumerate(voices[:5], 1):  # Show first 5
            print(f"{i}. {voice['name']} ({voice['gender']})")
    elif generator.provider == 'elevenlabs':
        for i, voice in enumerate(voices[:5], 1):  # Show first 5
            print(f"{i}. {voice['name']} - {voice.get('description', 'N/A')}")
    
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
        
        if generator.provider == 'google':
            print(f"🎤 Voice: {result['voice_name']}")
            print(f"🔊 Speaking Rate: {result['speaking_rate']}")
        elif generator.provider == 'elevenlabs':
            print(f"🎤 Voice ID: {result['voice_id']}")
            print(f"🤖 Model: {result['model_id']}")
        
        # Check file size
        file_size = os.path.getsize(output_path)
        print(f"💾 File Size: {file_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if generator.provider == 'google':
            print("\nMake sure you have:")
            print("1. Set GOOGLE_APPLICATION_CREDENTIALS in .env")
            print("2. Downloaded your Google Cloud service account JSON")
            print("3. Enabled Text-to-Speech API in Google Cloud Console")
        elif generator.provider == 'elevenlabs':
            print("\nMake sure you have:")
            print("1. Set ELEVENLABS_API_KEY in .env")
            print("2. Valid ElevenLabs API key from https://elevenlabs.io/")
    
    print("\n" + "=" * 50)
    print("Test Complete!")


if __name__ == "__main__":
    test_tts_generator()
