from django.shortcuts import render

# Create your views here.
def chat_view(request, room_name):
    return render(request, 'mainapp/index.html', {'room_name': room_name})