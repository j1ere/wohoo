#my views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse
from django.db.models import Q
from itertools import chain
import json


# Create your views here.
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)#automatically log the user in after authentication
            return redirect(reverse('home'))#redirect to the homepage
    else:
        form = CustomUserCreationForm()
    return render(request, 'mainapp/signup.html', {'form':form})

#user login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                print(f"====User {username} does not exist!====")
    else:
        form = AuthenticationForm()
    return render(request, 'mainapp/login.html', {'form':form})



@login_required
def home_view(request):
    user = request.user

    # Fetch unread notifications
    notifications = Notification.objects.filter(user=user, is_read=False)

    # Get all direct messages where the user is either the sender or recipient
    dms_as_sender = Message.objects.filter(sender=user)
    dms_as_recipient = Message.objects.filter(recipient=user)

    # Combine the send and receive messages
    all_dms = chain(dms_as_sender, dms_as_recipient)

    # Create a set to track unique users in the DMs
    unique_dm_users = {dm.sender if dm.recipient == user else dm.recipient for dm in all_dms}

    #groups = Group.objects.filter(members=user)
    # Fetch all groups and prefetch related memberships
    groups = Group.objects.prefetch_related('group_memberships__user').all()


    context = {
        'unique_dm_users': unique_dm_users,
        'notifications': notifications,
        'groups': groups,
    }

    print("Context data:", context)
    return render(request, 'mainapp/home.html', context)



@login_required
def create_group_view(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        if group_name:
            # Create the new group and add the current user as an admin
            group = Group.objects.create(name=group_name)
            group.add_member(request.user, added_by=request.user)
            group.add_admin(request.user, promoted_by=request.user)
        return redirect('home')


# def search_users_view(request):
#     query = request.GET.get('q', '')
#     if query:
#         users = CustomUser.objects.filter(username__icontains=query).exclude(username=request.user.username)
#         users_data = [{'username': user.username} for user in users]
#         print(json.dumps({'users': users_data}))
#         return JsonResponse({'users': users_data})
#     return JsonResponse({'users': []})  
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import CustomUser  # Make sure to import your CustomUser model

# Set up logging
logger = logging.getLogger(__name__)
# @login_required
# @require_GET  # Ensure this view only responds to GET requests
# def search_users_view(request):
#     logger.info("========================================Search view called============================")  # Log each time the view is called
#     query = request.GET.get('q', '').strip()  # Strip whitespace from query
#     if query:  # Only search if the query is not empty
#         users = CustomUser.objects.filter(username__icontains=query).exclude(username=request.user.username)
#         users_data = [{'username': user.username} for user in users]
        
#         # Log the response for debugging purposes
#         logger.debug("User search results: %s", json.dumps({'users': users_data}))
        
#         return JsonResponse({'users': users_data})
    
#     # Return an empty list if the query is empty
#     return JsonResponse({'users': []})

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import CustomUser

@require_GET
def search_users(request):
    query = request.GET.get('q', '').strip()

    if query:
        # Use icontains for case-insensitive matching
        users = CustomUser.objects.filter(username__icontains=query).values('username')

        # Format the data as a list of dictionaries
        user_data = list(users)

        # Prepare the JSON response
        response_data = {
            'users': user_data
        }
    else:
        response_data = {
            'users': []
        }

    return JsonResponse(response_data)

















@login_required
def dm_view(request, receiver_username):
    receiver = get_object_or_404(CustomUser, username=receiver_username)
    messages = Message.objects.filter(
        sender=request.user, recipient=receiver
    ) | Message.objects.filter(
        sender=receiver, recipient=request.user
    ).order_by('timestamp')

    context = {
        'receiver': receiver,
        'messages': messages,
        'user': request.user,
    }

    return render(request, 'mainapp/dm_page.html', context)


# def chat_view(request, room_name):
#     return render(request, 'mainapp/index.html', {'room_name': room_name})
# @login_required
# def chat_view(request, room_name):
#     user = request.user
#     # You can add logic here to fetch the conversation history, etc.
    
#     context = {
#         'room_name': room_name,
#         'user': user,
#     }
#     return render(request, 'mainapp/dm_page.html', context)


# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync

# def send_notification(request, sender, message):
#     # Access the channel layer
#     channel_layer = get_channel_layer()

#     # Send a notification to the 'notifications' group
#     async_to_sync(channel_layer.group_send)(
#         'notifications',
#         {
#             'type': 'send_notification',  # Maps to the method in the consumer
#             'message': message,
#             'sender': sender,
#         }
#     )
# views.py

from django.shortcuts import render
from .utils import send_notification_to_user

def submit_form(request):
    if request.method == 'POST':
        # Your form processing logic here
        
        sender = request.user.username
        message = "You have a new notification!"
        recipient = "john_doe"  # Replace with dynamic recipient based on logic
        
        # Trigger notification
        send_notification_to_user(sender, message, recipient)

        # Continue with your view logic
        return render(request, 'some_template.html')

def group_chat(request):
    return render(request, 'mainapp/group_page.html')
