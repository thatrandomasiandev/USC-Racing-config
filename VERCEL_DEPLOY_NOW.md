# Deploy to Vercel - Step by Step Guide

## ✅ Pre-Deployment Checklist

Your project is now configured for Vercel! Here's what's ready:

- ✅ `api/index.py` - Serverless function with Mangum adapter
- ✅ `vercel.json` - Vercel configuration
- ✅ `requirements.txt` - Python dependencies (includes Mangum)
- ✅ `runtime.txt` - Python 3.11
- ✅ Frontend templates and static files in place

## 🚀 Deployment Options

### Option 1: Deploy via Vercel Dashboard (Recommended)

#### Step 1: Connect Your Repository

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Import your GitHub repository:
   - Select your repository (`USC-Racing-config` or similar)
   - Click **"Import"**

#### Step 2: Configure Project Settings

In the project configuration screen:

- **Framework Preset**: Select **"Other"** or leave blank
- **Root Directory**: `./` (project root)
- **Build Command**: Leave **empty**
- **Output Directory**: Leave **empty**
- **Install Command**: Leave **empty** (Vercel auto-detects `requirements.txt`)

Click **"Deploy"**

#### Step 3: Set Environment Variables

After initial deployment, go to **Settings** → **Environment Variables** and add:

```
TEL_HOST=0.0.0.0
TEL_PORT=8000
TEL_CORS_ORIGINS=*
TEL_LOG_ENABLED=false
TEL_DATA_DIR=/tmp
MOTEC_ENABLED=false
MOTEC_NAS_DISCOVERY_SCAN_ON_STARTUP=false
```

**Important**: 
- Add these for **Production**, **Preview**, and **Development** environments
- Click **"Save"** after adding each variable

#### Step 4: Redeploy

After adding environment variables:
1. Go to **Deployments** tab
2. Click the **"..."** menu on the latest deployment
3. Select **"Redeploy"**
4. Check **"Use existing Build Cache"** (optional)
5. Click **"Redeploy"**

### Option 2: Deploy via Vercel CLI

#### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

#### Step 2: Login

```bash
vercel login
```

#### Step 3: Deploy

From your project root directory:

```bash
# Link to existing project (if you have one)
vercel link

# Or deploy as new project
vercel

# For production deployment
vercel --prod
```

#### Step 4: Set Environment Variables via CLI

```bash
vercel env add TEL_HOST production
# Enter: 0.0.0.0

vercel env add TEL_PORT production
# Enter: 8000

vercel env add TEL_CORS_ORIGINS production
# Enter: *

vercel env add TEL_LOG_ENABLED production
# Enter: false

vercel env add TEL_DATA_DIR production
# Enter: /tmp

vercel env add MOTEC_ENABLED production
# Enter: false

vercel env add MOTEC_NAS_DISCOVERY_SCAN_ON_STARTUP production
# Enter: false
```

## 🔍 Verify Deployment

After deployment completes, test these URLs:

1. **Homepage**: `https://your-project.vercel.app/`
   - Should show the telemetry dashboard

2. **Health Check**: `https://your-project.vercel.app/api/health`
   - Should return: `{"status": "healthy", ...}`

3. **Configuration**: `https://your-project.vercel.app/api/config`
   - Should return configuration JSON

4. **Static Files**: `https://your-project.vercel.app/static/css/style.css`
   - Should return CSS content

## 🐛 Troubleshooting

### Issue: 404 Not Found

**Check**:
- ✅ `api/index.py` exists and exports `handler`
- ✅ `vercel.json` routes are correct
- ✅ Files are committed to Git

**Fix**: Check build logs in Vercel dashboard for import errors

### Issue: Import Errors

**Symptoms**: `ModuleNotFoundError` in build logs

**Fix**:
1. Verify `requirements.txt` includes all dependencies
2. Check that `backend/` directory is in repository
3. Ensure Python paths in `api/index.py` are correct

### Issue: Static Files Not Loading

**Symptoms**: CSS/JS return 404

**Fix**:
1. Verify `frontend/static/` exists in repo
2. Check FastAPI static mount in `backend/main.py`
3. Ensure files are committed (not in `.gitignore`)

### Issue: Template Not Found

**Symptoms**: 500 error on homepage

**Fix**:
1. Verify `frontend/templates/index.html` exists
2. Check `TEMPLATES_DIR` path detection in `settings.py`
3. Ensure templates are committed to Git

### Issue: Function Timeout

**Symptoms**: 504 Gateway Timeout

**Fix**:
- Current timeout is 30 seconds (max for Vercel)
- For longer operations, consider breaking into smaller requests
- Or use a different platform (Railway/Render) for long-running tasks

## 📊 Monitoring Your Deployment

### View Logs

1. Go to Vercel Dashboard → Your Project
2. Click **"Deployments"** tab
3. Click on a deployment
4. Click **"Functions"** → **"Logs"** to see runtime logs

### View Build Logs

1. Go to deployment details
2. Click **"Build Logs"** tab
3. Check for errors during build/deployment

## 🔄 Continuous Deployment

Once connected to GitHub:

- ✅ Every push to `main` branch = Production deployment
- ✅ Every pull request = Preview deployment
- ✅ Automatic deployments enabled by default

## ⚙️ Advanced Configuration

### Custom Domain

1. Go to **Settings** → **Domains**
2. Add your custom domain
3. Follow DNS configuration instructions

### Environment-Specific Variables

Set different values for:
- **Production**: Live site
- **Preview**: PR previews
- **Development**: Local development

### Increase Function Limits

In `vercel.json`, you can adjust:
- `maxDuration`: Up to 30 seconds (Pro plan)
- `memory`: Up to 3008 MB (Pro plan)

## 📝 Next Steps After Deployment

1. ✅ Test all endpoints
2. ✅ Verify frontend loads correctly
3. ✅ Check WebSocket connection (may have limitations)
4. ✅ Set up monitoring/alerts
5. ✅ Configure custom domain (optional)

## ⚠️ Important Limitations

### Vercel Serverless Functions:

**What Works**:
- ✅ Fast API responses
- ✅ Static file serving
- ✅ REST API endpoints
- ✅ Auto-scaling

**What Has Limitations**:
- ⚠️ **WebSocket**: Limited support (may not work reliably)
- ⚠️ **File System**: Read-only (except `/tmp`)
- ⚠️ **Execution Time**: Max 30 seconds
- ⚠️ **Cold Starts**: First request may be slower

### For Full Features:

If you need:
- Full WebSocket support
- File system write access
- Long-running processes

Consider:
- **Railway** (recommended for Python/WebSocket)
- **Render** (good free tier)
- **Fly.io** (Docker-based, full control)

## 🎯 Quick Reference

**Deploy Command**:
```bash
vercel --prod
```

**Check Status**:
```bash
vercel ls
```

**View Logs**:
```bash
vercel logs
```

**Redeploy**:
```bash
vercel --prod --force
```

## 📞 Need Help?

1. Check build logs in Vercel dashboard
2. Review `VERCEL_DEPLOY_FIX.md` for detailed troubleshooting
3. Check Vercel documentation: https://vercel.com/docs

