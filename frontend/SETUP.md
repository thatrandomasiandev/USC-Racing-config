# Next.js Frontend Setup Guide

## Prerequisites

- Node.js 18+ installed
- FastAPI backend running on `http://localhost:8000`

## Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

## Running the Development Server

1. **Start the FastAPI backend first** (in a separate terminal):
   ```bash
   cd ../backend
   python main.py
   ```

2. **Start Next.js dev server** (in frontend directory):
   ```bash
   npm run dev
   ```

3. **Open browser:**
   - Next.js frontend: http://localhost:3000
   - FastAPI backend: http://localhost:8000

## Features

### Modern UI Components
- ✅ Responsive design with Tailwind CSS
- ✅ Smooth animations with Framer Motion
- ✅ Accessible components with Headless UI
- ✅ Heroicons for consistent iconography

### Functionality
- ✅ Parameter management with real-time updates
- ✅ Queue system for admin approval
- ✅ User management (admin only)
- ✅ MoTeC file upload and management
- ✅ Session tracking and history
- ✅ Parameter history with full audit trail

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Main dashboard
│   ├── login/             # Login page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Tailwind styles
├── components/             # React components
│   ├── Header.tsx
│   ├── ParametersTable.tsx
│   ├── EditParameterModal.tsx
│   ├── HistoryModal.tsx
│   ├── QueueSection.tsx
│   ├── MoTecFiles.tsx
│   ├── SessionsSection.tsx
│   └── UserManagementModal.tsx
└── package.json
```

## Building for Production

```bash
npm run build
npm start
```

## Troubleshooting

### CORS Issues
If you see CORS errors, make sure:
1. FastAPI backend is running
2. Backend CORS is configured to allow `http://localhost:3000`

### Authentication Issues
- Make sure cookies are being sent (check browser DevTools > Network)
- Verify backend session middleware is working
- Check that credentials: 'include' is set on all fetch requests

### Port Conflicts
- Next.js defaults to port 3000
- Change in `package.json` scripts if needed: `"dev": "next dev -p 3001"`
