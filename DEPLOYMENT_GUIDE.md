# Deployment Guide: Pronunciation Quiz to Render

This guide will help you deploy your pronunciation quiz web app to Render (free hosting).

## Step 1: Prepare Your Local Repository

First, make sure you're in the project root directory:
```
cd C:\Users\alamz_uy7970p\OneDrive\Documents\English
```

Initialize Git (if not already done):
```
git init
git add .
git commit -m "Initial commit: Pronunciation Quiz Web App"
```

## Step 2: Create GitHub Repository

1. **Go to [github.com](https://github.com)** and sign in
2. **Click "+"** in top right → **New repository**
3. **Name it**: `pronunciation-quiz` (or your preferred name)
4. **Choose**: Public (so Render can access it)
5. **DO NOT initialize** with README, .gitignore, or license (we already have them)
6. **Click "Create repository"**

## Step 3: Push Code to GitHub

Copy the commands from your GitHub repo page. They'll look like:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/pronunciation-quiz.git
git branch -M main
git push -u origin main
```

Run these in PowerShell in your project root.

## Step 4: Deploy to Render

### Option A: Simple (One-Click) Deploy

1. **Go to [render.com](https://render.com)**
2. **Sign up with GitHub account** (authorize the connection)
3. **Click "New +"** → **Web Service**
4. **Select your `pronunciation-quiz` repository**
5. **Fill in:**
   - Name: `pronunciation-quiz-backend`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn web_app.backend.api.main:app --host 0.0.0.0 --port 8000`
6. **Plan: Free** (stays in free tier)
7. **Click "Create Web Service"**

Wait 3-5 minutes for deployment. Your backend URL will look like:
```
https://pronunciation-quiz-backend.onrender.com
```

### Option B: Advanced (Using render.yaml)

If you want to deploy both backend and frontend from the same repo:

1. Follow Steps 1-3 above
2. Go to Render dashboard
3. **New +" → "Blueprint**
4. Select your GitHub repo
5. Render will auto-read `render.yaml` and set everything up
6. Click "Deploy"

This deploys:
- Backend API on one URL
- Frontend on another URL
- Auto-redeploy on every GitHub push

## Step 5: Update Your Frontend (if needed)

The app now **automatically detects** the environment:
- **On Render**: Uses the deployed backend URL
- **On localhost**: Uses `http://localhost:8000`

If you want to manually specify the backend URL, edit `web_app/frontend/static/js/app.js` line 6-17.

## Step 6: Access Your Deployed App

Once deployment is complete:

**BackendAPI:** https://pronunciation-quiz-backend.onrender.com/api/health
**Frontend App**: https://pronunciation-quiz-backend.onrender.com/templates/index.html

(The frontend is served from the same backend domain)

## Step 7: Update Code

To update your app:

```powershell
# Make changes locally
git add .
git commit -m "Describe your changes"
git push
```

Render automatically re-deploys on every push to `main` branch!

## Troubleshooting

### Backend shows error on Render
1. Go to Render dashboard → Your Web Service
2. Click **Logs** tab
3. Look for error messages
4. Common issues:
   - Module not found → Check requirements.txt
   - Port already in use → Shouldn't happen on Render
   - Import error → Check your file structure is correct

### Frontend can't reach backend
- Check browser Console (F12)
- The app auto-detects environment, so it should work
- If error persists, manually check the backend URL in app.js

### Port or module errors
1. Go back to local machine
2. Test locally: `.\start_app.bat`
3. Make sure everything works
4. Then push to GitHub and redeploy

## Free Tier Limits

- 750 hours/month per service (free tier)
- 50 concurrent connections
- 100MB/sec bandwidth
- Apps spin down after 30 minutes of inactivity

⚠️ **Note**: First deploy may take 5+ minutes. After ~30 mins of no usage, the free dyno sleeps. Next request takes 30 seconds to wake up.

## Upgrade Later (Optional)

If you want better performance:
- Starter Plan: $7/month
- Standard: $12/month
- All include 24/7 uptime (no spin-down)

## Next Steps

1. **Add custom domain** (optional): Settings → Domains
2. **Enable auto-deploy on push**: Already enabled!
3. **Monitor usage**: Metrics tab in Render dashboard
4. **Add environment variables** if needed: Settings → Environment

## Questions?

If deployment fails:
1. Check Render logs (most helpful)
2. Verify `requirements.txt` has all dependencies
3. Ensure `web_app/backend/api/main.py` path is correct
4. Test locally first with `start_app.bat`

---

**Congratulations! Your app is now published!** 🎉

Share the URL with others: `https://pronunciation-quiz-backend.onrender.com/templates/index.html`
