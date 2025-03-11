from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/sohbet/(?P<sohbet_id>\d+)/$', consumers.SohbetConsumer.as_asgi()),
] 