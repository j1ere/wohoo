from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's default AbstractUser.

    Attributes:
        category (str): Indicates whether the user is a 'student' or 'mentor'.
    """
    CATEGORY_CHOICES = [
        ('student', 'student'),
        ('mentor', 'mentor'),

    ]
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)

    def __str__(self):
        """
        String representation of the CustomUser instance.
        
        Returns:
            str: The username and human-readable category of the user.
        """
        return f"{self.username} ({self.get_category_display()})" #allows displaying the human readable label for the category instead of the database value
    

"""
message model will be useful for both dms and group messages
it includes fields for content sender, receipient, and group
"""
class Message(models.Model):
    """
    Model representing a message that can be sent as a direct message (DM) or in a group.

    Attributes:
        sender (CustomUser): The user who sent the message.
        recipient (CustomUser): The user who receives the message (for DMs).
        group (Group): The group in which the message was sent (for group messages).
        content (str): The content of the message.
        timestamp (datetime): The time the message was sent.
    """
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,null = True, blank=True, on_delete=models.CASCADE, related_name='received_messages')#for dms
    group = models.ForeignKey('Group', null=True, blank=True, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        """
        String representation of the Message instance.
        
        Returns:
            str: A short description of the message, indicating if it is a DM or a group message.
        """
        if self.recipient:
            return f"DM from {self.sender} to {self.recipient}: {self.content[:20]}"
        return f"Group messsage in {self.group.name}: {self.content[:20]}"


"""
This model will manage membership in groups
track who added a user and handle permissions
a role field will distinguish between a normal member and an admin
"""
class GroupMembership(models.Model):
    """
    Model to manage membership within groups, including user roles and tracking who added members.

    Attributes:
        user (CustomUser): The user who is a member of the group.
        group (Group): The group the user belongs to.
        added_by (CustomUser): The user who added this member to the group.
        role (str): The role of the user in the group (either 'member' or 'admin').
        date_joined (datetime): The date the user joined the group.
    """
    ROLE_CHOICES = [
        ('member', 'member'),
        ('admin','admin'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_memberships')
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name= 'group_memberships')
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='added_members')#tracks who added the members
    role = models.CharField(max_length=10,choices=ROLE_CHOICES, default= 'member')
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Meta options for GroupMembership.
        
        Ensures that a user can only belong to a group once.
        """
        """ensures a user can only belong to a group once"""
        constraints = [
            models.UniqueConstraint(fields=['user','group'],name='unique_group_membership')
        ]
    
    def __str__(self):
        """
        String representation of the GroupMembership instance.
        
        Returns:
            str: The username and group name along with the role of the user.
        """
        return f"{self.user.username} in {self.group.name} ({self.get_role_display()})"
    
    def is_admin(self):
        """
        Check if the user has an admin role in the group.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        return self.role== 'admin'

    def promote_to_admin(self):
        """
        Promote the user to an admin role within the group.
        """
        self.role= 'admin'
        self.save()
    
    def demote_to_member(self):
        """
        Demote the user to a member role within the group.
        """
        self.role = 'member'
        self.save()
    



"""
the group model represents each chat group with reference to the group members
and administrators
a many-to-many relationship  to users will be managed by groupmembership model
"""
class Group(models.Model):
    """
    Model representing a chat group, including its members and administrators.

    Attributes:
        name (str): The name of the group.
        members (ManyToManyField): The users who are members of the group.
        admins (ManyToManyField): The users who are administrators of the group.
    """
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through=GroupMembership,
        through_fields=('group', 'user'),  # Specify the foreign keys used in the GroupMembership model
        #related_name='groups'  # Update the related name to avoid confusion with other relationships
        related_name='group_members'  # Change this to avoid clash
    )
    #members = models.ManyToManyField(settings.AUTH_USER_MODEL, through=GroupMembership,related_name='group')
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name= 'administered_groups')#admins will have privilages

    def __str__(self):
        """
        String representation of the Group instance.
        
        Returns:
            str: The name of the group.
        """
        return self.name
    
    def add_member(self,user, added_by=None):
        """
        Add a new member to the group.

        Args:
            user (CustomUser): The user to be added to the group.
            added_by (CustomUser, optional): The user who is adding the new member.

        Raises:
            PermissionError: If the user trying to add members is not an admin.
        """
        """add a new member to the group"""
        if not self.is_admin(added_by):
            raise PermissionError("only admins can add members")
        GroupMembership.objects.create(user=user, group=self, added_by=added_by)

    def remove_member(self, user,removed_by):
        """
        Remove a member from the group.

        Args:
            user (CustomUser): The user to be removed from the group.
            removed_by (CustomUser): The user who is removing the member.

        Raises:
            PermissionError: If the user trying to remove members is not an admin.
        """
        """remove a member from the group"""
        if not self.is_admin(removed_by):
            raise PermissionError("only admins can remove a member")
        GroupMembership.objects.filter(user=user, group=self).delete()

    def is_admin(self, user):
        """
        Check if a user is an admin of the group.

        Args:
            user (CustomUser): The user to check.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        return self.admins.filter(id=user.id).exists()
    
    def add_admin(self, user, promoted_by):
        """
        Promote a member to an admin role in the group.

        Args:
            user (CustomUser): The user to be promoted to admin.
            promoted_by (CustomUser): The user who is promoting the member.

        Raises:
            PermissionError: If the user trying to promote members is not an admin.
        """
        """promote a member to an admin"""
        if not self.is_admin(promoted_by):
            raise PermissionError("only admins can promote a member")
        self.admins.add(user)
    
    def remove_admin(self, user, removed_by):
        """
        Demote an admin to a regular member.

        Args:
            user (CustomUser): The user to be demoted.
            removed_by (CustomUser): The user who is demoting the admin.

        Raises:
            PermissionError: If the user trying to demote admins is not an admin.
        """
        """demote an admin"""
        if not self.is_admin(removed_by):
            raise PermissionError("only admins can demote admins")
        self.admins.remove(user)

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()  # Notification content
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
