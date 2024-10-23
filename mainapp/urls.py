from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name='signup'),
    path("", views.login_view, name='login'),
    path("home/", views.home_view, name='home'),
    path('create-group/', views.create_group_view, name='create_group'),
    path('search-users/', views.search_users_view, name='search_users'),
    path("group/<str:room_name>/" ,views.chat_view, name='group'),
]