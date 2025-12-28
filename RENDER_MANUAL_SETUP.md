# Render Deployment - Manual Steps After Blueprint

The `render.yaml` blueprint will create:
- ✅ Backend API (Flask)
- ✅ Frontend (Vue.js)  
- ✅ PostgreSQL Database

**You need to add manually:**
- Redis
- Celery Worker
- Celery Beat

---

## Step 1: Deploy the Blueprint First

1. Push the updated `render.yaml` to GitHub
2. Create Blueprint on Render
3. Wait for backend and frontend to deploy successfully

---

## Step 2: Create Redis Instance

1. In Render Dashboard, click **"New +"** → **"Redis"**
2. Fill in:
   - **Name:** `hms-redis`
   - **Region:** Oregon (same as other services)
   - **Plan:** Free
3. Click **"Create Redis"**
4. Wait for it to be "Available"
5. **Copy the Internal Redis URL** (looks like `redis://red-xxxxx:6379`)

---

## Step 3: Add Redis URL to Backend

1. Go to **hms-backend** service
2. Click **"Environment"** tab
3. Add these environment variables:
   - **Key:** `REDIS_URL` | **Value:** `<paste internal Redis URL>`
   - **Key:** `CELERY_BROKER_URL` | **Value:** `<paste internal Redis URL>`
   - **Key:** `CELERY_RESULT_BACKEND` | **Value:** `<paste internal Redis URL>`
4. Click **"Save Changes"** (backend will redeploy)

---

## Step 4: Create Celery Worker

1. Click **"New +"** → **"Background Worker"**
2. Connect to your GitHub repo
3. Fill in:
   - **Name:** `hms-celery-worker`
   - **Region:** Oregon
   - **Branch:** `master`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `celery -A app.celery worker --loglevel=info`
4. Add environment variables (copy from backend):
   - `DATABASE_URL` - Link to `hms-db`
   - `REDIS_URL` - Paste Redis internal URL
   - `CELERY_BROKER_URL` - Paste Redis internal URL
   - `CELERY_RESULT_BACKEND` - Paste Redis internal URL
   - `MAIL_USERNAME` - Your Gmail
   - `MAIL_PASSWORD` - Gmail App Password
5. Click **"Create Background Worker"**

---

## Step 5: Create Celery Beat (Scheduler)

1. Click **"New +"** → **"Background Worker"**
2. Connect to your GitHub repo
3. Fill in:
   - **Name:** `hms-celery-beat`
   - **Region:** Oregon
   - **Branch:** `master`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `celery -A app.celery beat --loglevel=info`
4. Add environment variables (same as worker):
   - `DATABASE_URL` - Link to `hms-db`
   - `REDIS_URL` - Paste Redis internal URL
   - `CELERY_BROKER_URL` - Paste Redis internal URL
   - `CELERY_RESULT_BACKEND` - Paste Redis internal URL
5. Click **"Create Background Worker"**

---

## Final Check

You should have 5 services running:

- ✅ hms-backend (Web Service)
- ✅ hms-frontend (Web Service)
- ✅ hms-celery-worker (Background Worker)
- ✅ hms-celery-beat (Background Worker)
- ✅ hms-redis (Redis)
- ✅ hms-db (PostgreSQL)

---

## Quick Reference: Environment Variables

### Backend, Worker, and Beat all need:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Auto-linked from hms-db |
| `REDIS_URL` | Redis internal URL |
| `CELERY_BROKER_URL` | Redis internal URL |
| `CELERY_RESULT_BACKEND` | Redis internal URL |
| `MAIL_USERNAME` | your-email@gmail.com |
| `MAIL_PASSWORD` | Gmail App Password |

### Frontend needs:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | Auto-linked from hms-backend |

---

## Why Manual Setup?

Render's Blueprint (render.yaml) doesn't support:
- Redis as a database type in free tier
- Automatic linking of Redis to services

So we deploy the basic services via Blueprint, then add Redis and workers manually.
