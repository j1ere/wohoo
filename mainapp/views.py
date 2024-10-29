#my views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from itertools import chain
import json
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import CustomUser  # Make sure to import your CustomUser model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Set up logging
logger = logging.getLogger(__name__)


from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import CustomUser

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
def home_view(request, group_name=None):
    user = request.user

    # Fetch unread notifications
    notifications = JoinRequest.objects.filter(status='pending')

    # Get all direct messages where the user is either the sender or recipient
    dms_as_sender = Message.objects.filter(sender=user, recipient__isnull=False)
    dms_as_recipient = Message.objects.filter(recipient=user, sender__isnull=False)

    # Combine the send and receive messages
    all_dms = chain(dms_as_sender, dms_as_recipient)

    # Create a set to track unique users in the DMs
    unique_dm_users = {dm.sender if dm.recipient == user else dm.recipient for dm in all_dms}

    # Ensure usernames are valid (non-empty)
    unique_dm_users = [u for u in unique_dm_users if u.username]

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
        join_policy = request.POST.get('join_policy')

        if group_name and join_policy:
            # Create the new group and add the current user as an admin
            group = Group.objects.create(name=group_name, join_policy=join_policy)
            #automatically add the creator as an admin and member
            group.admins.add(request.user)
            group.members.add(request.user)

            # group.add_member(request.user, added_by=request.user)
            # group.add_admin(request.user, promoted_by=request.user)
        return redirect('home')



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
    user = request.user
    receiver = get_object_or_404(CustomUser, username=receiver_username)
    messages = Message.objects.filter(
        sender=request.user, recipient=receiver
    ) | Message.objects.filter(
        sender=receiver, recipient=request.user
    ).order_by('timestamp')

    # Get all direct messages where the user is either the sender or recipient
    dms_as_sender = Message.objects.filter(sender=user, recipient__isnull=False)
    dms_as_recipient = Message.objects.filter(recipient=user, sender__isnull=False)

    # Combine the send and receive messages
    all_dms = chain(dms_as_sender, dms_as_recipient)

    # Create a set to track unique users in the DMs
    unique_dm_users = {dm.sender if dm.recipient == user else dm.recipient for dm in all_dms}

    # Ensure usernames are valid (non-empty)
    unique_dm_users = [u for u in unique_dm_users if u.username]

    #groups = Group.objects.filter(members=user)
    # Fetch all groups and prefetch related memberships
    groups = Group.objects.prefetch_related('group_memberships__user').all()

    context = {
        'receiver': receiver,
        'messages': messages,
        'unique_dm_users': unique_dm_users,
        'groups': groups
    }

    return render(request, 'mainapp/dm_page.html', context)


def group_chat(request, group_name):
    user = request.user
    # Retrieve the group by its name
    group = get_object_or_404(Group, name=group_name)

    # Fetch messages related to the group
    messages = Message.objects.filter(group=group).order_by('timestamp')

     # Get all direct messages where the user is either the sender or recipient
    dms_as_sender = Message.objects.filter(sender=user, recipient__isnull=False)
    dms_as_recipient = Message.objects.filter(recipient=user, sender__isnull=False)

    # Combine the send and receive messages
    all_dms = chain(dms_as_sender, dms_as_recipient)

    # Create a set to track unique users in the DMs
    unique_dm_users = {dm.sender if dm.recipient == user else dm.recipient for dm in all_dms}

    # Ensure usernames are valid (non-empty)
    unique_dm_users = [u for u in unique_dm_users if u.username]

    #groups = Group.objects.filter(members=user)
    # Fetch all groups and prefetch related memberships
    groups = Group.objects.prefetch_related('group_memberships__user').all()


    context = {
        'group': group,
        'messages': messages,
        'user': request.user,  # Pass the logged-in user for context
        'unique_dm_users': unique_dm_users,
        'groups': groups
    }

    return render(request, 'mainapp/group_page.html', context)



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


@login_required
def join_group(request, group_name):
    logger.info("================i got called ==================")
    group = get_object_or_404(Group, name=group_name)

    #check user if user is already a member
    if group.members.filter(id=request.user.id).exists():
        return redirect('group_chat',group_name = group_name)

    #if open group, add directly: else create a join request
    if group.join_policy == 'open':
        group.members.add(request.user)
        return redirect('group_chat', group_name=group_name)
    
    logger.info("=================================then i followed===================================")
    #otherwise create a join request and notify the admin
    join_request, created = JoinRequest.objects.get_or_create(user=request.user, group=group, status='pending')

    logger.info('=====================i was saved to the database ============================')
    
   
    logger.info(f"===============FINISHED EXECUTION====================")
    logger.info(f"===============FINISHED EXECUTION====================")
    return JsonResponse({"message": "A join request has been successfully sent for you"}, safe=False)


from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt
def approve_request(request, request_id, action):
    try:
        join_request = get_object_or_404(JoinRequest, id=request_id)
        group=join_request.group

        if not group.is_admin(request.user):
            return HttpResponseForbidden("only admins can approve requests")

        if action == 'approve':
            join_request.status = 'approved'
            group.members.add(join_request.user)
        elif action == 'deny':
            join_request.status = 'denied'
        join_request.save()

        return JsonResponse({'message': f'Request {action}d successfully.'})
        
    except JoinRequest.DoesNotExist:
        return JsonResponse({"error":"request not found"}, status=404)
    




@login_required
def manage_join_requests(request, group_name):
    group = get_object_or_404(Group, id=group_name)

    if not group.is_admin(request.user):
        return HttpResponseForbidden("Only admins can manage join requests")

    requests = group.join_requests.filter(status='pending')
    return render(request, 'manage_join_requests.html', {'group':group, 'requests':requests})
