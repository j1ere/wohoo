from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name='signup'),
    path("", views.login_view, name='login'),
    path("home/", views.home_view, name='home'),
    path("group/<str:room_name>/" ,views.chat_view, name='group'),
]