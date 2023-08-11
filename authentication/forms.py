from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser
from django.contrib.auth.forms import SetPasswordForm


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']
        
class StopBotForm(forms.Form):
    bot_name = forms.CharField(widget=forms.HiddenInput())
        