# Deployment-specific local settings
# ----------------------------------
#
# This is an example configuration for the OpenBook server used by the example
# Docker Compose setup. The original file from which this was derived lives in the source
# tree of the OpenBook server. See the comments there for details.

# Replace with your own secret key !!
SECRET_KEY = "django-insecure-jeo+.}_}9(Q.t_IU$WJ!%eL=b:MDbAL.~NY_=a:>D@:W[XPh4["
DEBUG = False
ALLOWED_HOSTS = ["*"]

# Also configured in ../webserver/Caddyfile, but actually only needed in one place.
OB_ROOT_REDIRECT = "/api/"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "openbook",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "postgres",
        "PORT": "5432",
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

STATIC_DIR = "/app/src/_static.volume"
STATIC_URL = "/static/"

MEDIA_DIR = "/app/src/_media.volume"
MEDIA_URL = "/media/"

DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": "/app/src/_backup.volume"}

USE_TZ = True
TIME_ZONE = "Europe/Berlin"

LANGUAGE_CODE = "de-de"
USE_THOUSAND_SEPARATOR = True

SITE_ID = 1
