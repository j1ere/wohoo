from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_notification_to_user(sender, message, username):
    channel_layer = get_channel_layer()
    notification_data = {
        'type': 'send_notification',
        'notification': {
            'message': message,
            'sender': sender
        }
    }
    async_to_sync(channel_layer.group_send)(f"notifications_{username}", notification_data)
