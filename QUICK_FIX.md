# Quick Fix: Connect Vercel to GitHub

## The Problem
Code is pushed to GitHub but Vercel isn't deploying automatically.

## The Solution

### Option 1: Connect via Vercel Dashboard (Easiest)

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Click "Add New Project"** (or find your existing project)
3. **Import Git Repository**:
   - Select GitHub
   - Find: `thatrandomasiandev/USC-Racing-config`
   - Click **Import**
4. **Configure Project**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave default)
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
5. **Click "Deploy"**

### Option 2: Use Vercel CLI

```bash
# Install Vercel CLI (if not installed)
npm install -g vercel

# Navigate to project
cd "/Users/joshuaterranova/Desktop/Coding Files: Website Files/USC Racing"

# Login to Vercel
vercel login

# Link project (this will create .vercel directory)
vercel link

# Deploy
vercel --prod
```

### Option 3: Manual Trigger

1. Go to Vercel Dashboard
2. Find your project
3. Click **Deployments** tab
4. Click **Create Deployment**
5. Select:
   - Repository: `thatrandomasiandev/USC-Racing-config`
   - Branch: `main`
   - Commit: Latest
6. Click **Deploy**

## After Connecting

Once connected, Vercel will:
- ✅ Automatically deploy on every push to `main`
- ✅ Show deployment status in GitHub
- ✅ Create a `.vercel` directory (don't commit this)

## Verify Connection

After connecting, check:
- Vercel Dashboard → Settings → Git
- Should show: "Connected to GitHub"
- Repository: `thatrandomasiandev/USC-Racing-config`
- Branch: `main`

