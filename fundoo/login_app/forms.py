"""
forms.py file
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# pylint: disable=too-few-public-methods
class SignupForm(UserCreationForm):
    """ Sign up form need to create a GUI form for user input """
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        """ Meta class"""
        model = User
        fields = ('username', 'email', 'password1', 'password2')
