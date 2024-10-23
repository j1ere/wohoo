from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name='signup'),
    path("login/", views.login_view, name='login'),
    path("home/<str:room_name>/" ,views.chat_view, name='home'),
]