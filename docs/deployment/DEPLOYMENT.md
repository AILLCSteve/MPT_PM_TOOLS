# Deployment Guide - PM Tools Suite

Complete step-by-step guide for deploying the PM Tools Suite to production.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Render Deployment (Recommended)](#render-deployment)
3. [Heroku Deployment](#heroku-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Custom VPS Deployment](#custom-vps-deployment)
6. [Post-Deployment Steps](#post-deployment-steps)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Pre-Deployment Checklist

Before deploying, ensure you have completed:

- [ ] Updated branding assets in `shared/assets/images/`
- [ ] Customized color scheme in `shared/assets/css/common.css`
- [ ] Set up environment variables (copy `.env.example` to `.env`)
- [ ] Changed default `SECRET_KEY` in production
- [ ] Tested all tools locally
- [ ] Reviewed and updated footer links (About, Support, etc.)
- [ ] Set `DEBUG=false` for production
- [ ] Created a Git repository with all code

---

## Render Deployment

### Why Render?

- **Free Tier Available**: Great for testing and small projects
- **Auto-Deploy**: Automatic deploys from Git
- **Zero Config**: Works with included `render.yaml`
- **HTTPS Included**: SSL certificates automatically provisioned
- **Easy Scaling**: Upgrade plans as needed

### Step-by-Step Process

#### 1. Prepare Your Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial deployment commit"

# Create GitHub/GitLab repository and push
git remote add origin https://github.com/yourusername/pm-tools-suite.git
git branch -M main
git push -u origin main
```

#### 2. Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub/GitLab
3. Authorize Render to access your repositories

#### 3. Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Select **"Build and deploy from a Git repository"**
3. Choose your repository
4. Render auto-detects `render.yaml`

#### 4. Review Configuration

Render will show detected settings:
- **Name**: `pm-tools-suite` (or customize)
- **Region**: Choose closest to users
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`

#### 5. Set Environment Variables

In Render dashboard, add:

| Key | Value | Notes |
|-----|-------|-------|
| `SECRET_KEY` | Auto-generated | Click "Generate" |
| `DEBUG` | `false` | Production mode |
| `LOG_LEVEL` | `INFO` | Or `WARNING` for less verbose |

#### 6. Deploy

1. Click **"Create Web Service"**
2. Render builds and deploys (takes 2-5 minutes)
3. Monitor build logs for errors
4. Once deployed, you'll get a URL: `https://pm-tools-suite.onrender.com`

#### 7. Test Deployment

Visit your deployment URL:
```
https://your-app-name.onrender.com/
https://your-app-name.onrender.com/health
https://your-app-name.onrender.com/cipp-analyzer
https://your-app-name.onrender.com/progress-estimator
```

### Render Configuration Details

#### Free Tier Limitations

- **Spins down after 15 min inactivity** (first request takes ~30s to wake)
- **750 hours/month free**
- **512MB RAM**

To avoid spin-down, upgrade to **Starter Plan ($7/month)**:
- Always online
- More resources
- Better performance

#### Custom Domain

1. In Render dashboard → **Settings** → **Custom Domain**
2. Add your domain (e.g., `tools.yourcompany.com`)
3. Update DNS records as shown by Render
4. SSL certificate auto-provisioned

#### Automatic Deploys

Render automatically deploys when you push to `main`:
```bash
git add .
git commit -m "Updated feature"
git push origin main
# Render auto-deploys in 1-2 minutes
```

---

## Heroku Deployment

### Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- Heroku account

### Deployment Steps

#### 1. Create Procfile

Already included! Contents:
```
web: gunicorn --bind 0.0.0.0:$PORT app:app
```

#### 2. Login to Heroku

```bash
heroku login
```

#### 3. Create Heroku App

```bash
heroku create pm-tools-suite

# Or specify region:
heroku create pm-tools-suite --region us
```

#### 4. Set Environment Variables

```bash
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
heroku config:set DEBUG=false
heroku config:set LOG_LEVEL=INFO
```

#### 5. Deploy

```bash
git push heroku main
```

#### 6. Open Application

```bash
heroku open
```

### Heroku Add-ons (Optional)

#### Logging
```bash
heroku addons:create papertrail:chopper
heroku addons:open papertrail
```

#### Monitoring
```bash
heroku addons:create newrelic:wayne
```

---

## Docker Deployment

### Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBUG=false

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
```

### Build and Run

```bash
# Build image
docker build -t pm-tools-suite .

# Run container
docker run -d -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e DEBUG=false \
  --name pm-tools \
  pm-tools-suite

# View logs
docker logs -f pm-tools

# Stop container
docker stop pm-tools
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

---

## Custom VPS Deployment

For AWS, DigitalOcean, Linode, etc.

### Prerequisites

- VPS with Ubuntu 20.04+ or similar
- Root/sudo access
- Domain name (optional)

### Installation Steps

#### 1. Connect to VPS

```bash
ssh user@your-server-ip
```

#### 2. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and tools
sudo apt install python3 python3-pip python3-venv nginx -y
```

#### 3. Create Application User

```bash
sudo adduser pmtools
sudo usermod -aG sudo pmtools
su - pmtools
```

#### 4. Deploy Application

```bash
# Clone repository
git clone https://github.com/yourusername/pm-tools-suite.git
cd pm-tools-suite

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 5. Configure Gunicorn Service

Create `/etc/systemd/system/pmtools.service`:

```ini
[Unit]
Description=PM Tools Suite
After=network.target

[Service]
User=pmtools
WorkingDirectory=/home/pmtools/pm-tools-suite
Environment="PATH=/home/pmtools/pm-tools-suite/venv/bin"
ExecStart=/home/pmtools/pm-tools-suite/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl enable pmtools
sudo systemctl start pmtools
sudo systemctl status pmtools
```

#### 6. Configure Nginx

Create `/etc/nginx/sites-available/pmtools`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /shared/ {
        alias /home/pmtools/pm-tools-suite/shared/;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/pmtools /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. Setup SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## Post-Deployment Steps

### 1. Test All Endpoints

```bash
# Health check
curl https://your-domain.com/health

# Test each tool
curl https://your-domain.com/cipp-analyzer
curl https://your-domain.com/progress-estimator
```

### 2. Setup Monitoring

#### Uptime Monitoring

Use services like:
- [UptimeRobot](https://uptimerobot.com/) (Free)
- [Pingdom](https://www.pingdom.com/)
- [StatusCake](https://www.statuscake.com/)

Monitor URL: `https://your-domain.com/health`

#### Application Monitoring

- **Sentry**: Error tracking
- **New Relic**: Performance monitoring
- **DataDog**: Full-stack observability

### 3. Setup Backups

For VPS deployments:
```bash
# Create backup script
#!/bin/bash
tar -czf /backups/pmtools-$(date +%Y%m%d).tar.gz /home/pmtools/pm-tools-suite

# Add to crontab (daily backup at 2 AM)
0 2 * * * /home/pmtools/backup.sh
```

### 4. Configure Analytics (Optional)

Add Google Analytics to `index.html`:
```html
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

---

## Monitoring and Maintenance

### View Logs

**Render:**
- Dashboard → Logs tab

**Heroku:**
```bash
heroku logs --tail
```

**VPS (systemd):**
```bash
sudo journalctl -u pmtools -f
```

### Update Application

**Render/Heroku:**
```bash
git add .
git commit -m "Update"
git push origin main
# Auto-deploys
```

**VPS:**
```bash
cd /home/pmtools/pm-tools-suite
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart pmtools
```

### Health Checks

Set up automated health checks:
```bash
# Test script
#!/bin/bash
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://your-domain.com/health)
if [ $RESPONSE != "200" ]; then
    echo "Health check failed: $RESPONSE"
    # Send alert email/SMS
fi
```

### Performance Optimization

1. **Enable Caching** (Nginx):
```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

2. **Compress Responses**:
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

3. **Scale Workers**:
```bash
# Increase Gunicorn workers
gunicorn --workers 4 --threads 2 app:app
```

---

## Troubleshooting

### Application Won't Start

1. Check logs for errors
2. Verify environment variables set
3. Test locally with same configuration
4. Check Python version compatibility

### 502 Bad Gateway (Nginx)

1. Verify Gunicorn is running: `sudo systemctl status pmtools`
2. Check Nginx config: `sudo nginx -t`
3. Review Nginx logs: `sudo tail -f /var/log/nginx/error.log`

### Slow Performance

1. Increase Gunicorn workers
2. Enable caching
3. Optimize database queries (if added later)
4. Use CDN for static assets
5. Upgrade server resources

### SSL Certificate Issues

```bash
# Renew Let's Encrypt certificate
sudo certbot renew
sudo systemctl reload nginx
```

---

## Security Best Practices

1. **Never commit `.env` file** (already in `.gitignore`)
2. **Use strong SECRET_KEY** in production
3. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```
4. **Enable firewall**:
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```
5. **Regular security updates**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## Cost Estimates

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| **Render** | Yes (750h/mo, sleeps) | $7+/month | Easy deployment |
| **Heroku** | Yes (550h/mo, sleeps) | $7+/month | Quick prototypes |
| **DigitalOcean** | No | $6+/month | Full control |
| **AWS Lightsail** | No | $3.50+/month | AWS integration |

---

## Support

For deployment issues:
1. Check logs first
2. Review this guide
3. Check [Flask docs](https://flask.palletsprojects.com/)
4. Contact support: support@example.com

---

**Happy Deploying! 🚀**
