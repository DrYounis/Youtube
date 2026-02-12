# GitHub Actions Setup Guide

How to use GitHub Actions to create videos automatically or manually from GitHub.

---

## Overview

Two GitHub Actions workflows have been set up:

1. **Manual Video Creation** - Create videos on-demand from GitHub
2. **Scheduled Videos** - Automatically create videos daily

---

## Setup: Add API Keys as GitHub Secrets

Before using the workflows, you need to add your API keys as GitHub Secrets.

### Step 1: Go to Repository Settings

1. Go to your repository: https://github.com/DrYounis/Youtube
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**

### Step 2: Add Each Secret

Add these secrets one by one:

| Secret Name | Value | Required |
|-------------|-------|----------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | ✅ Yes |
| `ANTHROPIC_MODEL` | `claude-3-haiku-20240307` | ✅ Yes |
| `ELEVENLABS_API_KEY` | Your ElevenLabs API key | ✅ Yes |
| `PEXELS_API_KEY` | Your Pexels API key | ✅ Yes |
| `YOUTUBE_CLIENT_SECRETS` | Your YouTube OAuth JSON (entire file content) | ⬜ Optional |

**For each secret:**
1. Click **New repository secret**
2. Enter the **Name** (exactly as shown above)
3. Paste the **Value**
4. Click **Add secret**

---

## Usage: Manual Video Creation

### Step 1: Go to Actions Tab

1. Go to: https://github.com/DrYounis/Youtube/actions
2. Click **Create Islamic Story Video** (left sidebar)
3. Click **Run workflow** (right side)

### Step 2: Configure Options

- **Story topic**: Choose topic or leave as "random"
  - prophets
  - sahaba
  - moral_lessons
  - quran_stories
  
- **Story theme** (optional): Enter a theme like "patience", "gratitude", "faith"

- **Upload to YouTube?**: 
  - ✅ Check to upload automatically (requires YouTube API setup)
  - ⬜ Leave unchecked to just create the video

### Step 3: Run and Download

1. Click **Run workflow**
2. Wait 2-3 minutes for completion
3. Click on the completed run
4. Scroll down to **Artifacts**
5. Download `islamic-story-video-XXX.zip`
6. Extract to get your video!

---

## Usage: Scheduled Videos

### Automatic Daily Creation

The workflow is configured to run daily at 9 AM UTC.

**To change the schedule:**

Edit `.github/workflows/scheduled-videos.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # Daily at 9 AM UTC
```

**Common schedules:**
- Daily at 6 AM: `0 6 * * *`
- Twice daily (9 AM & 6 PM): `0 9,18 * * *`
- Every 12 hours: `0 */12 * * *`
- Monday-Friday at 9 AM: `0 9 * * 1-5`

### Manual Trigger

You can also run it manually:

1. Go to **Actions** → **Scheduled Video Creation**
2. Click **Run workflow**
3. Enter **Number of videos to create** (1-3 recommended)
4. Click **Run workflow**

---

## Downloading Videos from GitHub Actions

After a workflow runs:

1. Go to the **Actions** tab
2. Click on the completed workflow run
3. Scroll to **Artifacts** section
4. Click to download the ZIP file
5. Extract to get:
   - `assets/output/*.mp4` - Your videos
   - `assets/audio/*.mp3` - Audio files

**Note**: Artifacts are kept for 7 days, then automatically deleted.

---

## Cost Considerations

### GitHub Actions Minutes

**Free tier:**
- 2,000 minutes/month for public repositories
- 500 minutes/month for private repositories

**Video creation time:**
- ~2-3 minutes per video
- You can create **~20-30 videos/month** on free tier

### API Costs

Same as local usage:
- **~$0.0003 per video**
- ElevenLabs free tier: 40 videos/month

---

## Advanced: Auto-Upload to YouTube

To enable automatic YouTube uploads from GitHub Actions:

### Step 1: Get YouTube OAuth Credentials

1. Go to: https://console.cloud.google.com/
2. Enable **YouTube Data API v3**
3. Create **OAuth 2.0 credentials**
4. Download `client_secrets.json`

### Step 2: Add as GitHub Secret

1. Open `client_secrets.json` in a text editor
2. Copy the **entire file content**
3. Go to repository **Settings** → **Secrets** → **Actions**
4. Create new secret:
   - Name: `YOUTUBE_CLIENT_SECRETS`
   - Value: Paste the entire JSON content
5. Click **Add secret**

### Step 3: Run Workflow with Upload

When running the manual workflow:
1. Check **"Upload to YouTube?"**
2. Run workflow
3. Videos will be uploaded automatically!

---

## Troubleshooting

### Workflow Fails: "Secret not found"

**Solution**: Make sure you added all required secrets in repository settings.

### Workflow Fails: "No module named..."

**Solution**: The `requirements.txt` might be missing dependencies. Check the error and add missing packages.

### Videos Not Creating

**Solution**: Check the workflow logs:
1. Go to failed workflow run
2. Click on the job
3. Expand each step to see error messages

### API Rate Limits Exceeded

**Solution**:
- ElevenLabs: Wait until next month or upgrade
- Pexels: Unlikely, but wait a few minutes
- Anthropic: Add billing or use a different model

---

## Tips & Best Practices

### 1. Test Locally First

Always test your changes locally before relying on GitHub Actions:
```bash
python3 main.py --dry-run
```

### 2. Monitor Your Usage

- **GitHub Actions**: Settings → Billing → Usage
- **ElevenLabs**: https://elevenlabs.io/usage
- **Anthropic**: https://console.anthropic.com/settings/usage

### 3. Don't Over-Schedule

Start with 1 video/day and increase gradually:
- Test quality first
- Monitor costs
- Check YouTube upload limits (50+ uploads/day may trigger review)

### 4. Download Artifacts Promptly

Artifacts are deleted after 7 days. Download videos you want to keep!

### 5. Keep Secrets Secure

- Never commit `.env` or credential files
- Only add secrets through GitHub Settings
- Rotate API keys if compromised

---

## Example: Complete Workflow

**Goal**: Create 3 Islamic story videos daily and download them

1. **Setup** (one-time):
   - Add all API keys as GitHub Secrets
   - Configure schedule in `scheduled-videos.yml`

2. **Daily** (automatic):
   - Workflow runs at 9 AM UTC
   - Creates 3 videos automatically
   - Stores as artifacts

3. **Weekly** (manual):
   - Go to Actions tab
   - Download the artifacts
   - Extract videos
   - Upload best ones to YouTube manually

---

## Disabling Workflows

To temporarily disable a workflow:

1. Go to **Actions** tab
2. Click on the workflow name (left sidebar)
3. Click **⋯** (three dots, top right)
4. Click **Disable workflow**

To re-enable, follow the same steps and click **Enable workflow**.

---

## Next Steps

1. ✅ Add API keys as GitHub Secrets
2. ✅ Test manual workflow creation
3. ✅ Download and review the video
4. ✅ Adjust schedule if needed
5. ⬜ Setup YouTube auto-upload (optional)
6. ⬜ Create more videos!

**You're ready to create Islamic story videos from anywhere! 🚀**
