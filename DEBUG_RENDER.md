# Debugging Frontend-Backend Connection on Render

## Quick Diagnostics

### 1. Check Browser Console (F12)

When you open the frontend and try to login, check the browser console for:

1. **API URL being used:**
   - You should see: `"Detected Render deployment, using: https://hms-backend-xxxx.onrender.com"`
   - If you see `"Using localhost for development"`, the detection failed

2. **Network errors:**
   - Look for failed fetch requests
   - Check if it's trying to reach the correct backend URL

### 2. Test Backend Directly

Open a new browser tab and go to your backend URL:
```
https://hms-backend-XXXX.onrender.com/auth/login
```

You should see an error like `{"message": "Method not allowed"}` - this means backend is running!

### 3. Common Issues & Fixes

#### Issue: "Login failed" alert
**Possible causes:**
- Backend not running
- CORS issue
- Database not initialized
- Wrong credentials

**Check:**
1. Go to Render Dashboard → `hms-backend` → Logs
2. Look for errors like:
   - `ModuleNotFoundError`
   - `Database connection failed`
   - `CORS error`

#### Issue: Network error in console
**Fix:**
- Verify both services are "Live" in Render dashboard
- Check that backend URL in console matches actual backend URL

#### Issue: CORS error
**Fix:**
- Backend `app.py` already has CORS enabled
- If still seeing CORS errors, backend might not be running

### 4. Manual URL Override (Temporary Test)

If auto-detection isn't working, you can manually set the backend URL:

1. Go to Render Dashboard
2. Click on `hms-frontend` service
3. Go to "Environment" tab
4. Add environment variable:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://hms-backend-XXXX.onrender.com` (replace XXXX with your actual backend URL)
5. Click "Save Changes" (will trigger redeploy)

### 5. Check Backend Logs

Go to Render Dashboard → `hms-backend` → Logs

Look for:
- ✅ `Running on http://0.0.0.0:10000` - Backend started successfully
- ✅ `Admin user created` - Database initialized
- ❌ Any Python errors or stack traces

### 6. Test Login Credentials

Default admin credentials:
- **Username:** `admin`
- **Password:** `admin123`

If you see "Invalid credentials", the backend IS working but credentials are wrong.

### 7. Check Database Initialization

Backend logs should show:
```
Admin user created.
```

If you don't see this, the database might not be initialized.

---

## What to Report Back

Please check and tell me:

1. **What URL does the console show?**
   - Open browser console (F12)
   - Refresh the page
   - Look for the API URL log message

2. **Is the backend running?**
   - Go to `https://hms-backend-XXXX.onrender.com` in browser
   - What do you see?

3. **What error appears in browser console?**
   - Any red error messages?
   - Failed network requests?

4. **Backend logs:**
   - Any errors in Render → hms-backend → Logs?

This will help me pinpoint the exact issue! 🔍
