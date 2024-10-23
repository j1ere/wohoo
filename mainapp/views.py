from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required

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
    return render(request, 'mainapp/home.html', {'user':user})

def chat_view(request, room_name):
    return render(request, 'mainapp/index.html', {'room_name': room_name})