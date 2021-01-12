DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    },
}
SECRET_KEY = "django_tests_secret_key"
TIME_ZONE = "America/Chicago"
LANGUAGE_CODE = "en-us"
ADMIN_MEDIA_PREFIX = "/static/admin/"
STATICFILES_DIRS = ()

MIDDLEWARE_CLASSES = []
INSTALLED_APPS = ()

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": 
            "django-sentinel/127.0.0.1:26379/0,django-sentinel/127.0.0.1:26380/0,django-sentinel/127.0.0.1:26381/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_sentinel.SentinelClient",
        }
    },
    "with_prefix": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "django-sentinel/127.0.0.1:26379/0,django-sentinel/127.0.0.1:26380/0,django-sentinel/127.0.0.1:26381/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_sentinel.SentinelClient",
        },
        "KEY_PREFIX": "test-prefix",
    },
    "with_blocking_connection_pool": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION":
            "django-sentinel/127.0.0.1:26379/0,django-sentinel/127.0.0.1:26380/0,django-sentinel/127.0.0.1:26381/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_sentinel.SentinelClient",
            "CONNECTION_POOL_CLASS": "redis.connection.BlockingConnectionPool",
        }
    }
}
