from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomUser, Message, GroupMembership, Group, Notification
from django.contrib.auth.admin import UserAdmin

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin for CustomUser model with additional fields displayed.
    """
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('category', 'last_active')}),
    )
    list_display = ('username', 'email', 'category', 'is_online')
    list_filter = ('category',)
    search_fields = ('username', 'email')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for Message model.
    """
    list_display = ('sender', 'recipient', 'group', 'content', 'timestamp')
    list_filter = ('group', 'sender')
    search_fields = ('sender__username', 'recipient__username', 'content')
    date_hierarchy = 'timestamp'

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    """
    Admin configuration for GroupMembership model.
    """
    list_display = ('user', 'group', 'role', 'date_joined', 'added_by')
    list_filter = ('role', 'group')
    search_fields = ('user__username', 'group__name', 'added_by__username')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    Admin configuration for Group model.
    """
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('admins',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for Notification model.
    """
    list_display = ('user', 'message', 'is_read', 'timestamp')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'message')
    date_hierarchy = 'timestamp'
