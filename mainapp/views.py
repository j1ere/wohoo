from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .forms import CustomUserCreationForm

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
    return render(request, 'signup.html', {'form':form})

#user login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('home'))
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form':form})



def chat_view(request, room_name):
    return render(request, 'mainapp/index.html', {'room_name': room_name})