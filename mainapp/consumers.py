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
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

logger = logging.getLogger(__name__)
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        logger.info(">>>>connection successful>>>>")
    
    async def disconnect(self, code):
        return await super().disconnect(code)
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        logger.info(f"===={message}====")

        await self.send(text_data=json.dumps({
            'message':message
        }))