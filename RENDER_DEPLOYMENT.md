# MedTech AI - Render Deployment Guide

## Prerequisites

1. **GitHub Repository** - Code pushed to GitHub
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **API Keys** - Gemini API key from Google
4. **PostgreSQL** - Render provides this automatically

## Step 1: Prepare Your GitHub Repository

### 1.1 Verify files are in the root:
- `Dockerfile` ✓
- `docker-compose.yml` ✓
- `pyproject.toml` ✓
- `app.py` ✓
- `.env.example` ✓

### 1.2 Commit and push to GitHub:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

## Step 3: Deploy Backend on Render

### 3.1 Create New Web Service:
1. Click **New +** button
2. Select **Web Service**
3. Connect GitHub and select `medtech-backend` repository
4. **Runtime**: Docker
5. **Name**: `medtech-backend`
6. **Region**: Choose closest to your location
7. **Plan**: Free tier or Starter ($7/month)

### 3.2 Configure Build & Deploy:
- **Build Command**: Leave blank (uses Dockerfile)
- **Start Command**: Leave blank (uses Dockerfile)

## Step 4: Add Environment Variables

In Render dashboard:
1. Go to your web service
2. Click **Environment** tab
3. Add these variables:

```
JWT_SECRET_KEY=jk5cfc6h52J7LDd9rNRbaXezNshZzUaNeRTeApTZnqw

GEMINI_KEY=your-actual-gemini-api-key-here

CORS_ALLOW_ORIGINS=["https://medtech-backend.onrender.com","https://your-frontend-url.com"]

DATABASE_URL=postgresql://... (auto-created by Render PostgreSQL)
```

## Step 5: Create PostgreSQL Database

1. Click **New +** button in Render
2. Select **PostgreSQL**
3. **Name**: `medtech-db`
4. **Region**: Same as web service
5. **PostgreSQL Version**: 15
6. Click **Create Database**

### 5.1 Get Database Connection String:
- Go to the PostgreSQL service
- Copy the **Internal Database URL**
- Paste as `DATABASE_URL` in web service environment variables

**Important**: Use the **Internal URL** (postgres://...) not the External URL

## Step 6: Run Database Migrations

### 6.1 Connect to Database:
```bash
# On your local machine
psql <DATABASE_URL>
```

### 6.2 Run migrations:
```bash
alembic upgrade head
```

Or set up a migration job in Render:
1. Create new **Cron Job**
2. **Schedule**: Run once
3. **Command**: `alembic upgrade head`
4. This will create tables on deployment

## Step 7: Deploy Frontend on Render

### 7.1 Build the frontend:
```bash
cd frontend
npm run build
```

This creates a `dist/` folder with production build.

### 7.2 Create Static Site:
1. Click **New +** in Render
2. Select **Static Site**
3. Connect GitHub and select your repository
4. **Name**: `medtech-frontend`
5. **Build Command**: `cd frontend && npm install && npm run build`
6. **Publish Directory**: `frontend/dist`

### 7.3 Add Environment Variables:
1. Go to Static Site settings
2. Add **Build Environment Variables**:
```
VITE_API_BASE_URL=https://medtech-backend.onrender.com
```

## Step 8: Get API Keys

### 8.1 Gemini API Key:
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **Create API Key**
3. Copy the key
4. Add to Render `GEMINI_KEY` variable

## Step 9: Update CORS Settings (If needed)

After frontend and backend URLs are generated:
1. Go to backend web service
2. Update `CORS_ALLOW_ORIGINS` with actual URLs:
```
CORS_ALLOW_ORIGINS=["https://medtech-frontend.onrender.com","https://medtech-backend.onrender.com"]
```

## Step 10: Test Deployment

1. Visit your frontend URL: `https://medtech-frontend.onrender.com`
2. Go to Settings → Register
3. Create test account
4. Try uploading a prescription image
5. Check browser console (F12) for errors

## Monitoring & Debugging

### Check Logs:
- Backend: Logs tab in web service
- Frontend: Logs tab in static site
- Database: Logs tab in PostgreSQL service

### Common Issues:

**CORS Error**: Update `CORS_ALLOW_ORIGINS` in environment variables

**Database Connection Failed**: 
- Use Internal Database URL
- Run migrations with `alembic upgrade head`

**API Key Not Working**:
- Verify GEMINI_KEY is set correctly
- Check it's not expired on Google AI Studio

**Build Fails**:
- Check logs for specific error
- Ensure Dockerfile and requirements are correct

## Costs on Render

- **Free Tier**: 
  - $0/month web service (spins down after 15 min inactivity)
  - $0/month static site
  - $0/month PostgreSQL

- **Starter Plan**:
  - $7/month web service (always running)
  - $7/month PostgreSQL (recommended for production)

## Next Steps

1. Set up automated deployments (GitHub integration is automatic)
2. Add monitoring/alerts
3. Set up email notifications for errors
4. Consider upgrading to paid plans for production reliability

---

**Need Help?**
- Render Docs: [docs.render.com](https://docs.render.com)
- FastAPI Docs: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- Contact support: support@render.com
