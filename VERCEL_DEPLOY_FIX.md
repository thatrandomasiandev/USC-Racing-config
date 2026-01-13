# Vercel Deployment Fix Guide

## Changes Made

### 1. Fixed `api/index.py`
- ✅ Added Mangum adapter to wrap FastAPI for Vercel serverless runtime
- ✅ Fixed import paths to correctly reference `backend/main.py`
- ✅ Set proper environment variables for Vercel deployment
- ✅ Configured template and static file paths

### 2. Updated `vercel.json`
- ✅ Simplified routing configuration
- ✅ Set Python runtime to 3.11
- ✅ Configured function memory and timeout

## Deployment Steps

### Step 1: Commit Changes
```bash
git add api/index.py vercel.json
git commit -m "Fix Vercel deployment configuration"
git push
```

### Step 2: Verify Vercel Project Settings

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to **Settings** → **General**
4. Verify:
   - **Framework Preset**: Other (or blank)
   - **Root Directory**: `./` (project root)
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
   - **Install Command**: (leave empty - Vercel auto-detects `requirements.txt`)

### Step 3: Set Environment Variables

Go to **Settings** → **Environment Variables** and add:

```
TEL_HOST=0.0.0.0
TEL_PORT=8000
TEL_CORS_ORIGINS=*
TEL_LOG_ENABLED=false
TEL_DATA_DIR=/tmp
MOTEC_ENABLED=false
MOTEC_NAS_DISCOVERY_SCAN_ON_STARTUP=false
```

### Step 4: Trigger Deployment

**Option A: Automatic (if GitHub connected)**
- Push to your main branch
- Vercel will auto-deploy

**Option B: Manual**
1. Go to **Deployments** tab
2. Click **Create Deployment**
3. Select your repository and branch
4. Click **Deploy**

### Step 5: Check Build Logs

1. Go to **Deployments** tab
2. Click on the latest deployment
3. Check **Build Logs** for:
   - ✅ Python dependencies installing
   - ✅ No import errors
   - ✅ Function created successfully

### Step 6: Test Endpoints

After deployment, test these URLs:

- `https://your-project.vercel.app/` - Frontend homepage
- `https://your-project.vercel.app/api/health` - Health check
- `https://your-project.vercel.app/api/config` - Configuration

## Troubleshooting

### Issue: Function Not Found (404)

**Symptoms**: 404 error when accessing any route

**Solutions**:
1. Verify `api/index.py` exists and exports `handler`
2. Check that `vercel.json` routes point to `api/index.py`
3. Ensure Python runtime is set in function config

### Issue: Import Errors

**Symptoms**: `ModuleNotFoundError` or `ImportError` in logs

**Solutions**:
1. Check `requirements.txt` includes all dependencies
2. Verify `sys.path` modifications in `api/index.py`
3. Ensure `backend/` directory is included in deployment

### Issue: Static Files Not Loading

**Symptoms**: CSS/JS files return 404

**Solutions**:
1. Verify `frontend/static/` directory exists in repo
2. Check FastAPI static mount in `backend/main.py`
3. Ensure static files are committed to Git

### Issue: Template Not Found

**Symptoms**: 500 error on homepage

**Solutions**:
1. Verify `frontend/templates/index.html` exists
2. Check `TEMPLATES_DIR` path in settings
3. Ensure templates directory is committed

### Issue: WebSocket Not Working

**Note**: Vercel serverless functions have **limited WebSocket support**. The `/ws` endpoint may not work reliably on Vercel.

**Alternatives**:
- Use polling instead of WebSocket for real-time updates
- Consider Railway, Render, or Fly.io for full WebSocket support

## Key Files for Deployment

```
├── api/
│   └── index.py          # Vercel serverless entry point
├── backend/
│   ├── main.py           # FastAPI app
│   └── internal/         # Backend modules
├── frontend/
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, assets
├── requirements.txt      # Python dependencies
├── vercel.json           # Vercel configuration
└── runtime.txt           # Python version (3.11)
```

## Verification Checklist

- [ ] `api/index.py` exports `handler` (Mangum-wrapped FastAPI app)
- [ ] `vercel.json` routes configured correctly
- [ ] `requirements.txt` includes `mangum>=0.17.0`
- [ ] `frontend/templates/index.html` exists
- [ ] `frontend/static/` directory exists with CSS/JS
- [ ] Environment variables set in Vercel dashboard
- [ ] Python runtime set to 3.11
- [ ] All files committed to Git

## Next Steps After Successful Deployment

1. **Test all endpoints** - Verify API responses
2. **Check logs** - Monitor for runtime errors
3. **Set up monitoring** - Configure Vercel analytics
4. **Consider alternatives** - For WebSocket support, consider Railway/Render

## Platform Limitations

### Vercel Serverless Functions:
- ✅ Fast API responses
- ✅ Auto-scaling
- ✅ Easy GitHub integration
- ❌ Limited WebSocket support
- ❌ Read-only filesystem (except `/tmp`)
- ❌ Cold start delays
- ❌ 30-second max execution time

### For Full Features, Consider:
- **Railway** - Full Python support, WebSockets, file I/O
- **Render** - Similar to Railway, good free tier
- **Fly.io** - Docker-based, full control

