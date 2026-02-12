# Quick Start: Automated Daily YouTube Uploads

Get your system uploading 1 Islamic story video per day automatically!

---

## Prerequisites

✅ You've already completed:
- System setup (API keys configured)
- First video created successfully
- Code pushed to GitHub

---

## Setup Steps (15 minutes)

### Step 1: Get YouTube API Credentials

**Follow the detailed guide**: `docs/youtube-api-setup.md`

**Quick summary**:
1. Go to https://console.cloud.google.com/
2. Create project
3. Enable "YouTube Data API v3"
4. Create OAuth credentials
5. Download `client_secrets.json`

### Step 2: Authenticate Locally (One-Time)

```bash
# 1. Copy credentials to project
cp ~/Downloads/client_secret_*.json /Volumes/Samsung/youtube/config/youtube-client-secrets.json

# 2. Update .env
echo "YOUTUBE_CLIENT_SECRETS=/Volumes/Samsung/youtube/config/youtube-client-secrets.json" >> /Volumes/Samsung/youtube/config/.env

# 3. Run first-time authentication
cd /Volumes/Samsung/youtube
python3 -c "from modules.youtube_uploader import YouTubeUploader; uploader = YouTubeUploader(); uploader.authenticate()"
```

**What happens:**
- Browser opens
- Sign in with your YouTube account
- Grant permissions
- Token saved to `config/youtube_token.json`

### Step 3: Test Local Upload

```bash
# Create and upload a video
python3 main.py
```

**Check**: Go to https://studio.youtube.com/ - video should be there!

### Step 4: Add Secrets to GitHub

Go to: https://github.com/DrYounis/Youtube/settings/secrets/actions

Add **3 new secrets**:

**1. YOUTUBE_CLIENT_SECRETS**
```bash
# Copy the content
cat /Volumes/Samsung/youtube/config/youtube-client-secrets.json
```
- Click "New repository secret"
- Name: `YOUTUBE_CLIENT_SECRETS`
- Value: Paste the entire JSON
- Click "Add secret"

**2. YOUTUBE_TOKEN**
```bash
# Copy the content
cat /Volumes/Samsung/youtube/config/youtube_token.json
```
- Click "New repository secret"
- Name: `YOUTUBE_TOKEN`
- Value: Paste the entire JSON
- Click "Add secret"

**3. Verify all secrets:**

You should now have:
- ✅ ANTHROPIC_API_KEY
- ✅ ANTHROPIC_MODEL  
- ✅ ELEVENLABS_API_KEY
- ✅ PEXELS_API_KEY
- ✅ YOUTUBE_CLIENT_SECRETS
- ✅ YOUTUBE_TOKEN

### Step 5: Configure Upload Settings

Edit `config/config.yaml`:

```yaml
youtube:
  privacy_status: "public"  # or "unlisted" or "private"
  notify_subscribers: true   # Notify on new upload
  made_for_kids: false
```

Commit changes:
```bash
git add config/config.yaml
git commit -m "Configure YouTube upload settings for public videos"
git push origin main
```

### Step 6: Verify Everything

**Check the GitHub Actions workflow** is ready:
1. Go to https://github.com/DrYounis/Youtube/actions
2. Click "Scheduled Video Creation"
3. The workflow is set to run daily at **9 AM Saudi Arabia time**

---

## 🎉 Done! Your System is Now Automated

### What Happens Now:

**Every day at 9 AM Saudi time:**
1. GitHub Actions automatically runs
2. Creates 1 new  Islamic story video:
   - Generates Arabic story with AI
   - Creates voiceover with ElevenLabs
   - Downloads Islamic/nature footage
   - Compiles video
3. **Uploads to your YouTube channel**
4. Stores video as downloadable artifact (backup)

### Manual Trigger

You can also trigger manually:

1. Go to https://github.com/DrYounis/Youtube/actions
2. Click "Scheduled Video Creation"
3. Click "Run workflow"
4. Enter number of videos (default: 1)
5. Click "Run workflow"

---

## Monitoring

### Check Uploads

**YouTube Studio**: https://studio.youtube.com/
- Videos appear in "Content"
- Check views, comments, etc.

**GitHub Actions**: https://github.com/DrYounis/Youtube/actions
- See workflow runs
- Download videos from Artifacts
- Check logs if errors occur

### Costs

**Per video**: ~$0.0003
**Per month (30 videos)**: ~$0.01
**YouTube API**: FREE (within quota: 6 videos/day max)

---

## Troubleshooting

### Workflow runs but doesn't upload

**Check**: Do you have `YOUTUBE_TOKEN` secret added to GitHub?

**Solution**: Add it following Step 4 above

### Video uploaded as "Unlisted"

**Update** `config/config.yaml`:
```yaml
youtube:
  privacy_status: "public"
```

### "Quota exceeded" error

**Cause**: YouTube API allows ~6 uploads/day

**Solution**: 
- Wait 24 hours for quota reset
- Or request quota increase: https://console.cloud.google.com/iam-admin/quotas

### Token expired

**Solution**: Re-run authentication locally:
```bash
cd /Volumes/Samsung/youtube
python3 -c "from modules.youtube_uploader import YouTubeUploader; uploader = YouTubeUploader(); uploader.authenticate()"

# Update GitHub secret with new token
cat config/youtube_token.json
# Copy and update YOUTUBE_TOKEN secret
```

---

## Growth Tips

### 1. Optimize Metadata

Edit `config/config.yaml`:
```yaml
youtube:
  title_template: "{story_title} | قصة إسلامية #shorts"
  tags:
    - "Islamic stories"
    - "قصص إسلامية"
    - "Shorts"
    - # Add popular tags
```

### 2. Post Consistently

Stick to 1 video/day:
- Builds audience expectation
- Better for algorithm
- Sustainable long-term

### 3. Monitor Performance

- Check YouTube Analytics weekly
- See which topics perform best
- Adjust story topics in config

### 4. Engage with Audience

- Reply to comments
- Use community tab
- Ask for story suggestions

---

## Next Level Features

### Multiple Videos Per Day

Edit `.github/workflows/scheduled-videos.yml`:

Change line ~42:
```yaml
COUNT=3  # Instead of COUNT=1
```

**Warning**: Max 6/day due to YouTube API limits

### Add Thumbnails

1. Generate custom thumbnails
2. Add to upload metadata
3. Update `modules/youtube_uploader.py`

### Add Chapters/Timestamps

Update video description template to include timestamps

---

## Summary

✅ **Setup Complete!**

Your channel now:
- Automatically creates 1 video/day
- Uploads to YouTube at 9 AM Saudi time
- Costs ~$0.01/month
- Runs entirely on GitHub (no local machine needed)

**Just monitor and enjoy the growth! 🚀**

---

## Support

**Issues?** Check:
1. `docs/youtube-api-setup.md` - Detailed setup
2. GitHub Actions logs - Error messages
3. YouTube Studio - Upload status

**Everything working?** 
- Sit back and let it run!
- Check weekly for performance
- Engage with your growing audience

🎉 **Happy automating!**
