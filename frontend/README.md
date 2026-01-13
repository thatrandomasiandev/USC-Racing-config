# USC Racing Frontend - Next.js + Tailwind CSS

Modern frontend for USC Racing Parameter Management System built with Next.js 14 and Tailwind CSS.

## Features

- ⚡ **Next.js 14** - React framework with App Router
- 🎨 **Tailwind CSS** - Utility-first CSS framework
- 🎭 **Headless UI** - Accessible UI components
- ✨ **Framer Motion** - Smooth animations
- 🔒 **Server-side authentication** - Secure session management
- 📱 **Responsive design** - Works on all devices

## Getting Started

### Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Main dashboard page
│   ├── login/             # Login page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles with Tailwind
├── components/             # React components
│   ├── Header.tsx
│   ├── ParametersTable.tsx
│   ├── EditParameterModal.tsx
│   ├── HistoryModal.tsx
│   ├── QueueSection.tsx
│   ├── MoTecFiles.tsx
│   ├── SessionsSection.tsx
│   └── UserManagementModal.tsx
└── public/                # Static assets
```

## Backend Integration

The frontend communicates with the FastAPI backend running on `http://localhost:8000`. 

API routes are proxied through Next.js rewrites (see `next.config.js`).

## Styling

This project uses Tailwind CSS with custom colors matching USC Racing branding:

- **Primary**: `#990000` (USC Red)
- **Secondary**: `#FFB81C` (USC Gold)
- **Dark**: `#0a0a0a` (Background)
- **Card**: `#1a1a1a` (Card background)

Custom components are defined in `globals.css` using Tailwind's `@layer components`.

## Development

### Adding New Components

1. Create component in `components/` directory
2. Use Tailwind utility classes for styling
3. Import and use in pages or other components

### API Routes

API calls should use the `/api/*` path which is automatically proxied to the FastAPI backend.

Example:
```typescript
const response = await fetch('/api/parameters', {
  credentials: 'include', // Important for session cookies
})
```

## Deployment

See the main project `DEPLOYMENT.md` for production deployment instructions.
