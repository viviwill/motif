from django.contrib.auth.models import User
from django import forms
from .models import *


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class SummaryAddForm(forms.ModelForm):
    class Meta:
        model = Storage
        fields = ['summary']


class ProfileForm(forms.ModelForm):
    username = forms.CharField(required=False)
    email = forms.CharField(required=False)
    old_password = forms.CharField(required=False, widget=forms.PasswordInput)
    new_password = forms.CharField(required=False, widget=forms.PasswordInput)
    user_portrait = forms.ImageField(required=False)

    class Meta:
        model = SocialProfile
        fields = ['username', 'email', 'old_password', 'new_password', 'user_portrait']
