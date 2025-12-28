# Quick Deployment Steps

## 1. Push to GitHub
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

## 2. Create Render Blueprint
1. Go to [render.com](https://render.com)
2. Click **New +** → **Blueprint**
3. Connect GitHub and select your `hms` repository
4. Render will detect `render.yaml` automatically

## 3. Set Environment Variables

### Backend & Worker Services
Add these in Render dashboard:
- `MAIL_USERNAME`: Your Gmail address
- `MAIL_PASSWORD`: Gmail App Password (get from [myaccount.google.com/security](https://myaccount.google.com/security))

## 4. Deploy
Click **"Apply"** and wait 5-10 minutes for all services to deploy.

## 5. Access Your App
- Frontend: `https://hms-frontend-XXXX.onrender.com`
- Login with: `admin` / `admin123`

---

## Files Created
- ✅ `render.yaml` - Service configuration
- ✅ `backend/build.sh` - Build script
- ✅ Updated `backend/requirements.txt`
- ✅ Updated `backend/application/config.py`
- ✅ Updated `backend/app.py`
- ✅ Updated `frontend/vite.config.js`

---

## Important Notes
⚠️ Free services sleep after 15 min inactivity (~30s wake time)  
⚠️ Free PostgreSQL expires after 90 days  
💡 Use [UptimeRobot](https://uptimerobot.com) to keep services active

---

For detailed instructions, see [RENDER_DEPLOYMENT_GUIDE.md](file:///home/aryan/.gemini/antigravity/brain/0388f943-861f-4cb9-84c1-92c57d78d9e3/RENDER_DEPLOYMENT_GUIDE.md)
