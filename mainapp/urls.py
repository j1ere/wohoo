#my mainapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name='signup'),
    path("", views.login_view, name='login'),
    path("home/", views.home_view, name='home_view'),
    path('<str:room_name>/', views.chat_view, name='chat_view'),  # Add this URL pattern
    #path('home/<str:room_name>/', views.home_view, name='home_view_with_room'),  # View with room_name
    path('create-group/', views.create_group_view, name='create_group'),
    path('search-users/', views.search_users_view, name='search_users'),
    path("group/<str:room_name>/" ,views.chat_view, name='group'),
    path('home/<str:receiver_username>/', views.dm_view, name='homedm'),
]