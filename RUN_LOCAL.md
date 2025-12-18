# Run on Localhost - Quick Guide

## Option 1: Use the Script (Easiest)

Just run:

```bash
./run_server.sh
```

This will:
- Create a virtual environment (if needed)
- Install all dependencies
- Start the server on `http://localhost:8000`

## Option 2: Manual Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Run the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Access Your App

Once running, open:

- **Main App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Environment Variables (Optional)

Create a `.env` file in the project root if you need custom settings:

```bash
TEL_HOST=0.0.0.0
TEL_PORT=8000
TEL_CORS_ORIGINS=*
TEL_LOG_ENABLED=true
MOTEC_ENABLED=false
```

## Troubleshooting

### Port Already in Use

If port 8000 is taken, change it:

```bash
# In .env file:
TEL_PORT=8001

# Or in terminal:
cd backend
uvicorn main:app --port 8001
```

### Python Version

Make sure you're using Python 3.11+:

```bash
python3 --version
```

### Dependencies Not Installing

Try:

```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

## That's It!

No Vercel, no deployment headaches - just run it locally. 🚀

