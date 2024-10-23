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


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import  settings
from .models import Message, Notification
import asyncio
import logging

logger = logging.getLogger(__name__)


class DMConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.receiver_username = self.scope['url_route']['kwargs']['receiver_username']

        #fetch the receiver using CustomUser
        try:
            self.receiver = await settings.AUTH_USER_MODEL.objects.aget(username=self.receiver_username)
        except settings.AUTH_USER_MODEL.DoesNotExist:
            await self.send(text_data=json.dumps({'error': 'user does not exist'}))
            await self.close()
            logger.info(f"----websocket connection denied : unkown recipient ----")
        #create a unique room name for the dm between the two users
        self.room_group_name = f"dm_{min(self.user.username, self.receiver_username)}_{max(self.user.username, self.receiver_username)}"

        #join the room group
        await self.channel_layer.group_add(self.room_group_name,self.channel_name)
        await self.accept()
        logger.info(f">>>websocket connection successful>>>")


    async def diconnect(self, close_code):
        #leave the rooom group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        logger.info(f"<<<websocket connection closed. close code: {close_code}<<<")


    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        #save the message into the database using the message model
        direct_message = await Message.objects.acreate(sender=self.user, recipient=self.receiver, content=message)
        
        #create a notification for the receiver
        await Notification.objects.acreate(user=self.receiver, message=f"new message from {self.user.username}: {message}")

        #send the message to the room group
        await self.channel_layer.group_send(self.room_group_name, {'type':'chat_message', 'message':message, 'sender': self.user.username})

        #send notification to the recipient
        await self.channel_layer.group_send(f"notifications_{self.receiver_username}", {'type':'send_notification', 'notification': f"You have a new message from {self.user.username}"})

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        #send the message to the websocket
        await self.send(text_data=json.dumps({'message': message, 'sender':sender}))

class NotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_group_name = f"notifications_{self.user.username}"

        #join notification group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f">>>successful connection: notifications >>>>")

    async def disconnect(self, close_code):
        #leave notification group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_layer)
        logger.info(f"<<<closing notification connection close_code: {close_code}<<<")

    async def send_notification(self, event):
        notification = event['notification']
        #send notification to websocket
        await self.send(text_data=json.dumps({'notification':notification}))

