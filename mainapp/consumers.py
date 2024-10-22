# import json
# from channels.generic.websocket import WebsocketConsumer
# import logging

# logger = logging.getLogger(__name__)

# class ChatConsumer(WebsocketConsumer):

#     def connect(self):
#         #acccept the connection
#         self.accept()
#         logger.info("Websocket connection opened")

#     def disconnect(self,close_code):
#         #called when websocket closes
#         logger.info(f"websocket disconnected with closecode {close_code}")

#     def receive(self, text_data):
#         #called when a message is received from the websocket
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         #log the message received
#         logger.info(f"received message==== {message} =====")

#         #echo the received message back to the client
#         self.send(text_data=json.dumps({
#             'message':message
#         }))#a dictionary inside a tupple

"""
Asynchronous consumers
"""
# from channels.generic.websocket import AsyncWebsocketConsumer
# import json
# import logging

# logger = logging.getLogger(__name__)
# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         logger.info(">>>>connection successful>>>>")
    
#     async def disconnect(self, code):
#         return await super().disconnect(code)
    
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         logger.info(f"===={message}====")

#         await self.send(text_data=json.dumps({
#             'message':message
#         }))

import json
from channels.generic.websocket import AsyncWebsocketConsumer

import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    #async defines an asynchronous function
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        #join the room group
        #await waits for an asynchronous operation to complete without blocking other code from running
        #self.channel_name is the unique identifier for this websocket connection
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()#accepts the websocket connection. without it no connection is established
        logger.info(f">>>websocket connection opened>>>")

    
    async def disconnect(self, close_code):
        #leave the group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"<<<websocket connection closed. close code {close_code}<<<")

    #receive message from websocket
    async def receive(self, text_data):#read documentation for this method code at the end of the script
        text_data_json = json.loads(text_data)#convert the text data to a python dictionary
        message = text_data_json['message']#get the value of message
        #broadcast the message to everyone in the group(completed by the chat_message method)
        await self.channel_layer.group_send(self.room_group_name, {'type':'chat_message', 'message':message})

    

    #this method sends the broadcast to all websocket clients in the room
    async def chat_message(self,event):
        message = event['message']

        #Send your message to the websocket
        await self.send(text_data=json.dumps({'message':message}))
    
    
    
    #send the message to the group
        """
        {'type': 'chat_message', 'message': message} ==> a dictionary specifying the message data
        the 'type' is very important, it referes to the method that will be called when the message is
            received. In this case it refers to the chat_message method, defined after this method
        """