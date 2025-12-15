# Quick Deployment Guide

## Deploy to Remote Server

### 1. Copy files to server
```bash
# From your local machine
scp -r "USC Racing" user@your-server:/opt/
# Or use git if you have a repo
```

### 2. SSH into server
```bash
ssh user@your-server
cd /opt/USC\ Racing
```

### 3. Set up environment
```bash
# Ensure .env exists (already created from config.example.env)
# Edit .env if needed:
nano .env
```

### 4. Deploy with Docker
```bash
chmod +x deploy.sh
./deploy.sh
```

### 5. Check status
```bash
docker-compose ps
docker-compose logs -f
```

### 6. Access application
- Application: http://your-server-ip:8000
- API: http://your-server-ip:8000/api
- API Docs: http://your-server-ip:8000/docs

## Deploy without Docker (Direct Python)

### 1. On server, install Python 3.11+
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. Run server
```bash
cd "/opt/USC Racing"
chmod +x run_server.sh
./run_server.sh
```

### 3. Use systemd for auto-start (optional)
Create `/etc/systemd/system/usc-racing.service`:
```ini
[Unit]
Description=USC Racing Trackside Telemetry
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/USC Racing
ExecStart=/opt/USC Racing/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable usc-racing
sudo systemctl start usc-racing
sudo systemctl status usc-racing
```

## Production Setup with Nginx

### 1. Install Nginx
```bash
sudo apt install nginx
```

### 2. Copy nginx config
```bash
sudo cp nginx.conf /etc/nginx/sites-available/usc-racing
sudo ln -s /etc/nginx/sites-available/usc-racing /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Update nginx.conf
Edit `/etc/nginx/sites-available/usc-racing` and change:
- `server_name your-domain.com;` to your actual domain
- Or use `server_name _;` for IP-based access

### 4. SSL with Let's Encrypt (optional)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Firewall Configuration

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow direct access (if not using nginx)
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable
```

## Troubleshooting

### Check if port is in use
```bash
sudo netstat -tulpn | grep 8000
```

### View logs
```bash
# Docker
docker-compose logs -f backend

# Direct Python
tail -f /opt/USC\ Racing/data/*.log
```

### Restart service
```bash
# Docker
docker-compose restart

# Systemd
sudo systemctl restart usc-racing
```

