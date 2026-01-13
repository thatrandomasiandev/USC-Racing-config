# Quick Start - Viewing the New Microsoft Word-Style UI

## Problem: You're seeing the old frontend

If you're viewing `http://localhost:8000`, you're seeing the **old frontend** (vanilla HTML/JS). The new Next.js + Tailwind frontend runs on a **different port** (`http://localhost:3000`).

## Step 1: Install Node.js

You need Node.js to run Next.js. Download and install from:
- **https://nodejs.org/** (Download the LTS version)

After installing, restart your terminal/PowerShell.

## Step 2: Install Dependencies

Open PowerShell in the frontend directory:

```powershell
cd "C:\Users\josht\Documents\New folder\USC-Racing-config\frontend"
npm install
```

This will install all required packages (Next.js, React, Tailwind, etc.)

## Step 3: Start the Backend (if not running)

In one terminal:

```powershell
cd "C:\Users\josht\Documents\New folder\USC-Racing-config\backend"
python main.py
```

Backend should run on `http://localhost:8000`

## Step 4: Start the Next.js Frontend

In a **second terminal**:

```powershell
cd "C:\Users\josht\Documents\New folder\USC-Racing-config\frontend"
npm run dev
```

Frontend will run on `http://localhost:3000`

## Step 5: View the New UI

Open your browser to: **http://localhost:3000**

You should now see:
- ✅ White/light background (Microsoft Word style)
- ✅ Blue title bar at the top
- ✅ Ribbon toolbar
- ✅ Clean, professional design

## Troubleshooting

### "npm is not recognized"
- Node.js is not installed or not in PATH
- Install Node.js from nodejs.org
- Restart your terminal after installation

### "Port 3000 already in use"
- Another app is using port 3000
- Change the port: `npm run dev -- -p 3001`
- Then visit `http://localhost:3001`

### Still seeing old UI?
- Make sure you're visiting `http://localhost:3000` (not 8000)
- The old frontend is still at `http://localhost:8000`
- The new frontend is at `http://localhost:3000`

## What Changed?

- **Old frontend**: Dark theme, vanilla JS, at `localhost:8000`
- **New frontend**: Light/Word-style theme, Next.js, at `localhost:3000`

Both can run simultaneously - they're separate applications!
