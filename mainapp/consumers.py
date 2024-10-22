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



import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

"""
1. import json
import: This keyword is used to include external libraries or modules in your code.
 Here, we are importing Python's built-in json module.
json: This is the module that provides functions to work with JSON (JavaScript Object Notation).
 We will use it to convert Python dictionaries to JSON strings and vice versa.

2. from channels.generic.websocket import AsyncWebsocketConsumer
from ... import ...: This is another way to import specific components from a module. 
In this case, we are importing the AsyncWebsocketConsumer class from 
the channels.generic.websocket module.
AsyncWebsocketConsumer: This is a class provided by Django Channels,
 which allows you to handle WebSocket connections asynchronously.
   It enables handling events like connection, disconnection, and message reception.

3. class ChatConsumer(AsyncWebsocketConsumer):
class: This keyword is used to define a class in Python.
 A class is like a blueprint for creating objects with specific behavior and attributes.
ChatConsumer: This is the name of the class, 
which is specific to this project. It extends (inherits from)
 the AsyncWebsocketConsumer class, meaning it gets all the methods and behaviors
   from AsyncWebsocketConsumer and can add or override functionality.
(AsyncWebsocketConsumer): This indicates that ChatConsumer is a subclass
 of AsyncWebsocketConsumer, meaning it gets its WebSocket handling behavior from 
 AsyncWebsocketConsumer.

4. async def connect(self):
async: This keyword is used to define an asynchronous function.
 Asynchronous functions allow you to write non-blocking code,
   meaning the program can continue doing other work while waiting 
   for certain tasks (like network operations) to complete.
def: This keyword is used to define a function.
connect(self): This is the function that gets called when a WebSocket connection is opened.
 It is the method responsible for handling what happens when a user connects to the WebSocket.

5. self.room_name = self.scope['url_route']['kwargs']['room_name']
self: Refers to the instance of the class.
 It's used to access the class's attributes and methods.
scope: This is a dictionary that contains metadata about the connection, 
such as the user, session, and the URL route. It’s provided by Django Channels.
['url_route']['kwargs']['room_name']: This extracts the room_name from 
the WebSocket connection’s URL. url_route contains the data parsed from the URL 
routing (e.g., /ws/chat/<room_name>/), and kwargs holds the parameters extracted
 from the URL pattern, in this case, room_name.
self.room_name: Stores the room_name extracted from the URL in 
an instance variable so it can be used throughout the class.

6. self.room_group_name = 'chat_%s' % self.room_name
'chat_%s' % self.room_name: This is string formatting. 
It creates a room group name by combining the string 'chat_' with the room_name
 using the %s placeholder. For example, if room_name = 'room1', the room_group_name 
 will be 'chat_room1'.
self.room_group_name: Stores the formatted room group name,
 which will be used to organize multiple users into the same chat room.

7. await self.channel_layer.group_add(self.room_group_name, self.channel_name)
await: This is used to wait for an asynchronous operation to 
complete without blocking other code from running.
self.channel_layer: Refers to the channel layer, which is an abstraction 
that allows different instances of your app to communicate with each other.
 It manages groups of consumers (in this case, users in a chat room).
group_add: This method adds the current WebSocket connection to a group
 (in this case, the chat room group).
self.room_group_name: The group name that the connection is added to (e.g., chat_room1).
self.channel_name: The unique identifier for this WebSocket connection.

8. await self.accept()
This accepts the WebSocket connection. Without calling accept(), 
the connection will not be established. The await keyword means it's an asynchronous operation.

9. async def disconnect(self, close_code):
disconnect(self, close_code): This method gets called when the WebSocket connection is closed.
 The close_code is the code indicating why the connection was closed.
This method handles any cleanup when the user disconnects from the chat.

10. await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
group_discard: This method removes the WebSocket connection from the group. 
When the user leaves, they are removed from the chat room group.

11. async def receive(self, text_data):
receive(self, text_data): This method is called when the WebSocket receives 
a message from the client (the browser). The text_data parameter contains the 
data sent by the WebSocket client.
This method will parse the incoming message, process it, and broadcast it to all members 
of the chat room.

12. text_data_json = json.loads(text_data)
json.loads(): This function converts the JSON-encoded string (text_data) into
 a Python dictionary (text_data_json). For example, if the client sends a message in JSON format, 
 this line parses it into a Python object.

13. message = text_data_json['message']
message: Extracts the value associated with the key 'message'
 from the dictionary (text_data_json). This is the actual chat message sent by the client.


14. await self.channel_layer.group_send(self.room_group_name, {'type': 'chat_message', 'message': message})
group_send(): This method sends a message to everyone in the chat room group.
self.room_group_name: Specifies which group (chat room) the message is sent to.
{'type': 'chat_message', 'message': message}: A dictionary specifying the message data.
The 'type' key is important—it refers to the method that will be called when the message is received. 
In this case, it refers to the chat_message() method (defined next).

15. async def chat_message(self, event):
chat_message(self, event): This method is called when a message is sent to the group via group_send(). 
The event parameter contains the message data.
event['message']: Extracts the message from the event dictionary.

16. await self.send(text_data=json.dumps({'message': message}))
self.send(): Sends data to the WebSocket client (browser).
json.dumps(): Converts the Python dictionary ({'message': message}) into a JSON string so it can be
 sent over the WebSocket.
This sends the message back to the WebSocket client.

"""

"""
Yes, these two methods (receive and chat_message) work together to handle message 
transmission in a WebSocket-based chat system. Let me explain their interaction step by step:

1. receive(self, text_data)
This method handles incoming messages from the WebSocket client (usually the browser).
 Here's what happens in detail:

Step 1: Receive WebSocket Message

The receive method is triggered when the WebSocket client sends data to the server.
text_data is the raw message received from the client in JSON format. Typically,
 this might be a user sending a chat message.
Step 2: Convert JSON Data to Python Dictionary

text_data_json = json.loads(text_data) converts the incoming JSON string (text data) 
into a Python dictionary.
For example, if the client sent {"message": "Hello, everyone!"}, it would be converted 
into a Python dictionary: {"message": "Hello, everyone!"}.
Step 3: Extract the Message

message = text_data_json['message'] extracts the value associated with the 'message' key 
from the dictionary, so now message would be "Hello, everyone!".
Step 4: Broadcast Message to Group

await self.channel_layer.group_send(self.room_group_name, {'type': 'chat_message', 'message': message}):
This sends the message to all WebSocket clients (users) that are in the same room.
self.room_group_name specifies the group name (e.g., 'chat_room1').
group_send() is a method provided by the channel_layer, which broadcasts the message to everyone
 in the group.
{'type': 'chat_message', 'message': message}: The type: 'chat_message' specifies that the
 message should trigger the chat_message method (explained below). The message itself is included
   as part of this dictionary.

2. chat_message(self, event)
This method is triggered when a message is sent to the room group
 (via group_send from the receive method).
 Here's what happens in detail:

Step 1: Receive Event from Group

The chat_message method is called when the group (chat room) receives a message.
The event parameter contains the message that was sent by the group_send() call.
 So event is a dictionary, and its contents are the message that was sent, in this case,
   {'type': 'chat_message', 'message': 'Hello, everyone!'}.

Step 2: Extract the Message

message = event['message'] extracts the actual message from the event dictionary.
 So message will now be "Hello, everyone!".

Step 3: Send Message to WebSocket Client

await self.send(text_data=json.dumps({'message': message})):
self.send() sends the message back to the WebSocket client (the browser).
json.dumps() converts the Python dictionary {'message': message} 
back into a JSON string to be sent via WebSocket.
This sends the message (now in JSON format) to all WebSocket clients connected to the room.
Interaction Between receive and chat_message
When a User Sends a Message:

The WebSocket client sends a message (e.g., {"message": "Hello"}) to the server.
The receive method is triggered. It extracts the message and calls group_send() 
to broadcast it to the group.
When the Group Receives the Message:

The chat_message method is triggered for all clients in the group.
This method takes the message and sends it back to each WebSocket client in the room using self.send().
Result:

The message that one user sends gets broadcast to all other users in the chat room in real-time.
Flow:
receive() method: Handles incoming messages from a specific user, 
processes the message, and sends it to the chat group.
chat_message() method: Broadcasts the message to all users in the group,
 sending it back to their WebSocket connections.
This interaction allows a real-time chat room where messages are shared among all connected users.
"""