# garden/forms.py
from django import forms
from .models import Garden

class OnlineCredentialForm(forms.ModelForm):

    class Meta:
        model = Garden
        fields = ['ssid','password']
