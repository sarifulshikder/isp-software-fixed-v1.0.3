from django.urls import re_path
from .consumers import NetworkAlertConsumer

websocket_urlpatterns = [
    re_path(r'^ws/network/alerts/$', NetworkAlertConsumer.as_asgi()),
]
