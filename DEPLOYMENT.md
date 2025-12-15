# USC Racing Deployment Guide

This guide will help you deploy the USC Racing application to a server.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- A server with at least 2GB RAM and 10GB disk space
- Domain name (optional, for production)

## Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd "USC Racing"
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Deploy:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## Manual Deployment

If you prefer to deploy manually:

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Production Deployment

For production deployment, consider the following:

### 1. Use a Reverse Proxy (Nginx)

Create an `nginx.conf` file:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. SSL/HTTPS Setup

Use Let's Encrypt with Certbot:

```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Environment Variables

Update `.env` with production values:
- Set `NODE_ENV=production`
- Update `REACT_APP_API_URL` to your production domain
- Add any required API keys or database URLs

### 4. Firewall Configuration

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (if needed)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

## Cloud Deployment Options

### AWS (EC2 + ECS)

1. Create an EC2 instance
2. Install Docker and Docker Compose
3. Clone repository and run `./deploy.sh`
4. Configure security groups to allow ports 80, 443, 3000, 8000

### DigitalOcean

1. Create a Droplet (Ubuntu 22.04)
2. Follow the Quick Start guide above
3. Configure firewall in DigitalOcean dashboard

### Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: docker-compose up
   ```
3. Deploy: `heroku container:push web`

### Vercel/Netlify (Frontend only)

For frontend-only deployment:
1. Build frontend: `cd frontend && npm run build`
2. Deploy the `build` or `.next` folder to Vercel/Netlify
3. Configure backend API URL in environment variables

## Monitoring and Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup Data

```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

## Troubleshooting

### Containers won't start

1. Check logs: `docker-compose logs`
2. Verify Docker is running: `docker ps`
3. Check port availability: `netstat -tulpn | grep -E '3000|8000'`

### Port already in use

Change ports in `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Change host port
```

### Build failures

1. Check Dockerfile syntax
2. Verify all dependencies are listed
3. Check disk space: `df -h`

## Support

For issues or questions, check the logs first:
```bash
docker-compose logs -f
```


