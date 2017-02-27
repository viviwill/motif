from django.contrib.auth.models import User
from django import forms
from .models import Article, Storage


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class SummaryAddForm(forms.ModelForm):
    class Meta:
        model = Storage
        fields = ['summary']
