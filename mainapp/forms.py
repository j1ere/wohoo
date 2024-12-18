from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    category = forms.ChoiceField(choices=CustomUser.CATEGORY_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'category','password1', 'password2']
    
    