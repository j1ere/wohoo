#my mainapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name='signup'),
    path("", views.login_view, name='login'),
    path("home/", views.home_view, name='home'),
    path('home/<str:receiver_username>/', views.dm_view, name='homedm'),
    path("home/<str:group_name>/", views.home_view, name='home'),
    #path('<str:room_name>/', views.chat_view, name='chat_view'),  # Add this URL pattern
    #path('home/<str:room_name>/', views.home_view, name='home_view_with_room'),  # View with room_name
    path('create-group/', views.create_group_view, name='create_group'),
    path('group/<str:group_name>/', views.group_chat, name='group_chat'),
    path("search-users/", views.search_users, name='search_users'),
   # path("group/<str:room_name>/" ,views.chat_view, name='group'),
   
    

    #path('group', views.group_chat, name='group'), 
    path('join-group/<str:group_name>/', views.join_group, name='join_group'),
    
    path('approve-request/<int:request_id>/<str:action>', views.approve_request, name='approve_request'),

    path('manage-requests/<str:group_name>/', views.manage_join_requests, name='manage_join_requests'),
]