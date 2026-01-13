# Production Deployment Guide

Complete guide for deploying USC Racing Parameter Management System to production (Raspberry Pi).

## Prerequisites

- Raspberry Pi with Raspberry Pi OS
- Python 3.11+ installed
- Nginx installed (optional, for reverse proxy)

## Step 1: Install Dependencies

```bash
cd USC-Racing-config/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Configure Environment

Create `.env` file in project root:

```bash
HOST=0.0.0.0
PORT=8000
DATA_DIR=/home/pi/USC-Racing-config/data
CORS_ORIGINS=*
```

## Step 3: Set Up Systemd Service (Recommended)

1. Copy service file:
```bash
sudo cp deploy/systemd/usc-racing.service /etc/systemd/system/
```

2. Edit service file to match your paths:
```bash
sudo nano /etc/systemd/system/usc-racing.service
```

3. Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable usc-racing.service
sudo systemctl start usc-racing.service
```

4. Check status:
```bash
sudo systemctl status usc-racing.service
```

5. View logs:
```bash
sudo journalctl -u usc-racing.service -f
```

## Step 4: Set Up Nginx Reverse Proxy (Optional)

1. Install Nginx:
```bash
sudo apt update
sudo apt install nginx
```

2. Copy configuration:
```bash
sudo cp deploy/nginx/usc-racing.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/usc-racing.conf /etc/nginx/sites-enabled/
```

3. Test and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Step 5: Run Tests

Before deploying, run the test suite:

```bash
cd USC-Racing-config
source backend/venv/bin/activate
pytest tests/ -v
```

## Step 6: Firewall Configuration

Allow port 8000 (or 80 if using Nginx):

```bash
sudo ufw allow 8000/tcp
# Or if using Nginx:
sudo ufw allow 80/tcp
```

## Maintenance

### Restart Service
```bash
sudo systemctl restart usc-racing.service
```

### Update Application
```bash
cd USC-Racing-config
git pull  # If using git
source backend/venv/bin/activate
pip install -r backend/requirements.txt
sudo systemctl restart usc-racing.service
```

### Backup Database
```bash
cp data/parameters.db data/parameters.db.backup.$(date +%Y%m%d)
```

### View Logs
```bash
# Systemd logs
sudo journalctl -u usc-racing.service -n 100

# Application logs (if configured)
tail -f .cursor/debug.log
```

## Troubleshooting

### Service won't start
- Check paths in service file
- Verify Python virtual environment exists
- Check file permissions
- View logs: `sudo journalctl -u usc-racing.service`

### Port already in use
- Check what's using port 8000: `sudo lsof -i :8000`
- Change PORT in .env file
- Update service file if needed

### Database errors
- Check data directory permissions
- Verify database file exists
- Check disk space: `df -h`

## Security Considerations

1. **Change default admin password** immediately after first login
2. **Use HTTPS** in production (set up SSL certificate)
3. **Restrict network access** if only needed locally
4. **Regular backups** of database and uploaded files
5. **Keep dependencies updated** for security patches
