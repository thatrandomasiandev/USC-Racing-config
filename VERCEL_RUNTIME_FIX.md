# Fixing Vercel Runtime Error

## Error Message
```
Function Runtimes must have a valid version, for example `now-php@1.0.0`.
```

## Root Cause
This error typically occurs when Vercel is confused about the project type or when there's a conflict between Node.js and Python configurations.

## Solution Steps

### 1. Verify Project Settings in Vercel Dashboard

Go to your Vercel project → **Settings** → **General**:

- **Framework Preset**: Should be **"Other"** or **blank** (NOT Next.js, NOT Node.js)
- **Root Directory**: `./` (project root)
- **Build Command**: **Leave empty**
- **Output Directory**: **Leave empty**
- **Install Command**: **Leave empty**

### 2. Verify Required Files Exist

Ensure these files are at the **project root**:

- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Contains `python-3.11`
- ✅ `api/index.py` - Serverless function entry point
- ✅ `vercel.json` - Configuration (simplified, no runtime field)

### 3. Current vercel.json (Correct Format)

```json
{
  "version": 2,
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/index.py"
    },
    {
      "src": "/ws",
      "dest": "api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

**Important**: No `functions` section, no `runtime` field - Vercel auto-detects Python from `.py` files and `runtime.txt`.

### 4. If Error Persists

#### Option A: Check for Conflicting Config Files
- Ensure there's no `now.json` file (old Vercel config)
- Check that `package.json` is only in `frontend/` directory, not root

#### Option B: Disconnect and Reconnect Repository
1. Go to Vercel Dashboard → Settings → Git
2. Click "Disconnect"
3. Reconnect the repository
4. When configuring, select:
   - Framework: **Other**
   - Build settings: **Leave all empty**

#### Option C: Manual Deployment via CLI
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy (will prompt for settings)
vercel --prod
```

When prompted:
- **Set up and deploy?** Yes
- **Which scope?** Your account
- **Link to existing project?** Yes (select your project)
- **Override settings?** Yes
- **Framework?** Other
- **Build command?** (leave empty, press Enter)
- **Output directory?** (leave empty, press Enter)
- **Development command?** (leave empty, press Enter)
- **Install command?** (leave empty, press Enter)

### 5. Verify Python Detection

After deployment, check build logs:
- Should see: "Installing Python dependencies from requirements.txt"
- Should see: "Python version: 3.11"

If you see Node.js installation instead, the project settings are wrong.

## Why This Happens

Vercel might be detecting:
1. `frontend/package.json` and thinking it's a Node.js project
2. Conflicting framework settings in dashboard
3. Old configuration cached from previous deployments

## Quick Fix Checklist

- [ ] Vercel Dashboard → Settings → General → Framework = "Other"
- [ ] `vercel.json` has no `runtime` field
- [ ] `vercel.json` has no `functions` section (or functions section has no runtime)
- [ ] `requirements.txt` exists at project root
- [ ] `runtime.txt` exists at project root with `python-3.11`
- [ ] `api/index.py` exists and exports `handler`
- [ ] No `now.json` file exists
- [ ] `package.json` only exists in `frontend/` directory

## Still Not Working?

1. Check Vercel build logs for the exact error
2. Try creating a fresh Vercel project
3. Consider using Vercel CLI to deploy and see detailed errors

