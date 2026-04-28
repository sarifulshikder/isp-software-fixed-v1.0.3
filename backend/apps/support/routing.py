from django.urls import re_path
from .consumers import SupportTicketConsumer

websocket_urlpatterns = [
    re_path(r'^ws/support/tickets/$', SupportTicketConsumer.as_asgi()),
]
