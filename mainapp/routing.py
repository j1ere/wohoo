#routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    #re_path(r'ws/chat/home/(?P<room_name>\w+)/$',consumers.ChatConsumer.as_asgi()),#use the as_asgi() for async support
    #re_path('ws/dm/<str:receiver_username>/',consumers.DMConsumer.as_asgi()),
    #re_path(r'ws/dm/(?P<receiver_username>\w+)/$', consumers.DMConsumer.as_asgi()),
    #re_path("ws/dm/<str:recipient>/", consumers.DMConsumer.as_asgi()),
    #re_path('ws/notifications/', consumers.NotificationsConsumer.as_asgi()),
    re_path(r'ws/dm/(?P<recipient>\w+)/$', consumers.DMConsumer.as_asgi()),

    re_path(r'ws/notifications/$', consumers.NotificationsConsumer.as_asgi()),
]