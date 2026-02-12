# Google Cloud Text-to-Speech Setup Guide

Complete step-by-step instructions for setting up Google Cloud Text-to-Speech API for the YouTube automation system.

---

## Overview

Google Cloud Text-to-Speech provides natural Arabic voiceovers for your videos. It's free for up to 1 million characters per month (~1000 videos).

---

## Step 1: Create Google Cloud Account

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Click "Get started for free" or "Sign in"

2. **Sign in with Google Account**
   - Use your existing Google/Gmail account
   - Or create a new one

3. **Agree to Terms**
   - Accept Google Cloud Terms of Service
   - Skip the free trial setup for now (optional)

---

## Step 2: Create a New Project

1. **Click on Project Selector**
   - Look for the dropdown at the top of the page
   - It might say "Select a project" or show an existing project name

2. **Create New Project**
   - Click "NEW PROJECT"
   - Enter project name: `youtube-automation` (or any name you prefer)
   - Leave organization as "No organization" (unless you have one)
   - Click **CREATE**

3. **Wait for Project Creation**
   - Takes 10-30 seconds
   - You'll see a notification when ready

4. **Select Your Project**
   - Make sure your new project is selected in the dropdown at the top

---

## Step 3: Enable Text-to-Speech API

1. **Open API Library**
   - In the left sidebar, click **APIs & Services** → **Library**
   - Or search "API Library" in the search bar at the top

2. **Search for Text-to-Speech**
   - In the search box, type: `text to speech`
   - Click on **"Cloud Text-to-Speech API"**

3. **Enable the API**
   - Click the blue **ENABLE** button
   - Wait for it to enable (takes a few seconds)
   - You'll see "API enabled" notification

---

## Step 4: Create Service Account

1. **Go to Service Accounts**
   - Left sidebar: **IAM & Admin** → **Service Accounts**
   - Or search "Service Accounts" at the top

2. **Create Service Account**
   - Click **+ CREATE SERVICE ACCOUNT** at the top

3. **Enter Service Account Details**
   - **Service account name**: `youtube-tts-service`
   - **Service account ID**: Auto-filled (e.g., `youtube-tts-service`)
   - **Description**: `Service account for YouTube automation TTS` (optional)
   - Click **CREATE AND CONTINUE**

4. **Grant Permissions**
   - **Select a role**: Click the dropdown
   - Search for: `Cloud Text-to-Speech`
   - Select: **Cloud Text-to-Speech User**
   - Click **CONTINUE**

5. **Skip Optional Steps**
   - Click **DONE** (skip "Grant users access" section)

---

## Step 5: Create and Download JSON Key

1. **Find Your Service Account**
   - You should see your new service account in the list
   - Email format: `youtube-tts-service@project-name.iam.gserviceaccount.com`

2. **Create Key**
   - Click on your service account email to open details
   - Go to the **KEYS** tab at the top
   - Click **ADD KEY** → **Create new key**

3. **Select JSON Format**
   - Choose **JSON** (should be selected by default)
   - Click **CREATE**

4. **Download Key**
   - A JSON file will automatically download
   - **IMPORTANT**: Save this file securely
   - Example filename: `youtube-automation-1234567890ab.json`
   - **DO NOT share this file or commit it to GitHub**

5. **Move Key to Safe Location**
   ```bash
   # Example: Move to your project's config folder
   mv ~/Downloads/youtube-automation-*.json /Volumes/Samsung/youtube/config/google-tts-credentials.json
   ```

---

## Step 6: Configure Environment Variables

1. **Open your `.env` file**
   ```bash
   cd /Volumes/Samsung/youtube
   nano config/.env
   ```

2. **Add the credentials path**
   ```bash
   # Google Cloud Text-to-Speech
   GOOGLE_APPLICATION_CREDENTIALS=/Volumes/Samsung/youtube/config/google-tts-credentials.json
   ```

3. **Save and exit**
   - Press `Ctrl + X`
   - Press `Y` to confirm
   - Press `Enter` to save

---

## Step 7: Test the Setup

1. **Run the TTS test**
   ```bash
   cd /Volumes/Samsung/youtube
   python modules/tts_generator.py
   ```

2. **Expected Output**
   ```
   Testing Text-to-Speech Generator...
   --------------------------------------------------

   🎤 Available Arabic Voices:
   1. ar-XA-Wavenet-A (FEMALE)
   2. ar-XA-Wavenet-B (MALE)
   3. ar-XA-Wavenet-C (MALE)
   4. ar-XA-Wavenet-D (FEMALE)

   🎙️  Generating test voiceover...
   Text: بسم الله الرحمن الرحيم...

   ✅ Voiceover Generated Successfully!
   📁 Audio Path: assets/audio/test_voiceover.mp3
   ⏱️  Estimated Duration: 15.2s
   📊 Character Count: 243
   🎤 Voice: ar-XA-Wavenet-B
   🔊 Speaking Rate: 0.95
   💾 File Size: 24.3 KB

   ==================================================
   Test Complete!
   ```

3. **Listen to Test Audio**
   - Check `assets/audio/test_voiceover.mp3`
   - Verify it's in Arabic with proper pronunciation

---

## Troubleshooting

### Error: "Could not automatically determine credentials"

**Problem**: Google Cloud credentials not found

**Solution**:
```bash
# Make sure the path is correct and absolute
echo $GOOGLE_APPLICATION_CREDENTIALS

# Should output: /Volumes/Samsung/youtube/config/google-tts-credentials.json

# If not set, export it manually:
export GOOGLE_APPLICATION_CREDENTIALS="/Volumes/Samsung/youtube/config/google-tts-credentials.json"
```

### Error: "Permission denied" on credentials file

**Problem**: File permissions are wrong

**Solution**:
```bash
chmod 600 /Volumes/Samsung/youtube/config/google-tts-credentials.json
```

### Error: "API has not been used in project"

**Problem**: Text-to-Speech API not enabled

**Solution**:
- Go back to Step 3 and enable the API
- Wait 5-10 minutes for the API to fully activate
- Try again

### Error: "The caller does not have permission"

**Problem**: Service account doesn't have the right role

**Solution**:
1. Go to **IAM & Admin** → **IAM**
2. Find your service account email
3. Click edit (pencil icon)
4. Add role: **Cloud Text-to-Speech User**
5. Click **SAVE**

### No audio file generated

**Problem**: Various issues

**Solutions**:
1. Check if `assets/audio/` directory exists
2. Verify credentials file path is correct
3. Check internet connection
4. Verify Google Cloud billing is set up (if outside free tier)

---

## Important Notes

### Free Tier Limits

- **1 million characters per month = FREE**
- Average story: ~250 characters
- **You can create ~4,000 videos/month for free!**

### Billing

- You need to set up billing account (even for free tier)
- No charges unless you exceed free tier
- To set up billing:
  1. Go to **Billing** in left sidebar
  2. Click **LINK A BILLING ACCOUNT**
  3. Follow the prompts to add payment method
  4. Your card won't be charged unless you exceed limits

### Security Best Practices

1. **Never commit credentials to GitHub**
   - The `.gitignore` file already excludes `*.json` in config folder
   - Double-check before pushing code

2. **Restrict API key if needed**
   - Go to **APIs & Services** → **Credentials**
   - Click on your service account
   - Set API restrictions if desired

3. **Regularly rotate keys**
   - Delete old keys you're not using
   - Create new ones periodically

---

## Voice Options

### Available Arabic Voices

All voices support Arabic (ar-XA):

| Voice Name | Gender | Quality | Best For |
|------------|--------|---------|----------|
| ar-XA-Wavenet-A | Female | High | Formal stories |
| ar-XA-Wavenet-B | Male | High | **Default - Recommended** |
| ar-XA-Wavenet-C | Male | High | Deep, authoritative |
| ar-XA-Wavenet-D | Female | High | Gentle, narrative |

### Changing Voice

Edit `config/config.yaml`:
```yaml
tts:
  google:
    voice_name: "ar-XA-Wavenet-A"  # Change to desired voice
    speaking_rate: 0.95             # Speed (0.25-4.0)
    pitch: 0.0                      # Pitch (-20.0 to 20.0)
```

---

## Next Steps

Once setup is complete:

1. ✅ Test passes → Continue with YouTube API setup
2. ❌ Test fails → Review troubleshooting section above
3. Test different voices to find your preferred one
4. Adjust speaking rate if needed (0.9 = slower, 1.1 = faster)

---

## Quick Reference

**Console URL**: https://console.cloud.google.com/

**Key Locations**:
- API Library: Console → APIs & Services → Library
- Service Accounts: Console → IAM & Admin → Service Accounts
- Billing: Console → Billing

**Test Command**:
```bash
python modules/tts_generator.py
```

**Credentials Path**:
```bash
/Volumes/Samsung/youtube/config/google-tts-credentials.json
```

---

**You're all set! 🎉**

Your system can now generate natural Arabic voiceovers for your Islamic stories.
