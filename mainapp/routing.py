#routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    
    re_path(r'ws/dm/(?P<recipient>\w+)/$', consumers.DMConsumer.as_asgi()),

    #re_path(r'ws/notifications/$', consumers.NotificationsConsumer.as_asgi()),
    re_path(r'ws/notifications/', consumers.NotificationsConsumer.as_asgi()),
]