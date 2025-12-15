# USC Racing

## Quick Start

### Local Development

1. **Backend:**
   ```bash
   cd backend
   # Install dependencies (Python/Node.js/Go)
   # Run server
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

**Quick deploy:**
```bash
./deploy.sh
```

## Project Structure

```
USC Racing/
├── backend/          # Backend API
├── frontend/         # Frontend application
├── data/             # Data storage
├── docker-compose.yml
├── deploy.sh         # Deployment script
└── DEPLOYMENT.md     # Deployment guide
```

## Services

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000

## Requirements

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ or Go 1.21+ (depending on backend)


