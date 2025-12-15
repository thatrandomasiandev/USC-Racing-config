# Vercel Deployment Guide

## Issue: 404 NOT_FOUND

The Vercel deployment is showing a 404 error because Vercel needs specific configuration for FastAPI/Python applications.

## Current Setup

I've created:
- `vercel.json` - Vercel configuration
- `api/index.py` - Serverless function entry point

## Limitations

**Important:** Vercel serverless functions have limitations that may affect this application:

1. **WebSocket Support**: Limited WebSocket support (may not work for real-time telemetry)
2. **File System**: Read-only file system (can't write LDX files)
3. **Long-running**: Not ideal for persistent connections
4. **Cold Starts**: Functions may have cold start delays

## Better Alternatives

For a FastAPI app with WebSocket support and file I/O, consider:

1. **Railway** (Recommended)
   - Full Python support
   - WebSocket support
   - File system access
   - Easy deployment from GitHub

2. **Render**
   - Python support
   - WebSocket support
   - Free tier available

3. **Fly.io**
   - Docker-based
   - Full control
   - Good for complex apps

## Fixing Vercel Deployment

If you want to continue with Vercel:

1. **Commit the new files:**
   ```bash
   git add vercel.json api/index.py
   git commit -m "Add Vercel configuration"
   git push
   ```

2. **Vercel will auto-deploy** from GitHub

3. **Set Environment Variables** in Vercel dashboard:
   - `TEL_HOST=0.0.0.0`
   - `TEL_PORT=8000`
   - Any other config from `.env`

## Testing

After deployment, check:
- `/` - Should show frontend
- `/api/health` - Should return health status
- `/api/config` - Should return configuration

Note: WebSocket endpoints (`/ws`) may not work on Vercel serverless functions.

