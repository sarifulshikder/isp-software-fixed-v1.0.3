import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import apps.network.routing as network_routing
import apps.support.routing as support_routing
import apps.notifications.routing as notifications_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            network_routing.websocket_urlpatterns +
            support_routing.websocket_urlpatterns +
            notifications_routing.websocket_urlpatterns
        )
    ),
})
