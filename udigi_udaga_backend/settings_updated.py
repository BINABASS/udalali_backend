from pathlib import Path
import os
from datetime import timedelta

# ... (keep all existing imports and configurations)

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",

    # Third-party apps
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_yasg",

    # Local apps
    "core.apps.CoreConfig",
    "users.apps.UsersConfig",
]

# ... (rest of the settings remain the same)
