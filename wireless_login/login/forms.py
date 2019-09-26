# login/forms.py
from django import forms
from .models import WirelessUser

class OnlineCredentialForm(forms.ModelForm):

    class Meta:
        model = WirelessUser
        fields = ['ssid','password']