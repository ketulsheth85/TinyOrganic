"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.minimal')

application = WhiteNoise(
	get_wsgi_application(),
	root = os.path.join(os.path.dirname(__file__),'static'),
	prefix = 'static/',
	max_age = os.environ.get('MAX_AGE')
)

