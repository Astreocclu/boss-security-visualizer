# Deployment Guide

## Overview

This guide covers deployment options for the Homescreen Visualizer application, including development, staging, and production environments.

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Nginx (for production)

## Environment Configuration

### Environment Variables

Create environment files for each environment:

#### Production (.env.production)
```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-production-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@db:5432/homescreen_prod
REDIS_URL=redis://redis:6379/0

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# Email (configure based on your provider)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Storage (AWS S3)
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

#### Staging (.env.staging)
```bash
DEBUG=False
SECRET_KEY=staging-secret-key
ALLOWED_HOSTS=staging.yourdomain.com
DATABASE_URL=postgresql://user:password@db:5432/homescreen_staging
REDIS_URL=redis://redis:6379/1
```

#### Development (.env.development)
```bash
DEBUG=True
SECRET_KEY=dev-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DATABASE_URL=postgresql://homescreen:homescreen123@localhost:5432/homescreen_dev
REDIS_URL=redis://localhost:6379/0
```

## Docker Deployment

### Production Deployment

1. **Build the Docker image:**
```bash
docker build -t homescreen:latest .
```

2. **Run with Docker Compose:**
```bash
docker-compose up -d
```

3. **Initialize the database:**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
docker-compose exec web python manage.py createsuperuser
```

### Development Deployment

1. **Run development environment:**
```bash
docker-compose -f docker-compose.dev.yml up --build
```

2. **Access the application:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Admin: http://localhost:8000/admin

## Manual Deployment

### Backend Deployment

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure database:**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

3. **Create superuser:**
```bash
python manage.py createsuperuser
```

4. **Run with Gunicorn:**
```bash
gunicorn homescreen_project.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class gevent \
  --worker-connections 1000 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --timeout 30 \
  --keep-alive 2
```

### Frontend Deployment

1. **Install dependencies:**
```bash
cd frontend
npm ci
```

2. **Build for production:**
```bash
npm run build:prod
```

3. **Serve with Nginx:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS with Fargate

1. **Create ECR repository:**
```bash
aws ecr create-repository --repository-name homescreen
```

2. **Build and push image:**
```bash
docker build -t homescreen .
docker tag homescreen:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/homescreen:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/homescreen:latest
```

3. **Create ECS task definition:**
```json
{
  "family": "homescreen",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "homescreen",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/homescreen:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:password@rds-endpoint:5432/homescreen"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/homescreen",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Using AWS Elastic Beanstalk

1. **Install EB CLI:**
```bash
pip install awsebcli
```

2. **Initialize application:**
```bash
eb init homescreen
```

3. **Create environment:**
```bash
eb create production
```

4. **Deploy:**
```bash
eb deploy
```

### Google Cloud Platform

#### Using Google Cloud Run

1. **Build and push to Container Registry:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/homescreen
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy homescreen \
  --image gcr.io/PROJECT_ID/homescreen \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Heroku Deployment

1. **Create Heroku app:**
```bash
heroku create your-app-name
```

2. **Add PostgreSQL addon:**
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

3. **Add Redis addon:**
```bash
heroku addons:create heroku-redis:hobby-dev
```

4. **Set environment variables:**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
```

5. **Deploy:**
```bash
git push heroku main
```

6. **Run migrations:**
```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

## Database Setup

### PostgreSQL Configuration

1. **Create database and user:**
```sql
CREATE DATABASE homescreen;
CREATE USER homescreen WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE homescreen TO homescreen;
ALTER USER homescreen CREATEDB;
```

2. **Configure PostgreSQL for production:**
```postgresql
# postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Redis Configuration

```redis
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## SSL/TLS Configuration

### Let's Encrypt with Certbot

1. **Install Certbot:**
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. **Obtain certificate:**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. **Auto-renewal:**
```bash
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### Application Monitoring

1. **Sentry for error tracking:**
```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

2. **Health checks:**
```python
# urls.py
from django_health_check import urls as health_urls

urlpatterns = [
    path('health/', include(health_urls)),
]
```

### Log Configuration

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/homescreen.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

## Backup and Recovery

### Database Backup

```bash
# Backup
pg_dump -h localhost -U homescreen homescreen > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
psql -h localhost -U homescreen homescreen < backup_20231201_120000.sql
```

### Media Files Backup

```bash
# Backup to S3
aws s3 sync /app/media/ s3://your-backup-bucket/media/

# Restore from S3
aws s3 sync s3://your-backup-bucket/media/ /app/media/
```

## Performance Optimization

### Database Optimization

1. **Enable query optimization:**
```python
# settings.py
DATABASES['default']['OPTIONS'] = {
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    'charset': 'utf8mb4',
}
```

2. **Connection pooling:**
```python
# Install: pip install django-db-pool
DATABASES['default']['ENGINE'] = 'django_db_pool.backends.postgresql'
DATABASES['default']['POOL_OPTIONS'] = {
    'POOL_SIZE': 10,
    'MAX_OVERFLOW': 10,
}
```

### Caching

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Set secure environment variables
- [ ] Configure CORS properly
- [ ] Enable security headers
- [ ] Use strong passwords and keys
- [ ] Regular security updates
- [ ] Database access restrictions
- [ ] File upload validation
- [ ] Rate limiting enabled
- [ ] Error logging configured
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting setup

## Troubleshooting

See [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) for common issues and solutions.
