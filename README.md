# YouTube Islamic Stories Automation System

An automated system for generating original Islamic story content in Arabic, creating professional YouTube Shorts videos, and uploading them to YouTube automatically.

## Features

✅ **AI-Generated Stories** - Original Islamic stories in Arabic using OpenAI GPT
✅ **Natural Arabic Voiceover** - Google Cloud Text-to-Speech with native Arabic voices
✅ **Royalty-Free Footage** - Automatic download from Pexels API
✅ **Professional Subtitles** - Arabic subtitles with proper text shaping
✅ **YouTube Integration** - Automatic upload with optimized metadata
✅ **Scheduling** - Automated video creation on schedule

## Prerequisites

- **Python 3.8+**
- **API Keys** (see setup below)
- **FFmpeg** (for video processing)

## Installation

### 1. Clone or Download

```bash
cd /Volumes/Samsung/youtube
```

### 2. Install FFmpeg

```bash
# macOS
brew install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup API Keys

#### a) OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy key for later

#### b) Google Cloud Text-to-Speech
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable "Cloud Text-to-Speech API"
4. Create service account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Create service account
   - Grant role: "Cloud Text-to-Speech User"
   - Create JSON key
   - Download the JSON file

#### c) YouTube Data API
1. Go to https://console.cloud.google.com/
2. Enable "YouTube Data API v3"
3. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" → "Credentials"
   - Create "OAuth 2.0 Client ID"
   - Application type: "Desktop app"
   - Download JSON (client_secrets.json)

#### d) Pexels API Key
1. Go to https://www.pexels.com/api/
2. Sign up for free API key
3. Copy key for later

### 5. Configure Environment Variables

```bash
# Copy example env file
cp config/.env.example config/.env

# Edit config/.env with your keys
nano config/.env
```

Fill in your API keys:

```bash
OPENAI_API_KEY=sk-your-key-here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-credentials.json
YOUTUBE_CLIENT_SECRETS=/path/to/youtube-client-secrets.json
PEXELS_API_KEY=your-pexels-key-here
```

### 6. Create Required Directories

```bash
mkdir -p assets/footage assets/audio assets/output assets/temp assets/music data logs
```

## Configuration

Edit `config/config.yaml` to customize:

- **Story topics** (prophets, sahaba, moral lessons, Quran stories)
- **Video length** (30-60 seconds)
- **Voice settings** (voice name, speaking rate)
- **Subtitle styling** (font, color, position)
- **Upload settings** (privacy, category, tags)
- **Automation schedule** (daily/weekly, time)

## Usage

### Create a Single Video

```bash
# Create and upload a video (random topic)
python main.py

# Create without uploading
python main.py --no-upload

# Specify topic and theme
python main.py --topic prophets --theme faith

# Dry run (test without uploading)
python main.py --dry-run
```

### Test Individual Modules

```bash
# Test story generation
python modules/story_generator.py

# Test text-to-speech
python modules/tts_generator.py

# Test footage manager
python modules/footage_manager.py

# Test YouTube authentication
python modules/youtube_uploader.py
```

### Automated Scheduling

```bash
# Enable automation in config/config.yaml first:
# automation:
#   enabled: true
#   schedule:
#     frequency: "daily"
#     time: "09:00"

# Start scheduler
python scheduler.py

# Or run automation immediately
python scheduler.py --run-now
```

## First Run

On first run, you'll need to:

1. **Authenticate with YouTube**
   - A browser window will open
   - Login to your YouTube account
   - Grant permissions
   - Token will be saved for future use

2. **Test with Unlisted Upload**
   - First video uploads as "unlisted" (check config.yaml)
   - Verify video quality on YouTube
   - Change to "public" when ready

## Project Structure

```
youtube/
├── config/
│   ├── config.yaml          # Main configuration
│   ├── .env                 # API keys (create from .env.example)
│   └── .env.example         # Template
├── modules/
│   ├── story_generator.py   # AI story generation
│   ├── tts_generator.py     # Text-to-speech
│   ├── footage_manager.py   # Stock footage
│   ├── video_creator.py     # Video compilation
│   └── youtube_uploader.py  # YouTube upload
├── assets/
│   ├── footage/             # Downloaded videos
│   ├── audio/               # Generated voiceovers
│   └── output/              # Final videos
├── data/
│   └── video_history.json   # Upload tracking
├── main.py                  # Main automation script
├── scheduler.py             # Scheduling
├── requirements.txt
└── README.md
```

## Costs

- **OpenAI API**: ~$0.01-0.03 per video
- **Google Cloud TTS**: Free tier = 1M characters/month (~1000 videos)
- **YouTube API**: Free (quota limits apply)
- **Pexels API**: Free (unlimited)

**Estimated cost**: $0.01 per video (extremely affordable!)

## Troubleshooting

### ModuleNotFoundError

```bash
pip install -r requirements.txt
```

### Google Cloud Authentication Error

Make sure `GOOGLE_APPLICATION_CREDENTIALS` points to correct JSON file:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/full/path/to/credentials.json"
```

### YouTube Upload Quota Exceeded

YouTube limits daily uploads (usually 6-10 for new accounts):
- Wait 24 hours
- Reduce `max_videos_per_day` in config
- Request quota increase from Google

### Arabic Text Not Displaying

Install system Arabic fonts:
```bash
# macOS - fonts usually included
# Linux
sudo apt-get install fonts-arabic
```

### Video Processing Slow

- Reduce video resolution in config
- Use faster FFmpeg preset (in video_creator.py)
- Use shorter videos (30s instead of 60s)

## Tips

1. **Start with unlisted uploads** to verify quality
2. **Test different voice settings** to find best sound
3. **Monitor YouTube quotas** to avoid hitting limits
4. **Use cron/systemd** for production scheduling
5. **Backup your `.env` file** securely

## Customization

### Add Custom Background Music

1. Add nasheed MP3 files to `assets/music/`
2. Enable music in `config/config.yaml`:
   ```yaml
   music:
     enabled: true
     volume: 0.15
   ```
3. Update `video_creator.py` to use music files

### Change Subtitle Styling

Edit in `config/config.yaml`:
```yaml
subtitles:
  font_size: 60
  color: "white"
  position: "center"  # center, bottom, top
```

### Use Different AI Model

Edit `.env`:
```bash
OPENAI_MODEL=gpt-3.5-turbo  # Cheaper
# or
OPENAI_MODEL=gpt-4  # Better quality
```

## License

This project is for educational purposes. Ensure you comply with:
- YouTube Terms of Service
- API provider terms (OpenAI, Google, Pexels)
- Copyright laws in your jurisdiction

## Support

For issues or questions:
1. Check troubleshooting section
2. Review API documentation
3. Check module test outputs

## Credits

- **OpenAI GPT** - Story generation
- **Google Cloud** - Text-to-speech
- **Pexels** - Stock footage
- **MoviePy** - Video processing
- **YouTube API** - Upload functionality

---

**Ready to create amazing Islamic content! 🚀**
