# ElevenLabs Setup Guide - Step by Step

Complete instructions for setting up ElevenLabs Text-to-Speech for Arabic voiceovers.

---

## Why ElevenLabs?

✅ **Very natural Arabic pronunciation**  
✅ **Simple setup** - Just one API key  
✅ **Free tier** - 10,000 characters/month (~40 videos)  
✅ **No billing account required**  
✅ **Works globally** - No regional restrictions  

---

## Step 1: Create ElevenLabs Account

1. **Go to ElevenLabs website:**
   👉 https://elevenlabs.io/

2. **Click "Get Started Free"** or "Sign Up"

3. **Sign up with:**
   - Google account (recommended - quick!)
   - OR Email + Password

4. **Verify your email** if you signed up with email

---

## Step 2: Get Your API Key

1. **After logging in, click your profile icon** (top right)

2. **Click "Profile"** or "Settings"

3. **Go to "API Keys" section**

4. **Click "Create API Key"** or use the default key shown

5. **Copy your API key**
   - Format: `sk_...` (long string)
   - Click the copy icon
   - **Save it securely!**

---

## Step 3: Add API Key to Your Project

1. **Open your `.env` file:**
   ```bash
   cd /Volumes/Samsung/youtube
   nano config/.env
   ```

2. **Add your ElevenLabs API key:**
   ```bash
   # ElevenLabs API Key
   ELEVENLABS_API_KEY=sk_your_actual_api_key_here
   ```

3. **Save and exit:**
   - Press `Ctrl + X`
   - Press `Y` to confirm
   - Press `Enter`

---

## Step 4: Verify Configuration

The system is already configured to use ElevenLabs!

**Check `config/config.yaml`:**
```yaml
tts:
  provider: "elevenlabs"  # ✅ Already set!
```

---

## Step 5: Test It!

Run the test to verify everything works:

```bash
cd /Volumes/Samsung/youtube
python3 modules/tts_generator.py
```

**Expected output:**
```
Testing Text-to-Speech Generator...
--------------------------------------------------

🎤 Using Provider: ELEVENLABS

📋 Available Voices:
1. Adam - Deep and resonant
2. Antoni - Well-rounded
3. Arnold - Crisp and articulate
4. Bella - Soft and pleasant
5. Rachel - Calm and composed

🎙️  Generating test voiceover...

✅ Voiceover Generated Successfully!
📁 Audio Path: assets/audio/test_voiceover.mp3
⏱️  Estimated Duration: 15.2s
📊 Character Count: 243
🎤 Voice ID: pNInz6obpgDQGcFmaJgB
🤖 Model: eleven_multilingual_v2
💾 File Size: 42.3 KB
```

---

## Available Arabic Voices

ElevenLabs offers several voices that work well with Arabic:

| Voice Name | Voice ID | Best For |
|------------|----------|----------|
| **Adam** (Default) | `pNInz6obpgDQGcFmaJgB` | Deep, resonant - great for stories |
| Antoni | `ErXwobaYiN019PkySvjV` | Pleasant, versatile |
| Arnold | `VR6AewLTigWG4xSOukaG` | Clear, authoritative |
| Callum | `N2lVS1w4EtoT3dr4eOWO` | Calm, professional |

### To Change Voice:

Edit `config/config.yaml`:
```yaml
elevenlabs:
  voice_id: "ErXwobaYiN019PkySvjV"  # Antoni
```

---

## Free Tier Limits

**Free Plan:**
- ✅ 10,000 characters per month
- ✅ That's approximately **40 videos** (250 chars each)
- ✅ All voices available
- ✅ Commercial use allowed

**Paid Plans** (if you need more):
- **Starter**: $5/month - 30,000 characters (~120 videos)
- **Creator**: $22/month - 100,000 characters (~400 videos)
- **Pro**: $99/month - 500,000 characters (~2,000 videos)

---

##Troubleshooting

### Error: "ELEVENLABS_API_KEY not found"

**Solution:**
```bash
# Make sure you added it to .env file
cat config/.env | grep ELEVENLABS

# Should output: ELEVENLABS_API_KEY=sk_...
# If not, add it to config/.env
```

### Error: "Invalid API key"

**Solutions:**
1. Check you copied the full key (starts with `sk_`)
2. No quotes around the key in `.env`
3. No spaces before or after the `=`
4. Try regenerating the key on ElevenLabs website

### Error: "Quota exceeded"

**Solution:**
- You've used your 10,000 free characters for the month
- Wait until next month
- OR upgrade to a paid plan at https://elevenlabs.io/pricing

### Audio sounds robotic

**Solution:**
Adjust voice settings in `config/config.yaml`:
```yaml
elevenlabs:
  stability: 0.7        # Higher = more consistent (0.5-0.8)
  similarity_boost: 0.8  # Higher = clearer (0.7-0.9)
```

---

## Voice Settings Explained

### Stability (0.0 - 1.0)
- **Low (0.3-0.5)**: More expressive, varied
- **Medium (0.5-0.7)**: Balanced (recommended)
- **High (0.7-1.0)**: More consistent, stable

### Similarity Boost (0.0 - 1.0)
- **Low (0.5-0.7)**: More creative interpretation
- **Medium (0.7-0.8)**: Balanced (recommended)
- **High (0.8-1.0)**: Closer to original voice

---

## Next Steps

Once ElevenLabs is working:

1. ✅ **Test with Arabic text** - Run the test
2. ✅ **Try different voices** - Find your favorite
3. ✅ **Adjust settings** - Fine-tune stability/clarity
4. ✅ **Create your first video** - Run `python3 main.py`

---

## Comparison: ElevenLabs vs Google Cloud

| Feature | ElevenLabs | Google Cloud |
|---------|-----------|--------------|
| Setup | ⭐⭐⭐⭐⭐ Easy | ⭐⭐ Complex |
| Arabic Quality | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good |
| Free Tier | 10K chars/month | 1M chars/month |
| Billing Required | ❌ No | ✅ Yes |
| Regional Restrictions | ❌ None | ✅ Saudi Arabia requires CNTXT |

---

**You're all set! 🎉**

ElevenLabs is ready to generate beautiful Arabic voiceovers for your Islamic stories.
