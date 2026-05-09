# Backend Deployment Guide

This backend is ready to be deployed to **Railway**, **Render**, or **Fly.io** using Docker.

## Prerequisites

1. **GitHub Repository**: Backend code is pushed to `https://github.com/vishxesh10/medtech-backend`
2. **Docker Hub Account**: For storing Docker images (optional)
3. **Environment Variables**: Set these in your deployment platform

## Environment Variables

```
DATABASE_URL=postgresql+psycopg://user:password@host:port/dbname
JWT_SECRET_KEY=your-long-random-secret-key-here
GEMINI_KEY=your-gemini-api-key-here
CORS_ALLOW_ORIGINS=["https://yourdomain.com"]
```

## Deployment Options

### Option 1: Railway (Recommended for fast setup)

1. Go to [Railway.app](https://railway.app) and sign in
2. Click **New Project** → **Deploy from GitHub**
3. Select `medtech-backend` repository
4. Add environment variables in the dashboard
5. Railway will auto-deploy on every push to `main`

### Option 2: Render

1. Go to [Render.com](https://render.com) and sign in
2. Click **New** → **Web Service**
3. Connect your GitHub account and select `medtech-backend`
4. Set environment to **Docker**
5. Add environment variables
6. Deploy

### Option 3: Docker + Manual Deployment

```bash
# Build
docker build -t medtech-backend:latest .

# Run locally
docker-compose up -d

# Push to Docker Hub
docker tag medtech-backend:latest your-username/medtech-backend:latest
docker push your-username/medtech-backend:latest
```

## GitHub Secrets (for CI/CD)

If using GitHub Actions to push Docker images:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub access token

## Database

- **Development**: SQLite (default)
- **Production**: PostgreSQL (set `DATABASE_URL`)

Migrations run automatically on startup via `alembic upgrade head`.

## Monitoring

- Backend runs on port `8000` by default
- Health check: `GET /health`
- API version: `GET /version`

## Support

For issues or questions, check the main README or open an issue on GitHub.
