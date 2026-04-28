"""
WebSocket consumer for in-app notifications.

Pushes notification payloads to a per-user group `notifications_<user_id>`.

Broadcast example:

    async_to_sync(get_channel_layer().group_send)(
        f'notifications_{user.id}',
        {'type': 'notify.message', 'data': {'title': '...', 'body': '...'}},
    )
"""
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return
        self.group = f'notifications_{user.id}'
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        await self.send_json({'type': 'connected'})

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.group, self.channel_name)
        except Exception:
            pass

    async def receive_json(self, content, **kwargs):
        if content.get('type') == 'ping':
            await self.send_json({'type': 'pong'})

    async def notify_message(self, event):
        await self.send_json({'type': 'notification', 'data': event.get('data')})
