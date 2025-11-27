"""
Test settings for homescreen project.
"""

from .settings import *

# Test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Test-specific settings
DEBUG = False
TESTING = True

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Speed up password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Media files for testing
MEDIA_ROOT = '/tmp/test_media'

# Static files for testing
STATIC_ROOT = '/tmp/test_static'

# Disable CSRF for API tests
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
    'rest_framework.authentication.SessionAuthentication',
]

# JWT settings for testing
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=10),
})

# Disable rate limiting in tests
RATELIMIT_ENABLE = False

# Test-specific apps
INSTALLED_APPS += [
    'django_nose',
]

# Use nose test runner for better test discovery
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Nose test arguments
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=api',
    '--cover-html',
    '--cover-html-dir=htmlcov',
    '--cover-erase',
    '--nocapture',
    '--nologcapture',
]

# Celery settings for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Security settings for testing
SECRET_KEY = 'test-secret-key-not-for-production'
ALLOWED_HOSTS = ['*']

# CORS settings for testing
CORS_ALLOW_ALL_ORIGINS = True
