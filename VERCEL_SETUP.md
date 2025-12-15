# Vercel Deployment Setup Guide

## Issue: Code pushed to GitHub but Vercel not deploying

If Vercel isn't automatically deploying when you push to GitHub, follow these steps:

## Step 1: Check Vercel Project Connection

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Find your project: `usc-racing-config`
3. Click on the project
4. Go to **Settings** → **Git**

**Check:**
- ✅ Is GitHub repository connected?
- ✅ Is the correct repository selected? (`thatrandomasiandev/USC-Racing-config`)
- ✅ Is the branch set to `main`?
- ✅ Are "Automatic Deployments" enabled?

## Step 2: Reconnect Repository (if needed)

If repository is not connected:

1. Go to **Settings** → **Git**
2. Click **Disconnect** (if connected to wrong repo)
3. Click **Connect Git Repository**
4. Select `thatrandomasiandev/USC-Racing-config`
5. Select branch: `main`
6. Click **Deploy**

## Step 3: Manual Deployment

If auto-deploy still doesn't work:

1. In Vercel Dashboard, click **Deployments** tab
2. Click **Create Deployment** button
3. Select:
   - **Git Repository**: `thatrandomasiandev/USC-Racing-config`
   - **Branch**: `main`
   - **Commit**: Latest commit
4. Click **Deploy**

## Step 4: Check Webhook (if still not working)

1. Go to GitHub repository: https://github.com/thatrandomasiandev/USC-Racing-config
2. Go to **Settings** → **Webhooks**
3. Look for Vercel webhook
4. If missing, Vercel should create it automatically when you connect the repo

## Step 5: Verify Project Settings

In Vercel Dashboard → Settings → General:

- **Framework Preset**: Other (or leave blank)
- **Root Directory**: `./` (project root)
- **Build Command**: (leave empty - Python doesn't need build)
- **Output Directory**: (leave empty)
- **Install Command**: (leave empty - Vercel auto-installs from requirements.txt)

## Step 6: Check Build Logs

1. Go to **Deployments** tab
2. Click on any deployment
3. Check **Build Logs** for errors
4. Check **Function Logs** for runtime errors

## Troubleshooting

### If deployments still don't trigger:

1. **Disconnect and reconnect** the GitHub repository in Vercel
2. **Manually trigger** a deployment to test
3. **Check GitHub webhooks** - ensure Vercel webhook exists and is active
4. **Verify repository permissions** - Vercel needs read access to your repo

### Alternative: Use Vercel CLI

If web UI isn't working, you can deploy via CLI:

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link project
vercel link

# Deploy
vercel --prod
```

## Current Repository

- **GitHub**: https://github.com/thatrandomasiandev/USC-Racing-config.git
- **Branch**: `main`
- **Latest Commit**: Check with `git log --oneline -1`

