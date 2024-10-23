"""
ASGI config for wohoo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wohoo.settings")
#initialize django asgi application early to ensure the AppRegistry is populated before importing 
# code that might import ORM models.   
django_asgi_application = get_asgi_application()#doing this code this way in this file as it is saved my life,
#otherwise the server would not have run

from mainapp.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_application,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns # we define this in routing.py
            )
        )
    ),
})