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
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


"""
The error you're encountering, AttributeError: 'str' object has no attribute 'objects', indicates that settings.AUTH_USER_MODEL is being treated as a string rather than a model class. In Django, settings.AUTH_USER_MODEL is typically a string that specifies the user model (in the format 'app_label.ModelName'), but you need the actual model class to perform queries.

Fixing the Error
To resolve this issue, you can use Django's get_user_model function, which returns the user model class based on the value of settings.AUTH_USER_MODEL. Here’s how you can update your code:

Import get_user_model: Ensure you import the function at the top of your file:

python
Copy code
from django.contrib.auth import get_user_model
Get the User Model Class: Replace your existing line with the following code, using get_user_model to retrieve the user class:

python
Copy code
User = get_user_model()  # Get the user model class
specific_user = await database_sync_to_async(User.objects.get)(id=requesting_user
"""
import base64
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from datetime import datetime
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

        """
        In your receive method, you have message = data['message'], which assumes that a message will always be present when no file is uploaded. It may be safer to use data.get('message') to avoid KeyErrors if a message is not included.

        """
        message = data.get('message')
        file_data = data.get('file')

        if file_data:
            # Decode the base64 data
            file_name = file_data['name']
            file_type = file_data['type']
            file_content = base64.b64decode(file_data['data'])
            file_size = len(file_content)

            if file_size > 100 * 1024 * 1024:  # 100 MB in bytes
                await self.send(text_data=json.dumps({
                    'error': 'File size exceeds the 100 MB limit.',
                }))
                return
            
             # Save the file
            path = default_storage.save(f'uploads/{file_name}', ContentFile(file_content))
            file_url = default_storage.url(path)
            file_storage_time = datetime.now().isoformat()

            await database_sync_to_async(Message.objects.create)(sender=self.sender, recipient=self.recipient, content=file_url)

            await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message_file',
            'message': message,
            'sender': self.sender.username,
            'timestamp': file_storage_time, # Send timestamp as ISO format
            'file': {
                    'name': file_name,
                    'type': file_type,
                    'url': file_url,
                },
            })
        else:
            # Save the message into the database using the message model
            direct_message = await database_sync_to_async(Message.objects.create)(sender=self.sender, recipient=self.recipient, content=message)

            # Send the message to the room group
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'chat_message',
                'message': message,
                'sender': self.sender.username,
                'timestamp': direct_message.timestamp.isoformat() # Send timestamp as ISO format
                })

        

    # Send the message to the WebSocket
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({'message': message, 'sender': sender, 'timestamp': timestamp}))

    async def chat_message_file(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']
        file = event['file']

        await self.send(text_data=json.dumps({'message': message, 'sender': sender, 'timestamp': timestamp, 'file': file}))

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
        requesting_user_id = data.get('user_id')

        try:
            # Get admin user IDs for the specified group using database_sync_to_async
            admin_user_ids = await database_sync_to_async(
                lambda: list(GroupMembership.objects.filter(group_id=group_id, role='admin').values_list('user_id', flat=True))
            )()
            User = get_user_model()  # Get the user model class
            specific_user = await database_sync_to_async(User.objects.get)(id=requesting_user_id)
            specific_group = await database_sync_to_async(Group.objects.get)(id=group_id)

            await database_sync_to_async(JoinRequest.objects.create)(user=specific_user,group=specific_group,status='pending')
            # Prepare the notification message with role and group details
            notification = {
                'message': f"New join request from {requesting_user}",
                'target_group_id': group_id,
                'target_role': 'admin',
                'user_id': requesting_user_id,
                'admin_user_ids': list(admin_user_ids)  # List of admin user IDs
            }
        except ObjectDoesNotExist:
            logger.info(f"--------------------some issues with accuracy of variables received from front end------------------------")

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