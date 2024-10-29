# # import json
# # from channels.generic.websocket import WebsocketConsumer
# # import logging

# # logger = logging.getLogger(__name__)

# # class ChatConsumer(WebsocketConsumer):

# #     def connect(self):
# #         #acccept the connection
# #         self.accept()
# #         logger.info("Websocket connection opened")

# #     def disconnect(self,close_code):
# #         #called when websocket closes
# #         logger.info(f"websocket disconnected with closecode {close_code}")

# #     def receive(self, text_data):
# #         #called when a message is received from the websocket
# #         text_data_json = json.loads(text_data)
# #         message = text_data_json['message']

# #         #log the message received
# #         logger.info(f"received message==== {message} =====")

# #         #echo the received message back to the client
# #         self.send(text_data=json.dumps({
# #             'message':message
# #         }))#a dictionary inside a tupple

# """
# Asynchronous consumers
# """
# # from channels.generic.websocket import AsyncWebsocketConsumer
# # import json
# # import logging

# # logger = logging.getLogger(__name__)
# # class ChatConsumer(AsyncWebsocketConsumer):
# #     async def connect(self):
# #         await self.accept()
# #         logger.info(">>>>connection successful>>>>")
    
# #     async def disconnect(self, code):
# #         return await super().disconnect(code)
    
# #     async def receive(self, text_data):
# #         text_data_json = json.loads(text_data)
# #         message = text_data_json['message']

# #         logger.info(f"===={message}====")

# #         await self.send(text_data=json.dumps({
# #             'message':message
# #         }))

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# import asyncio

# import logging

# logger = logging.getLogger(__name__)

# #defining the timeout duration
# TIMEOUT_DURATION = 300 #5 mins

# class ChatConsumer(AsyncWebsocketConsumer):
#     #async defines an asynchronous function
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = "chat_%s" % self.room_name
#         #join the room group
#         #await waits for an asynchronous operation to complete without blocking other code from running
#         #self.channel_name is the unique identifier for this websocket connection
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()#accepts the websocket connection. without it no connection is established
#         logger.info(f">>>websocket connection opened>>>")

#         #start the timeout task
#         self.timeout_task = asyncio.create_task(self.timeout_connection())
    
#     async def disconnect(self, close_code):
#         #leave the group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#         logger.info(f"<<<websocket connection closed. close code {close_code}<<<")
        
#         #cancel the timeout task
#         if hasattr(self, 'timeout_task'):
#             self.timeout_task.cancel()

#     #receive message from websocket
#     async def receive(self, text_data):#read documentation for this method code at the end of the script
#         #reset the timeout timer
#         if hasattr(self, 'timeout_task'):
#             self.timeout_task.cancel()
#             self.timeout_task = asyncio.create_task(self.timeout_connection())
#         text_data_json = json.loads(text_data)#convert the text data to a python dictionary
#         message = text_data_json['message']#get the value of message
#         #broadcast the message to everyone in the group(completed by the chat_message method)
#         await self.channel_layer.group_send(self.room_group_name, {'type':'chat_message', 'message':message})

    

#     #this method sends the broadcast to all websocket clients in the room
#     async def chat_message(self,event):
#         message = event['message']

#         #Send your message to the websocket
#         await self.send(text_data=json.dumps({'message':message}))
    
    
#     async def timeout_connection(self):
#         #wait for the specified time duration
#         await asyncio.sleep(TIMEOUT_DURATION)
#         #if no message was received during this time, disconnect the user
#         await self.close()#close websocket connection
#     #send the message to the group
#         """
#         {'type': 'chat_message', 'message': message} ==> a dictionary specifying the message data
#         the 'type' is very important, it referes to the method that will be called when the message is
#             received. In this case it refers to the chat_message method, defined after this method
#         """

#consumers.py

# self.user = self.scope['user']
        # self.receiver_username = self.scope['url_route']['kwargs']['receiver_username']

        # #fetch the receiver using CustomUser
        # try:
        #     self.receiver = await CustomUser.objects.aget(username=self.receiver_username)
        # except self.receiver.DoesNotExist:
        #     await self.send(text_data=json.dumps({'error': 'receiver does not exist'}))
        #     await self.close()
        #     logger.info(f"----websocket connection denied : unkown recipient ----")
        #create a unique room name for the dm between the two users
        #self.room_group_name = f"dm_{min(self.user.username, self.receiver_username)}_{max(self.user.username, self.receiver_username)}"
        
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from django.conf import  settings
# from .models import Message, Notification, CustomUser
# import asyncio
# import logging

# logger = logging.getLogger(__name__)

import json
import logging
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import *  # Ensure your models are imported

logger = logging.getLogger(__name__)

class DMConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the sender (user initiating the connection)
        self.sender = self.scope['user']
        print(self.scope['url_route']['kwargs'])  # Debug: check what's inside kwargs
        
        # Get the recipient username from the URL route kwargs
        self.recipient_username = self.scope['url_route']['kwargs']['recipient']

        # Fetch the recipient user object using Django's ORM
        self.recipient = await database_sync_to_async(CustomUser.objects.get)(username=self.recipient_username)

        if not self.recipient:
            raise ValueError("Recipient is missing in the database.")

        # Create a deterministic room name for DM based on both usernames
        room_name = f"dm_{sorted([self.sender.username, self.recipient.username])[0]}_{sorted([self.sender.username, self.recipient.username])[1]}"
        self.room_group_name = f"chat_{room_name}"

        # Join the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f">>> WebSocket connection successful >>>")

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"<<< WebSocket connection closed. Close code: {close_code} <<<")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Save the message into the database using the message model
        direct_message = await database_sync_to_async(Message.objects.create)(sender=self.sender, recipient=self.recipient, content=message)

        # Create a notification for the receiver
        #await database_sync_to_async(Notification.objects.create)(user=self.recipient, message=f"New message from {self.sender.username}: {message}")
        
        #logger.info(f"Notification created for {self.recipient.username}")

        # Send the message to the room group
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message': message,
            'sender': self.sender.username,
            'timestamp': direct_message.timestamp.isoformat() # Send timestamp as ISO format
            })

        # Check if the recipient is online
        # recipient = await self.get_recipient(self.recipient)  # Ensure this method is defined in your consumer
        # if recipient and recipient.is_online():  # Ensure is_online is a method on your CustomUser model
        #     # If the recipient is online, send the message instantly
        #     await self.send(text_data=json.dumps({
        #         'message': message,
        #         'sender': self.sender.username
        #     }))
        # else:
        #     # If the recipient is offline, send a notification
        #     await self.channel_layer.group_send(
        #         f"user_{self.recipient.username}",
        #         {
        #             'type': 'send_notification',
        #             'notification': f"You have a new message from {self.sender.username}"
        #         }
        #     )

    # Send the message to the WebSocket
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({'message': message, 'sender': sender, 'timestamp': timestamp}))



    # Ensure you define get_recipient method
    async def get_recipient(self, recipient):
        #return await database_sync_to_async(CustomUser.objects.filter)(username=recipient.username).first()
        # Get the recipient user from the database
        return await database_sync_to_async(lambda: CustomUser.objects.filter(username=recipient.username).first())()



class GroupConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']  # Get the group name from the URL
        self.group_channel_name = f"group_{self.group_name}"  # Unique channel name for the group

        # Join the group channel
        await self.channel_layer.group_add(
            self.group_channel_name,
            self.channel_name
        )

        await self.accept()  # Accept the WebSocket connection
        logger.info(">>>GROUP WEBSOCKET CONNECTION SUCCESS>>>")

    async def disconnect(self, close_code):
         # Leave the group channel
        await self.channel_layer.group_discard(
            self.group_channel_name,
            self.channel_name
        )
        logger.info(f"<<<GROUP WEBSOCKET DISCONNECT SUCCESSFUL. CLOSE CODE {close_code}<<<")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user_username = data['user_name']  # Get the user username from the message data
        group_name = data['group_name']  # Get the group name from the message data

        # Save the message to the database
        user = await sync_to_async(CustomUser.objects.get)(username=user_username)
        group = await sync_to_async(Group.objects.get)(name=group_name)
        message_instance = await sync_to_async(Message.objects.create)(
            sender=user,
            group=group,
            content=message
        )

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.group_channel_name,
            {
                'type': 'group_message',  # Specify the event type
                'message': message,
                'user_username': user.username,
                'timestamp': message_instance.timestamp.isoformat() # Send timestamp as ISO format
            }
        )


    async def group_message(self, event):
         # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user_username': event['user_username'],
            'timestamp': event['timestamp']
        }))


#group join request notification
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "notifications"
        
        # Add this channel to the notifications group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        
        await self.accept()
        logger.info(f"=====>>>CONNECTION TO NOTIFICATIONS SUCCESS=====>>>>>")

    async def disconnect(self, close_code):
        # Remove from group on disconnect
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"=====>>>CONNECTION TO NOTIFICATIONS FAILURE=====>>>>>")

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Example payload to broadcast, assuming group_id is sent in data
        group_id = data.get('group_id')
        requesting_user = data.get('username')
        
        # Filter for admin users in the specific group
        # admin_memberships = await sync_to_async(GroupMembership.objects.filter(group_id=group_id, role='admin'))
        # admin_user_ids = await sync_to_async(admin_memberships.values_list('user_id', flat=True))
        
        # Get admin user IDs for the specified group using database_sync_to_async
        admin_user_ids = await database_sync_to_async(
            lambda: list(GroupMembership.objects.filter(group_id=group_id, role='admin').values_list('user_id', flat=True))
        )()
        # Prepare the notification message with role and group details
        notification = {
            'message': f"New join request from {requesting_user}",
            'target_group_id': group_id,
            'target_role': 'admin',
            'admin_user_ids': list(admin_user_ids)  # List of admin user IDs
        }

        # Send the notification to the WebSocket group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_notification',
                'notification': notification
            }
        )

    async def send_notification(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['notification']))  