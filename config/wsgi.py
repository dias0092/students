"""
WSGI config for studyplan project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application
from config.settings import base
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')


application = get_wsgi_application()
application = WhiteNoise(application, root=base.STATIC_ROOT)
