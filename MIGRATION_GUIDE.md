# Migration to Next.js + Tailwind CSS

## What Changed

The frontend has been completely modernized with:

### ✅ New Stack
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for modern styling
- **Framer Motion** for smooth animations
- **Headless UI** for accessible components
- **Heroicons** for consistent icons

### ✅ Improved Features
- Modern, responsive design
- Smooth animations and transitions
- Better component organization
- Type-safe codebase
- Improved accessibility

## Running Both Servers

### Option 1: Run Separately (Recommended for Development)

**Terminal 1 - FastAPI Backend:**
```bash
cd backend
python main.py
# Backend runs on http://localhost:8000
```

**Terminal 2 - Next.js Frontend:**
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:3000
```

### Option 2: Use Next.js Proxy

The Next.js app proxies API requests to the FastAPI backend automatically via `next.config.js` rewrites.

## Architecture

```
┌─────────────────┐
│   Next.js App   │  http://localhost:3000
│  (Frontend)     │
└────────┬────────┘
         │ API calls (/api/*)
         │ (proxied via Next.js)
         ▼
┌─────────────────┐
│  FastAPI Backend│  http://localhost:8000
│  (Backend)      │
└─────────────────┘
```

## Key Differences

### Old Frontend (Vanilla JS)
- Server-rendered HTML templates
- Vanilla JavaScript
- Custom CSS
- Direct DOM manipulation

### New Frontend (Next.js)
- React components
- TypeScript
- Tailwind CSS utility classes
- Component-based architecture
- Client-side routing

## Migration Status

✅ **Completed:**
- All pages migrated
- All components created
- API integration working
- Authentication flow
- Parameter management
- User management
- MoTeC file management
- Queue system
- Session tracking

## Next Steps

1. Install dependencies: `cd frontend && npm install`
2. Start backend: `cd backend && python main.py`
3. Start frontend: `cd frontend && npm run dev`
4. Visit http://localhost:3000

## Backward Compatibility

The old frontend files are still in `frontend/templates/` and `frontend/static/` but are no longer used. The FastAPI backend can still serve the old frontend if needed by accessing `http://localhost:8000` directly.
