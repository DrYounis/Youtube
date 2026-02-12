# Eleven Labs Setup - Quick Start

Follow these steps to get your ElevenLabs API key and start generating Arabic voiceovers:

## Step 1: Create Account
1. Go to: https://elevenlabs.io/
2. Click "Get Started Free"
3. Sign up with Google (easiest) or email

## Step 2: Get API Key
1. After login, click your profile icon (top right)
2. Click "Profile" → "API Keys"
3. Copy your API key (starts with `sk_`)

## Step 3: Add to .env
Open `/Volumes/Samsung/youtube/config/.env` and add:
```
ELEVENLABS_API_KEY=sk_your_actual_key_here
```

## Step 4: Test
```bash
cd /Volumes/Samsung/youtube
python3 modules/tts_generator.py
```

## Done! ✅
Your system is already configured to use ElevenLabs (check `config/config.yaml`).

---

**Free Tier**: 10,000 characters/month (~40 videos)  
**Paid**: $5/month for 30,000 characters (~120 videos)

For detailed instructions, see: `docs/elevenlabs-setup.md`
