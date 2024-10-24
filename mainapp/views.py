#my views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse

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
    # Get all DMs where the user is either the sender or recipient
    dms = Message.objects.filter(sender=user) | Message.objects.filter(recipient=user)
    
    # Get all groups where the user is a member
    groups = user.group_members.all()
    
    context = {
        'dms': dms.distinct(),
        'groups': groups,
    }
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


def search_users_view(request):
    query = request.GET.get('q', '')
    if query:
        users = CustomUser.objects.filter(username__icontains=query).exclude(username=request.user.username)
        users_data = [{'username': user.username} for user in users]
        return JsonResponse({'users': users_data})
    return JsonResponse({'users': []})  

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


def chat_view(request, room_name):
    return render(request, 'mainapp/index.html', {'room_name': room_name})