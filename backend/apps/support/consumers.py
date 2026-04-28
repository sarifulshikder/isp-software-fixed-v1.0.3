"""
WebSocket consumer for live support ticket updates.

Each authenticated user joins the `support_<user_id>` group so backend
signals can push ticket-related events to that specific user. Staff
roles also join `support_staff` for global events.
"""
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class SupportTicketConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return
        self.user_group = f'support_{user.id}'
        self.staff_group = 'support_staff'
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        if getattr(user, 'role', '') in ('superadmin', 'admin', 'manager', 'support', 'technician'):
            await self.channel_layer.group_add(self.staff_group, self.channel_name)
        await self.accept()
        await self.send_json({'type': 'connected'})

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
            await self.channel_layer.group_discard(self.staff_group, self.channel_name)
        except Exception:
            pass

    async def receive_json(self, content, **kwargs):
        if content.get('type') == 'ping':
            await self.send_json({'type': 'pong'})

    async def ticket_event(self, event):
        await self.send_json({'type': 'ticket', 'data': event.get('data')})
