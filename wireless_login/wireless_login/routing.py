# wireless_login/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from garden import routing
from garden import consumers
from django.conf import settings
BOX_CHANNEL = str("work_" + settings.BOX_SERIAL)


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
    "channel":ChannelNameRouter({
       BOX_CHANNEL : consumers.change_detect,
    })
})
ASGI_APPLICATION = "wireless_login.routing.application"
