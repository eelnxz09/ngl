# 🚀 Deployment Guide - DocAuthAI

This guide provides step-by-step instructions for deploying the Document Authenticity Scanner to production.

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Deployment (Render)](#backend-deployment-render)
3. [Alternative Backend Hosts](#alternative-backend-hosts)
4. [Frontend Deployment (GitHub Pages)](#frontend-deployment-github-pages)
5. [Connecting Frontend to Backend](#connecting-frontend-to-backend)
6. [Custom Domain Setup](#custom-domain-setup)
7. [Environment Variables](#environment-variables)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ GitHub account
- ✅ Git installed locally
- ✅ Code editor (VS Code recommended)
- ✅ Python 3.9+ installed (for local testing)
- ✅ Basic command line knowledge

---

## Backend Deployment (Render)

Render offers a free tier perfect for this project with automatic builds and deployments.

### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended for easy integration)
3. Verify your email

### Step 2: Push Code to GitHub

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - DocAuthAI"

# Create repository on GitHub
# Then add remote and push
git remote add origin https://github.com/yourusername/doc-scanner.git
git push -u origin main
```

### Step 3: Create New Web Service on Render

1. **Dashboard** → Click **"New +"** → Select **"Web Service"**

2. **Connect Repository:**
   - Click **"Connect GitHub"**
   - Authorize Render to access your repositories
   - Select `doc-scanner` repository

3. **Configure Service:**

   ```
   Name:               doc-scanner-api
   Region:             Oregon (US West) or closest to your users
   Branch:             main
   Root Directory:     backend
   Runtime:            Python 3
   Build Command:      pip install -r requirements.txt
   Start Command:      uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Plan:**
   - Select **"Free"** tier (sufficient for most use cases)
   - Free tier limitations:
     - Spins down after 15 minutes of inactivity
     - First request after spin-down takes ~30 seconds
     - 750 hours/month free (plenty for development/portfolio)

5. **Environment Variables:**
   - None required for basic setup
   - Add later if implementing SynthID or authentication

6. **Click "Create Web Service"**

### Step 4: Monitor Deployment

1. Watch the **Logs** tab for build progress
2. Wait for "Deploy live" message (usually 2-5 minutes)
3. Your API will be available at: `https://doc-scanner-api.onrender.com`

### Step 5: Verify Backend

Test the health endpoint:
```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-02-11T12:00:00",
  "analyzer_ready": true,
  "supported_formats": ["PDF", "JPG", "PNG", "WEBP"],
  "synthid_available": false
}
```

---

## Alternative Backend Hosts

### Railway.app

**Pros:** Generous free tier, faster cold starts, built-in PostgreSQL
**Cons:** Requires credit card for free tier

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. **"New Project"** → **"Deploy from GitHub repo"**
4. Select `doc-scanner` repository
5. **Settings:**
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add `PORT` environment variable (Railway auto-assigns)
7. Deploy and copy generated URL

### Heroku

**Pros:** Battle-tested, many add-ons
**Cons:** Paid only since Nov 2022

**Steps:**
1. Create `Procfile` in `backend/`:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
2. Create `runtime.txt`:
   ```
   python-3.11.0
   ```
3. Deploy via Heroku CLI or GitHub integration

### Fly.io

**Pros:** Edge deployment, great performance
**Cons:** More complex setup

**Steps:**
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. `fly auth signup` or `fly auth login`
3. `cd backend && fly launch`
4. Follow interactive setup
5. `fly deploy`

---

## Frontend Deployment (GitHub Pages)

GitHub Pages is perfect for hosting the static frontend.

### Method 1: Deploy from Repository (Recommended)

**Step 1: Update API URL**

Edit `frontend/script.js`:

```javascript
const CONFIG = {
    // Replace with your Render URL
    API_URL: 'https://doc-scanner-api.onrender.com',
    MAX_FILE_SIZE: 10 * 1024 * 1024,
    SUPPORTED_TYPES: ['application/pdf', 'image/jpeg', 'image/png', 'image/webp']
};
```

**Step 2: Push to GitHub**

```bash
git add frontend/script.js
git commit -m "Update API URL for production"
git push origin main
```

**Step 3: Enable GitHub Pages**

1. Go to your repository on GitHub
2. Click **"Settings"** tab
3. Scroll to **"Pages"** in left sidebar
4. **Source:**
   - Branch: `main`
   - Folder: `/frontend`
5. Click **"Save"**
6. Wait 1-2 minutes for deployment

**Step 4: Access Your Site**

Your site will be available at:
```
https://yourusername.github.io/doc-scanner/
```

### Method 2: Deploy from gh-pages Branch

If you want to keep production code separate:

```bash
# Install gh-pages package (if using Node.js)
npm install -g gh-pages

# Or use a simple script
git checkout --orphan gh-pages
git rm -rf .
cp -r frontend/* .
git add .
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages
```

Then in repository settings, select `gh-pages` branch as source.

---

## Connecting Frontend to Backend

### CORS Configuration

Your backend already has CORS enabled for all origins. For production, update `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourusername.github.io",
        "https://your-custom-domain.com"  # if applicable
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy backend:
```bash
git add backend/main.py
git commit -m "Update CORS for production"
git push origin main
```

Render will auto-deploy from the commit.

---

## Custom Domain Setup

### For GitHub Pages

**Step 1: Buy Domain**
- Namecheap, Google Domains, Cloudflare, etc.

**Step 2: Configure DNS**

Add these records in your domain registrar:

```
Type    Host    Value
A       @       185.199.108.153
A       @       185.199.109.153
A       @       185.199.110.153
A       @       185.199.111.153
CNAME   www     yourusername.github.io
```

**Step 3: Configure GitHub Pages**

1. Repository **Settings** → **Pages**
2. **Custom domain:** `yourdomain.com`
3. **Save**
4. Wait for DNS verification (can take 24-48 hours)
5. Enable **"Enforce HTTPS"** once verified

### For Render Backend

1. Render Dashboard → Your service → **Settings**
2. **Custom Domains** section
3. Click **"Add Custom Domain"**
4. Enter: `api.yourdomain.com`
5. Add provided CNAME record to your DNS:
   ```
   Type    Host    Value
   CNAME   api     your-app.onrender.com
   ```
6. Wait for verification

---

## Environment Variables

### Backend Environment Variables

For future features (SynthID, database, etc.):

**Render:**
1. Dashboard → Your service → **Environment**
2. Click **"Add Environment Variable"**
3. Add key-value pairs

**Example:**
```bash
SYNTHID_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:pass@host:5432/db
MAX_UPLOAD_SIZE=10485760
DEBUG=False
```

**Access in code:**
```python
import os

synthid_key = os.getenv('SYNTHID_API_KEY')
debug = os.getenv('DEBUG', 'False') == 'True'
```

### Frontend Environment Variables

For frontend, use build-time replacement:

**Create `frontend/config.js`:**
```javascript
const CONFIG = {
    API_URL: process.env.API_URL || 'http://localhost:8000',
    DEBUG: process.env.DEBUG === 'true'
};
```

---

## Troubleshooting

### Backend Issues

**Problem:** Service won't start
```bash
# Check logs in Render dashboard
# Common issues:
- Missing dependencies in requirements.txt
- Python version mismatch
- Port binding issues (use $PORT env variable)
```

**Problem:** CORS errors
```bash
# Solution: Update allow_origins in main.py
# Include exact frontend URL (no trailing slash)
```

**Problem:** 502 Bad Gateway
```bash
# Render free tier spins down after inactivity
# First request after spin-down takes ~30 seconds
# This is expected behavior on free tier
```

### Frontend Issues

**Problem:** Can't connect to API
```bash
# Check:
1. Is API URL correct in script.js?
2. Is backend running? Test with curl
3. Are CORS headers set correctly?
4. Check browser console for specific error
```

**Problem:** GitHub Pages not updating
```bash
# Solution:
1. Clear browser cache
2. Check Actions tab for build status
3. Wait 1-2 minutes for propagation
4. Hard refresh (Ctrl+Shift+R)
```

**Problem:** 404 on GitHub Pages
```bash
# Check:
1. Is "Pages" enabled in repo settings?
2. Is correct folder selected (/frontend)?
3. Does index.html exist in frontend folder?
4. Wait a few minutes after enabling Pages
```

### Performance Issues

**Problem:** Slow analysis
```bash
# Optimize:
1. Resize large images before analysis
2. Implement caching for repeated files
3. Use background workers for heavy computation
4. Consider upgrading to Render paid tier
```

### Testing Deployment

**Quick Test Script:**

```bash
#!/bin/bash

# Test backend health
echo "Testing backend..."
curl https://your-app.onrender.com/health

# Test file upload (requires test file)
echo -e "\n\nTesting file upload..."
curl -X POST https://your-app.onrender.com/analyze \
  -F "file=@test-image.jpg" \
  -H "Content-Type: multipart/form-data"
```

---

## Post-Deployment Checklist

- [ ] Backend health endpoint responding
- [ ] Frontend loads without errors
- [ ] File upload works
- [ ] Analysis returns results
- [ ] Results display correctly
- [ ] Download report works
- [ ] History saves to localStorage
- [ ] Mobile responsive (test on phone)
- [ ] CORS configured for production domain
- [ ] Custom domain configured (if applicable)
- [ ] HTTPS enabled (both frontend and backend)
- [ ] Analytics setup (optional - Google Analytics)
- [ ] Error monitoring (optional - Sentry)

---

## Monitoring & Maintenance

### Render Monitoring

1. **Logs:** Dashboard → Your service → Logs
2. **Metrics:** CPU, Memory, Response times
3. **Alerts:** Set up email notifications for downtime

### GitHub Pages Monitoring

1. **Actions:** Check build status
2. **Traffic:** Repository → Insights → Traffic
3. **Uptime:** Use external service (UptimeRobot, Pingdom)

### Regular Maintenance

- **Weekly:** Check logs for errors
- **Monthly:** Review usage metrics
- **Quarterly:** Update dependencies
  ```bash
  pip list --outdated  # Check for updates
  pip install --upgrade package-name
  ```

---

## Scaling Considerations

### When to Upgrade

**Free Tier Sufficient:**
- Portfolio project
- Personal use
- < 100 requests/day
- Don't mind cold starts

**Consider Paid Tier:**
- Production application
- > 100 requests/day
- Need consistent performance
- Enterprise users

### Upgrade Path

1. **Render Starter ($7/month):**
   - No cold starts
   - 512 MB RAM
   - Good for 1000s of requests/day

2. **Render Pro ($25/month):**
   - 2 GB RAM
   - Horizontal scaling
   - Custom health checks

3. **Dedicated Server:**
   - AWS EC2, DigitalOcean Droplet
   - Full control
   - More complex setup

---

## Security Hardening for Production

```python
# backend/main.py additions

from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# HTTPS redirect (if not using Render's automatic HTTPS)
app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourdomain.com", "*.onrender.com"]
)

# Apply rate limit to analyze endpoint
@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze_document(request: Request, file: UploadFile = File(...)):
    ...
```

---

## Next Steps

After successful deployment:

1. **Share:** Update your LinkedIn, portfolio
2. **Monitor:** Set up analytics and error tracking
3. **Iterate:** Gather feedback, improve features
4. **Document:** Write blog post about the project
5. **Expand:** Add new detection methods, ML models

---

## Support

If you encounter issues:

1. Check troubleshooting section above
2. Review Render/GitHub Pages documentation
3. Search GitHub Issues
4. Create new issue with:
   - Deployment platform
   - Error messages
   - Steps to reproduce

---

**Deployment Complete! 🎉**

Your Document Authenticity Scanner is now live and ready for the world.
