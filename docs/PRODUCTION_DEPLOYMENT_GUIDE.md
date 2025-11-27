# 🚀 **Production Deployment Guide - Homescreen Project**

## 📋 **Prerequisites**

### **1. OpenAI Organization Verification**
**CRITICAL**: Complete this before deployment

1. **Visit**: https://platform.openai.com/settings/organization/general
2. **Click**: "Verify Organization" button
3. **Provide**: Required business information and documentation
4. **Wait**: 1-3 business days for approval
5. **Verify**: Run `python3 verify_organization.py` to confirm access

### **2. System Requirements**
- **Server**: Linux (Ubuntu 20.04+ recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 20GB minimum, 50GB recommended
- **Network**: Stable internet connection for AI API calls
- **Domain**: SSL certificate for HTTPS (required for production)

### **3. Required Accounts & Keys**
- **OpenAI API Key**: With organization verification complete
- **Domain & SSL**: For HTTPS deployment
- **Database**: PostgreSQL instance (local or cloud)
- **Redis**: For caching (optional but recommended)

---

## 🔧 **Step 1: Server Preparation**

### **Update System**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget nginx postgresql postgresql-contrib redis-server
```

### **Install Docker & Docker Compose**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### **Configure Firewall**
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

---

## 📦 **Step 2: Application Deployment**

### **Clone Repository**
```bash
cd /opt
sudo git clone https://github.com/yourusername/homescreen.git
sudo chown -R $USER:$USER homescreen
cd homescreen
```

### **Environment Configuration**
```bash
# Create production environment file
cp .env.example .env.production

# Edit environment variables
nano .env.production
```

**Required Environment Variables:**
```bash
# Django Settings
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/homescreen_prod

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

### **Database Setup**
```bash
# Create database
sudo -u postgres createdb homescreen_prod
sudo -u postgres createuser homescreen_user
sudo -u postgres psql -c "ALTER USER homescreen_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE homescreen_prod TO homescreen_user;"
```

### **Build and Deploy**
```bash
# Build production images
docker-compose -f docker-compose.yml build

# Start services
docker-compose -f docker-compose.yml up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

---

## 🔍 **Step 3: Production Readiness Verification**

### **Run Comprehensive Checks**
```bash
# Production readiness assessment
python3 production_readiness_checker.py

# Expected output:
# 🚀 PRODUCTION READINESS ASSESSMENT
# ✅ Environment Configuration: Ready
# ✅ AI Services: Operational
# ✅ Performance Optimization: Ready
# ✅ Monitoring Systems: Active
# 🎉 STATUS: READY FOR PRODUCTION
```

### **Test AI Services**
```bash
# Verify OpenAI access
python3 verify_organization.py

# Test reference system
python3 test_reference_integration.py

# Run comprehensive feature tests
python3 test_all_phase3_features.py
```

### **Performance Verification**
```bash
# Test image generation
python3 comprehensive_quality_test.py

# Monitor performance metrics
docker-compose logs -f backend | grep "Performance Summary"
```

---

## 🌐 **Step 4: Web Server Configuration**

### **Nginx Configuration**
```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/homescreen
```

**Nginx Configuration File:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    client_max_body_size 50M;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Static files
    location /static/ {
        alias /opt/homescreen/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/homescreen/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
```

### **Enable Nginx Configuration**
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/homescreen /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 📊 **Step 5: Monitoring Setup**

### **Health Checks**
```bash
# Backend health
curl https://yourdomain.com/api/health/

# AI services health
curl https://yourdomain.com/api/ai-services/status/

# Performance metrics
curl https://yourdomain.com/api/monitoring/metrics/
```

### **Log Monitoring**
```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Monitor AI service performance
tail -f /var/log/homescreen/ai_services.log

# Monitor system resources
htop
df -h
```

### **Automated Monitoring**
```bash
# Create monitoring script
sudo nano /opt/homescreen/scripts/health_check.sh
```

**Health Check Script:**
```bash
#!/bin/bash
# Health check script for homescreen application

LOG_FILE="/var/log/homescreen/health_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check backend health
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://yourdomain.com/api/health/)
if [ "$BACKEND_STATUS" != "200" ]; then
    echo "$DATE - Backend health check failed: $BACKEND_STATUS" >> $LOG_FILE
fi

# Check AI services
AI_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://yourdomain.com/api/ai-services/status/)
if [ "$AI_STATUS" != "200" ]; then
    echo "$DATE - AI services health check failed: $AI_STATUS" >> $LOG_FILE
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "$DATE - Disk usage high: $DISK_USAGE%" >> $LOG_FILE
fi

echo "$DATE - Health check completed" >> $LOG_FILE
```

### **Setup Cron Job**
```bash
# Make script executable
sudo chmod +x /opt/homescreen/scripts/health_check.sh

# Add to crontab (run every 5 minutes)
sudo crontab -e
# Add line: */5 * * * * /opt/homescreen/scripts/health_check.sh
```

---

## 🔒 **Step 6: Security Hardening**

### **SSL/TLS Configuration**
```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### **Security Headers**
Add to Nginx configuration:
```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

### **Fail2Ban Setup**
```bash
# Install Fail2Ban
sudo apt install fail2ban

# Configure for Nginx
sudo nano /etc/fail2ban/jail.local
```

**Fail2Ban Configuration:**
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true

[nginx-noproxy]
enabled = true
```

---

## 🚀 **Step 7: Final Deployment**

### **Start All Services**
```bash
# Start application services
docker-compose -f docker-compose.yml up -d

# Verify all containers are running
docker-compose ps

# Check logs for any errors
docker-compose logs --tail=50
```

### **Performance Optimization**
```bash
# Enable Redis caching
docker-compose exec backend python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'working')
>>> print(cache.get('test'))

# Verify AI service performance
python3 -c "
from api.ai_services.providers.openai_provider import OpenAIImageGenerationService
service = OpenAIImageGenerationService(config)
metrics = service.get_performance_metrics()
print(f'Cache hit rate: {metrics[\"cache_hit_rate\"]:.1f}%')
"
```

### **Final Verification**
```bash
# Run complete system test
python3 test_all_phase3_features.py

# Generate test image to verify end-to-end functionality
python3 comprehensive_quality_test.py

# Check production readiness one final time
python3 production_readiness_checker.py
```

---

## 📈 **Step 8: Post-Deployment Monitoring**

### **Performance Metrics**
- **Response Time**: < 30 seconds for image generation
- **Quality Score**: > 0.75 average (target: 0.85)
- **Cache Hit Rate**: > 30% for optimal performance
- **Error Rate**: < 5% for production stability

### **Daily Monitoring Tasks**
1. **Check application logs** for errors
2. **Monitor disk space** and system resources
3. **Verify AI service health** and performance
4. **Review quality metrics** and user feedback
5. **Check SSL certificate** expiration

### **Weekly Maintenance**
1. **Update system packages**: `sudo apt update && sudo apt upgrade`
2. **Backup database**: `pg_dump homescreen_prod > backup_$(date +%Y%m%d).sql`
3. **Review performance metrics** and optimize if needed
4. **Check for application updates** and security patches

---

## 🆘 **Troubleshooting**

### **Common Issues**

**AI Service Errors:**
```bash
# Check OpenAI API status
curl https://status.openai.com/

# Verify API key
python3 verify_organization.py

# Check service logs
docker-compose logs backend | grep "AI Service"
```

**Performance Issues:**
```bash
# Check system resources
htop
df -h

# Monitor database performance
docker-compose exec db psql -U homescreen_user -d homescreen_prod -c "SELECT * FROM pg_stat_activity;"

# Check Redis cache
docker-compose exec redis redis-cli info memory
```

**SSL/Certificate Issues:**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Test SSL configuration
openssl s_client -connect yourdomain.com:443
```

---

## 🎯 **Success Criteria**

### **Deployment Complete When:**
- ✅ All services running without errors
- ✅ AI image generation working with quality > 0.75
- ✅ SSL certificate installed and working
- ✅ Monitoring and health checks active
- ✅ Performance metrics within acceptable ranges
- ✅ Security hardening implemented
- ✅ Backup procedures in place

### **Production Ready Indicators:**
- **Uptime**: 99.9% availability
- **Performance**: < 30s generation time
- **Quality**: > 0.75 average score
- **Security**: A+ SSL rating
- **Monitoring**: Real-time alerts working

**🎉 Congratulations! Your Homescreen application is now deployed and ready for production use.**
