# Deployment Guide - Telegram Automation

Panduan lengkap untuk deploy aplikasi Telegram Automation ke production.

## 🚀 Deployment Options

### Option 1: Local Development
Untuk testing dan development lokal.

### Option 2: VPS/Cloud Server
Untuk production deployment dengan kontrol penuh.

### Option 3: Docker Deployment
Untuk deployment yang mudah dan portable.

## 📋 Pre-deployment Checklist

### Backend Preparation
- [ ] Update environment variables untuk production
- [ ] Set DEBUG=False
- [ ] Configure proper SECRET_KEY dan ENCRYPTION_KEY
- [ ] Test semua endpoints
- [ ] Setup database backup strategy

### Frontend Preparation  
- [ ] Update API base URL untuk production
- [ ] Build production assets
- [ ] Test responsive design
- [ ] Optimize bundle size

### Security Checklist
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Input validation active
- [ ] Error handling tidak expose sensitive data

## 🖥️ VPS/Cloud Server Deployment

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.8+
sudo apt install python3 python3-pip python3-venv -y

# Install Node.js 16+
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install nginx
sudo apt install nginx -y

# Install certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Deploy Backend
```bash
# Clone repository
git clone <your-repo-url>
cd telegram-automation/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Edit dengan konfigurasi production

# Test aplikasi
python run.py
```

### 3. Setup Systemd Service
```bash
# Buat service file
sudo nano /etc/systemd/system/telegram-automation.service
```

```ini
[Unit]
Description=Telegram Automation API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/telegram-automation/backend
Environment=PATH=/home/ubuntu/telegram-automation/backend/venv/bin
ExecStart=/home/ubuntu/telegram-automation/backend/venv/bin/python run.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Enable dan start service
sudo systemctl daemon-reload
sudo systemctl enable telegram-automation
sudo systemctl start telegram-automation
sudo systemctl status telegram-automation
```

### 4. Deploy Frontend
```bash
cd ../frontend

# Install dependencies
npm install

# Build untuk production
npm run build

# Copy build files ke nginx
sudo cp -r dist/* /var/www/html/
```

### 5. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/telegram-automation
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/telegram-automation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Setup SSL
```bash
sudo certbot --nginx -d your-domain.com
```

## 🐳 Docker Deployment

### 1. Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "run.py"]
```

### 2. Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:16-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

### 3. Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/telegram_automation.db
      - SECRET_KEY=${SECRET_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

### 4. Deploy dengan Docker
```bash
# Build dan start
docker-compose up -d

# Check logs
docker-compose logs -f

# Update aplikasi
git pull
docker-compose build
docker-compose up -d
```

## 🔧 Production Configuration

### Environment Variables
```env
# Production settings
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./data/telegram_automation.db

# Security
SECRET_KEY=your-very-secure-secret-key-here
ENCRYPTION_KEY=your-32-byte-encryption-key-here

# CORS
ALLOWED_ORIGINS=https://your-domain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/telegram-automation.log
```

### Frontend Configuration
```javascript
// src/config/production.js
export const API_BASE_URL = 'https://your-domain.com/api';
export const ENVIRONMENT = 'production';
```

## 📊 Monitoring & Maintenance

### 1. Log Monitoring
```bash
# Backend logs
sudo journalctl -u telegram-automation -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Application logs
tail -f /var/log/telegram-automation.log
```

### 2. Health Checks
```bash
# Check backend health
curl https://your-domain.com/api/health

# Check service status
sudo systemctl status telegram-automation
sudo systemctl status nginx
```

### 3. Backup Strategy
```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /path/to/telegram_automation.db /backups/telegram_automation_$DATE.db

# Setup cron job
crontab -e
# Add: 0 2 * * * /path/to/backup-script.sh
```

### 4. Update Process
```bash
# Update aplikasi
cd /path/to/telegram-automation
git pull

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart telegram-automation

# Update frontend
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/html/
```

## 🚨 Troubleshooting

### Common Issues

**1. Service Won't Start**
```bash
# Check logs
sudo journalctl -u telegram-automation -n 50

# Check permissions
ls -la /home/ubuntu/telegram-automation/backend/
```

**2. Database Permissions**
```bash
# Fix database permissions
sudo chown ubuntu:ubuntu /path/to/telegram_automation.db
chmod 664 /path/to/telegram_automation.db
```

**3. Nginx 502 Error**
```bash
# Check backend is running
curl localhost:8000/health

# Check nginx config
sudo nginx -t
```

**4. SSL Certificate Issues**
```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

## 🔒 Security Hardening

### 1. Firewall Setup
```bash
# UFW firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

### 2. Fail2Ban
```bash
# Install fail2ban
sudo apt install fail2ban -y

# Configure for nginx
sudo nano /etc/fail2ban/jail.local
```

### 3. Regular Updates
```bash
# Setup automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure unattended-upgrades
```

## 📈 Performance Optimization

### 1. Database Optimization
- Regular VACUUM untuk SQLite
- Index optimization
- Query performance monitoring

### 2. Caching
- Redis untuk session caching
- CDN untuk static assets
- API response caching

### 3. Load Balancing
- Multiple backend instances
- Nginx load balancing
- Health check endpoints

## 📞 Support & Maintenance

### Monitoring Tools
- Uptime monitoring (UptimeRobot, Pingdom)
- Error tracking (Sentry)
- Performance monitoring (New Relic)

### Backup & Recovery
- Daily database backups
- Configuration backups
- Disaster recovery plan

---

**Happy Deploying! 🚀**

