# YouTube API Setup Guide - Step by Step

Complete guide to set up YouTube Data API for automatic video uploads.

---

## Overview

To upload videos automatically to YouTube, you need:
1. Google Cloud Project
2. YouTube Data API v3 enabled
3. OAuth 2.0 credentials
4. Token authentication (one-time setup)

**Time required**: ~10 minutes

---

## Step 1: Create Google Cloud Project

### 1.1 Go to Google Cloud Console

👉 https://console.cloud.google.com/

### 1.2 Create New Project

1. Click the project dropdown (top left, next to "Google Cloud")
2. Click **"NEW PROJECT"**
3. Project name: `YouTube Islamic Stories` (or any name)
4. Organization: Leave as default or select if you have one
5. Click **"CREATE"**
6. Wait for the project to be created (~30 seconds)

**Note**: If you're in Saudi Arabia and see CNTXT portal, you can still use this for YouTube API (it's different from Text-to-Speech).

---

## Step 2: Enable YouTube Data API v3

### 2.1 Go to API Library

1. Make sure your new project is selected (check top left)
2. Click **hamburger menu (☰)** → **"APIs & Services"** → **"Library"**
3. Or direct link: https://console.cloud.google.com/apis/library

### 2.2 Search and Enable

1. Search for: **"YouTube Data API v3"**
2. Click on **"YouTube Data API v3"**
3. Click **"ENABLE"**
4. Wait for it to enable (~10 seconds)

---

## Step 3: Configure OAuth Consent Screen

### 3.1 Go to OAuth Consent Screen

1. Click **hamburger menu (☰)** → **"APIs & Services"** → **"OAuth consent screen"**
2. Or direct link: https://console.cloud.google.com/apis/credentials/consent

### 3.2 Choose User Type

- Select **"External"**
- Click **"CREATE"**

### 3.3 Fill in App Information

**App information:**
- App name: `Islamic Stories Uploader`
- User support email: Your email
- App logo: Skip (optional)

**App domain (all optional - skip these):**
- Application home page: Leave empty
- Application privacy policy link: Leave empty
- Application terms of service link: Leave empty

**Developer contact information:**
- Email addresses: Your email

Click **"SAVE AND CONTINUE"**

### 3.4 Scopes

1. Click **"ADD OR REMOVE SCOPES"**
2. Scroll down and check:
   - ✅ **`https://www.googleapis.com/auth/youtube.upload`**
   - ✅ **`https://www.googleapis.com/auth/youtube`**
3. Click **"UPDATE"**
4. Click **"SAVE AND CONTINUE"**

### 3.5 Test Users

1. Click **"ADD USERS"**
2. Add your Gmail/YouTube email address
3. Click **"ADD"**
4. Click **"SAVE AND CONTINUE"**

### 3.6 Summary

- Review and click **"BACK TO DASHBOARD"**

---

## Step 4: Create OAuth 2.0 Credentials

### 4.1 Go to Credentials

1. Click **hamburger menu (☰)** → **"APIs & Services"** → **"Credentials"**
2. Or direct link: https://console.cloud.google.com/apis/credentials

### 4.2 Create Credentials

1. Click **"+ CREATE CREDENTIALS"** (top)
2. Select **"OAuth client ID"**

### 4.3 Configure OAuth Client

**Application type:**
- Select **"Desktop app"**

**Name:**
- Enter: `YouTube Uploader Desktop`

Click **"CREATE"**

### 4.4 Download Credentials

1. A popup will show your **Client ID** and **Client secret**
2. Click **"DOWNLOAD JSON"**
3. Save the file as: `client_secrets.json`

**Keep this file safe!** You'll need it in the next step.

---

## Step 5: Add Credentials to Your Project

### 5.1 Copy JSON File

Copy the downloaded `client_secrets.json` to your project:

```bash
cp ~/Downloads/client_secret_*.json /Volumes/Samsung/youtube/config/youtube-client-secrets.json
```

**Or manually:**
1. Find the downloaded file (usually in Downloads)
2. Rename it to: `youtube-client-secrets.json`
3. Move it to: `/Volumes/Samsung/youtube/config/`

### 5.2 Update .env File

Edit `/Volumes/Samsung/youtube/config/.env`:

```bash
# YouTube Data API v3
YOUTUBE_CLIENT_SECRETS=/Volumes/Samsung/youtube/config/youtube-client-secrets.json
```

**Verify the path is correct!**

---

## Step 6: Test YouTube Upload (First-Time Authentication)

### 6.1 Run Test Upload

```bash
cd /Volumes/Samsung/youtube
python3 -c "from modules.youtube_uploader import YouTubeUploader; uploader = YouTubeUploader(); uploader.authenticate()"
```

### 6.2 Complete Browser Authentication

1. A browser window will open
2. **Sign in** with your YouTube/Gmail account
3. You'll see: **"Google hasn't verified this app"**
4. Click **"Advanced"** → **"Go to Islamic Stories Uploader (unsafe)"**
5. Click **"Continue"**
6. Select your YouTube channel (if you have multiple)
7. Click **"Allow"**
8. Grant permissions:
   - ✅ Manage your YouTube videos
   - ✅ Upload YouTube videos
9. Click **"Continue"**

### 6.3 Verify Success

You should see in terminal:
```
✅ Authentication successful!
Token saved to: config/youtube_token.json
```

**Important**: The file `config/youtube_token.json` is created. This allows automatic uploads without browser login each time.

---

## Step 7: Test Actual Upload

### 7.1 Create a Test Video

```bash
cd /Volumes/Samsung/youtube
python3 main.py --dry-run
```

This creates a video without uploading.

### 7.2 Upload the Video

```bash
python3 main.py
```

**No `--dry-run` flag = uploads to YouTube!**

### 7.3 Check YouTube Studio

1. Go to: https://studio.youtube.com/
2. Click **"Content"** (left sidebar)
3. Your video should be there! 🎉

**Default privacy**: "Unlisted" (check `config/config.yaml`)

---

## Step 8: Configure for Automation

### 8.1 Update Config for Auto-Upload

Edit `/Volumes/Samsung/youtube/config/config.yaml`:

```yaml
youtube:
  privacy_status: "public"  # Change from "unlisted" to "public"
  notify_subscribers: true  # Notify subscribers on upload
  made_for_kids: false
```

### 8.2 Add YouTube Secrets to GitHub

For GitHub Actions automation:

1. Go to: https://github.com/DrYounis/Youtube/settings/secrets/actions
2. Click **"New repository secret"**
3. Add **two** secrets:

**Secret 1: YOUTUBE_CLIENT_SECRETS**
- Name: `YOUTUBE_CLIENT_SECRETS`
- Value: Copy the **entire content** of `youtube-client-secrets.json`
  ```bash
  cat /Volumes/Samsung/youtube/config/youtube-client-secrets.json
  ```
- Paste all the JSON content
- Click **"Add secret"**

**Secret 2: YOUTUBE_TOKEN**
- Name: `YOUTUBE_TOKEN`
- Value: Copy the **entire content** of `youtube_token.json`
  ```bash
  cat /Volumes/Samsung/youtube/config/youtube_token.json
  ```
- Paste all the JSON content
- Click **"Add secret"**

---

## Step 9: Enable Scheduled Daily Uploads

### 9.1 Update Scheduled Workflow

The workflow is already set up in `.github/workflows/scheduled-videos.yml`.

**To enable uploads**, update the workflow:

Edit `.github/workflows/scheduled-videos.yml`, line ~45:

**Change from:**
```yaml
python3 main.py --dry-run
```

**To:**
```yaml
python3 main.py  # Remove --dry-run to enable uploads
```

### 9.2 Set Your Schedule

Default is 9 AM UTC daily. To change, edit the cron schedule:

```yaml
schedule:
  - cron: '0 6 * * *'  # 6 AM UTC = 9 AM Saudi Arabia
```

**Common schedules:**
- 9 AM Saudi Time: `0 6 * * *` (6 AM UTC)
- 12 PM Saudi Time: `0 9 * * *` (9 AM UTC)
- 6 PM Saudi Time: `0 15 * * *` (3 PM UTC)

### 9.3 Commit and Push

```bash
git add .github/workflows/scheduled-videos.yml
git commit -m "Enable automatic daily YouTube uploads"
git push origin main
```

---

## Verification Checklist

Before going fully automatic, verify:

- ✅ YouTube Data API v3 is enabled
- ✅ OAuth credentials downloaded
- ✅ `youtube-client-secrets.json` in `config/` folder
- ✅ First-time authentication completed
- ✅ `youtube_token.json` created in `config/` folder
- ✅ Test upload works (`python3 main.py`)
- ✅ Video appears in YouTube Studio
- ✅ Both secrets added to GitHub
- ✅ Workflow updated to remove `--dry-run`
- ✅ Schedule set to desired time

---

## Troubleshooting

### Error: "Invalid client secrets file"

**Solution:**
- Make sure you downloaded the correct JSON file
- Check the file path in `.env` is correct
- Verify the file is valid JSON (open in text editor)

### Error: "Access blocked: This app's request is invalid"

**Solution:**
- Make sure you added your email as a test user in OAuth consent screen
- Sign in with the same email you added as test user

### Error: "The request cannot be completed because you have exceeded your quota"

**Solution:**
- YouTube API has daily quotas (10,000 units/day)
- Each upload costs ~1,600 units
- You can upload ~6 videos/day on free quota
- For more, apply for quota increase: https://support.google.com/youtube/contact/yt_api_form

### Token Expired

**Solution:**
- Delete `config/youtube_token.json`
- Run the authentication again:
  ```bash
  python3 -c "from modules.youtube_uploader import YouTubeUploader; uploader = YouTubeUploader(); uploader.authenticate()"
  ```

---

## YouTube Upload Quotas & Limits

### Daily Quota

**Free tier**: 10,000 units/day

**Cost per video upload**:
- Upload: ~1,600 units
- With metadata: ~50 units
- Total: ~1,650 units per video

**Max videos/day**: ~6 videos

### Rate Limits

- Max 6 uploads per day (recommended: 1-3)
- If you exceed, wait 24 hours for quota reset

### Quota Increase

To upload more videos:
1. Go to: https://console.cloud.google.com/iam-admin/quotas
2. Search: "YouTube Data API v3"
3. Click "Queries per day"
4. Click "EDIT QUOTAS"
5. Request increase
6. Fill in justification (educational Islamic content)
7. Wait for approval (~1-2 days)

---

## Security Best Practices

1. **Never commit credentials**:
   - `youtube-client-secrets.json` ✅ Already in `.gitignore`
   - `youtube_token.json` ✅ Already in `.gitignore`

2. **Keep secrets secure**:
   - Only add to GitHub Secrets (never commit)
   - Rotate if compromised

3. **Monitor your channel**:
   - Check YouTube Studio daily
   - Review uploaded videos
   - Monitor comments

4. **Backup tokens**:
   - Keep a copy of `youtube_token.json` somewhere safe
   - If lost, re-authenticate

---

## Summary

✅ **Setup Complete!**

You can now:
- Upload videos automatically to YouTube
- Schedule daily uploads via GitHub Actions
- Monitor uploads in YouTube Studio

**Cost**: FREE (within YouTube API quotas)

**Next**: Let the automation run and grow your channel! 🚀
