"""
WebSocket consumer for real-time network alerts.

Connects authenticated users to a shared `network_alerts` group. Backend
code can broadcast events like:

    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    async_to_sync(get_channel_layer().group_send)(
        'network_alerts',
        {'type': 'alert.message', 'data': {'severity': 'high', 'msg': '...'}},
    )
"""
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NetworkAlertConsumer(AsyncJsonWebsocketConsumer):
    group_name = 'network_alerts'

    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({'type': 'connected', 'channel': self.group_name})

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        except Exception:
            pass

    async def receive_json(self, content, **kwargs):
        # Echo / heartbeat
        if content.get('type') == 'ping':
            await self.send_json({'type': 'pong'})

    async def alert_message(self, event):
        await self.send_json({'type': 'alert', 'data': event.get('data')})
