# Troubleshooting Guide

## Common Issues and Solutions

### Backend Issues

#### Database Connection Errors

**Problem:** `django.db.utils.OperationalError: could not connect to server`

**Solutions:**
1. Check database service status:
```bash
sudo systemctl status postgresql
```

2. Verify database credentials:
```bash
psql -h localhost -U homescreen -d homescreen
```

3. Check DATABASE_URL format:
```bash
# Correct format
DATABASE_URL=postgresql://username:password@host:port/database_name
```

4. For Docker environments:
```bash
docker-compose logs db
docker-compose exec db psql -U homescreen -d homescreen
```

#### Migration Issues

**Problem:** `django.db.migrations.exceptions.InconsistentMigrationHistory`

**Solutions:**
1. Reset migrations (development only):
```bash
python manage.py migrate --fake-initial
```

2. For production, create a new migration:
```bash
python manage.py makemigrations --merge
python manage.py migrate
```

3. Check migration status:
```bash
python manage.py showmigrations
```

#### JWT Token Issues

**Problem:** `Token has expired` or `Invalid token`

**Solutions:**
1. Check token expiration settings:
```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

2. Clear expired tokens:
```bash
python manage.py flushexpiredtokens
```

3. Verify token format in frontend:
```javascript
// Correct format
Authorization: Bearer <token>
```

#### File Upload Issues

**Problem:** `413 Request Entity Too Large`

**Solutions:**
1. Check Django settings:
```python
# settings.py
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
```

2. Configure Nginx:
```nginx
client_max_body_size 10M;
```

3. Check disk space:
```bash
df -h
```

#### Rate Limiting Issues

**Problem:** `429 Too Many Requests`

**Solutions:**
1. Check rate limit configuration:
```python
# In views
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
```

2. Clear rate limit cache:
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

3. Whitelist IP addresses if needed:
```python
# settings.py
RATELIMIT_SKIP_TIMEOUT = True
```

### Frontend Issues

#### Build Failures

**Problem:** `npm run build` fails

**Solutions:**
1. Clear npm cache:
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

2. Check Node.js version:
```bash
node --version  # Should be 18+
npm --version
```

3. Increase memory limit:
```bash
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

4. Check for TypeScript errors:
```bash
npm run lint
```

#### API Connection Issues

**Problem:** `Network Error` or `CORS` errors

**Solutions:**
1. Check API URL configuration:
```javascript
// .env
REACT_APP_API_URL=http://localhost:8000/api
```

2. Verify CORS settings in Django:
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

3. Check network connectivity:
```bash
curl -I http://localhost:8000/api/health/
```

#### Authentication Issues

**Problem:** User gets logged out frequently

**Solutions:**
1. Check token refresh logic:
```javascript
// Check if token is expired before API calls
if (isTokenExpired()) {
  await refreshToken();
}
```

2. Verify localStorage persistence:
```javascript
// Check if tokens are being stored
console.log(localStorage.getItem('access_token'));
console.log(localStorage.getItem('refresh_token'));
```

3. Check browser console for errors:
```javascript
// Look for authentication-related errors
console.error('Auth error:', error);
```

#### Component Rendering Issues

**Problem:** Components not rendering or showing errors

**Solutions:**
1. Check React DevTools for component tree
2. Verify prop types:
```javascript
// Add PropTypes for debugging
Component.propTypes = {
  prop: PropTypes.string.isRequired
};
```

3. Check for missing dependencies:
```bash
npm ls
npm audit fix
```

4. Clear browser cache and localStorage:
```javascript
localStorage.clear();
sessionStorage.clear();
```

### Docker Issues

#### Container Build Failures

**Problem:** Docker build fails

**Solutions:**
1. Check Dockerfile syntax:
```bash
docker build --no-cache -t homescreen .
```

2. Clear Docker cache:
```bash
docker system prune -a
```

3. Check available disk space:
```bash
docker system df
```

4. Verify base image availability:
```bash
docker pull python:3.11-slim
docker pull node:18-alpine
```

#### Container Runtime Issues

**Problem:** Containers exit unexpectedly

**Solutions:**
1. Check container logs:
```bash
docker-compose logs web
docker-compose logs db
```

2. Inspect container status:
```bash
docker-compose ps
docker inspect container_name
```

3. Check resource usage:
```bash
docker stats
```

4. Verify environment variables:
```bash
docker-compose exec web env
```

### Performance Issues

#### Slow API Responses

**Problem:** API endpoints are slow

**Solutions:**
1. Enable Django Debug Toolbar (development):
```python
# settings.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

2. Check database query performance:
```bash
python manage.py shell
>>> from django.db import connection
>>> print(connection.queries)
```

3. Add database indexes:
```python
# models.py
class Meta:
    indexes = [
        models.Index(fields=['created_at']),
        models.Index(fields=['user', 'status']),
    ]
```

4. Enable query optimization:
```python
# Use select_related and prefetch_related
queryset = VisualizationRequest.objects.select_related('user').prefetch_related('generated_images')
```

#### High Memory Usage

**Problem:** Application uses too much memory

**Solutions:**
1. Monitor memory usage:
```bash
docker stats
htop
```

2. Optimize Django settings:
```python
# settings.py
DEBUG = False  # In production
CONN_MAX_AGE = 60  # Database connection pooling
```

3. Configure Gunicorn workers:
```bash
gunicorn --workers 2 --max-requests 1000 --max-requests-jitter 100
```

4. Use memory profiling:
```python
# Install: pip install memory-profiler
@profile
def view_function(request):
    # Your code here
```

### Security Issues

#### CSRF Token Errors

**Problem:** `403 Forbidden (CSRF token missing)`

**Solutions:**
1. Ensure CSRF token in forms:
```html
{% csrf_token %}
```

2. Configure CSRF for API:
```python
# settings.py
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'https://yourdomain.com',
]
```

3. For API-only applications:
```python
# Disable CSRF for API views
from django.views.decorators.csrf import csrf_exempt
```

#### SSL/TLS Issues

**Problem:** SSL certificate errors

**Solutions:**
1. Check certificate validity:
```bash
openssl x509 -in certificate.crt -text -noout
```

2. Verify certificate chain:
```bash
openssl verify -CAfile ca-bundle.crt certificate.crt
```

3. Test SSL configuration:
```bash
curl -I https://yourdomain.com
```

### Monitoring and Debugging

#### Enable Debug Mode (Development Only)

```python
# settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

#### Database Query Debugging

```python
# Enable query logging
LOGGING['loggers'] = {
    'django.db.backends': {
        'level': 'DEBUG',
        'handlers': ['console'],
    }
}
```

#### Frontend Debugging

```javascript
// Enable React DevTools
// Add to index.js
if (process.env.NODE_ENV === 'development') {
  window.__REACT_DEVTOOLS_GLOBAL_HOOK__ = window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || {};
}

// API debugging
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

api.interceptors.request.use(request => {
  console.log('Starting Request:', request);
  return request;
});

api.interceptors.response.use(
  response => {
    console.log('Response:', response);
    return response;
  },
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
```

### Health Checks

#### Backend Health Check

```bash
curl -f http://localhost:8000/health/ || exit 1
```

#### Database Health Check

```bash
python manage.py check --database default
```

#### Frontend Health Check

```bash
curl -f http://localhost:3000/ || exit 1
```

### Log Analysis

#### Common Log Locations

```bash
# Django logs
tail -f /var/log/django/homescreen.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Docker logs
docker-compose logs -f web
docker-compose logs -f db
```

#### Log Analysis Commands

```bash
# Find errors in logs
grep -i error /var/log/django/homescreen.log

# Count requests by status code
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c

# Find slow queries
grep "slow query" /var/log/postgresql/postgresql.log
```

### Emergency Procedures

#### Application Recovery

1. **Stop all services:**
```bash
docker-compose down
```

2. **Backup current state:**
```bash
pg_dump homescreen > emergency_backup.sql
cp -r media/ media_backup/
```

3. **Restore from backup:**
```bash
psql homescreen < last_good_backup.sql
cp -r media_backup/* media/
```

4. **Restart services:**
```bash
docker-compose up -d
```

#### Database Recovery

1. **Check database integrity:**
```sql
REINDEX DATABASE homescreen;
VACUUM ANALYZE;
```

2. **Restore from backup:**
```bash
dropdb homescreen
createdb homescreen
psql homescreen < backup.sql
```

### Getting Help

#### Log Collection for Support

```bash
# Collect system information
uname -a > debug_info.txt
docker --version >> debug_info.txt
python --version >> debug_info.txt
node --version >> debug_info.txt

# Collect logs
docker-compose logs > docker_logs.txt
tail -n 100 /var/log/django/homescreen.log > django_logs.txt
```

#### Useful Commands for Debugging

```bash
# Check running processes
ps aux | grep python
ps aux | grep node

# Check network connections
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# Check disk usage
df -h
du -sh /var/lib/docker/

# Check memory usage
free -h
cat /proc/meminfo
```
