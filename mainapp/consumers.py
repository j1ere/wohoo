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
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import CustomUser, Message, Notification  # Ensure your models are imported

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
        await database_sync_to_async(Notification.objects.create)(user=self.recipient, message=f"New message from {self.sender.username}: {message}")

        # Send the message to the room group
        await self.channel_layer.group_send(self.room_group_name, {'type': 'chat_message', 'message': message, 'sender': self.sender.username})

        # Check if the recipient is online
        recipient = await self.get_recipient(self.recipient)  # Ensure this method is defined in your consumer
        if recipient and recipient.is_online():  # Ensure is_online is a method on your CustomUser model
            # If the recipient is online, send the message instantly
            await self.send(text_data=json.dumps({
                'message': message,
                'sender': self.sender.username
            }))
        else:
            # If the recipient is offline, send a notification
            await self.channel_layer.group_send(
                f"user_{self.recipient.username}",
                {
                    'type': 'send_notification',
                    'notification': f"You have a new message from {self.sender.username}"
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({'message': message, 'sender': sender}))

    # Ensure you define get_recipient method
    async def get_recipient(self, recipient):
        #return await database_sync_to_async(CustomUser.objects.filter)(username=recipient.username).first()
        # Get the recipient user from the database
        return await database_sync_to_async(lambda: CustomUser.objects.filter(username=recipient.username).first())()

class NotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_group_name = f"notifications_{self.user.username}"

        # Join notification group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f">>> Successful connection: notifications >>>>")

    async def disconnect(self, close_code):
        # Leave notification group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"<<< Closing notification connection Close code: {close_code} <<<")

    async def send_notification(self, event):
        notification = event['notification']
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({'notification': notification}))

# class DMConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
        
#         # Get the sender (user initiating the connection)
#         self.sender = self.scope['user']
#         print(self.scope['url_route']['kwargs'])  # Add this to check what's inside kwargs
#         # Get the recipient username from the URL route kwargs (passed in from your URL routing)
#          # Get the recipient from the URL parameters
#         self.recipient_username = self.scope['url_route']['kwargs']['recipient']

#         # Fetch the recipient user object using Django's ORM
#         self.recipient = await database_sync_to_async(CustomUser.objects.get)(username=self.recipient_username)

#         #self.recipient = self.scope['url_route']['kwargs']['recipient']
#         if not self.recipient:
#             raise ValueError("Recipient is missing in the databse .")

#         # Create a deterministic room name for DM based on both usernames
#         room_name = f"dm_{sorted([self.sender.username, self.recipient])[0]}_{sorted([self.sender.username, self.recipient])[1]}"
#         self.room_group_name = f"chat_{room_name}"

#         #join the room group
#         await self.channel_layer.group_add(self.room_group_name,self.channel_name)
#         await self.accept()
#         logger.info(f">>>websocket connection successful>>>")


#     async def disconnect(self, close_code):
#         #leave the rooom group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#         logger.info(f"<<<websocket connection closed. close code: {close_code}<<<")


#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']

#         #save the message into the database using the message model
#         direct_message = await Message.objects.acreate(sender=self.sender, recipient=self.recipient, content=message)
        
#         #create a notification for the receiver
#         await Notification.objects.acreate(user=self.recipient, message=f"new message from {self.sender.username}: {message}")

#         #send the message to the room group
#         await self.channel_layer.group_send(self.room_group_name, {'type':'chat_message', 'message':message, 'sender': self.user.username})

#         #send notification to the recipient
#         #await self.channel_layer.group_send(f"notifications_{self.receiver_username}", {'type':'send_notification', 'notification': f"You have a new message from {self.user.username}"})
#         if self.channel_layer.groups.get(f"notifications_{self.recipient_username}"):
#             await self.channel_layer.group_send(
#                 f"notifications_{self.recipient_username}",
#                 {'type': 'send_notification', 'notification': f"You have a new message from {self.sender.username}"}
#             )

#         # Check if the recipient is online
#         recipient = await self.get_recipient(self.recipient)
#         if recipient and recipient.is_online():
#             # If the recipient is online, send the message instantly
#             await self.send(text_data=json.dumps({
#                 'message': message,
#                 'sender': self.sender.username
#             }))
#         else:
#             # If the recipient is offline, send a notification
#             await self.channel_layer.group_send(
#                 f"user_{self.recipient}",
#                 {
#                     'type': 'send_notification',
#                     'notification': f"You have a new message from {self.user.username}"
#                 }
#             )

#     async def chat_message(self, event):
#         message = event['message']
#         sender = event['sender']

#         #send the message to the websocket
#         await self.send(text_data=json.dumps({'message': message, 'sender':sender}))

# class NotificationsConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope['user']
#         self.room_group_name = f"notifications_{self.user.username}"

#         #join notification group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()
#         logger.info(f">>>successful connection: notifications >>>>")

#     async def disconnect(self, close_code):
#         #leave notification group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
#         logger.info(f"<<<closing notification connection close_code: {close_code}<<<")

#     async def send_notification(self, event):
#         notification = event['notification']
#         #send notification to websocket
#         await self.send(text_data=json.dumps({'notification':notification}))

