# login/views.py
from django.shortcuts import render
from django.conf import settings
from .forms import OnlineCredentialForm
from .models import WirelessUser
from garden.views import garden as biggarden

def success(request):
    wireless = WirelessUser.objects.get(pk=1)
    context = {'wireless':wireless}
    return render(request,'login/youarein.html', context)

def wireless(request):
    wireless = WirelessUser.objects.get(pk=1)
    if request.method == "POST":
        form = OnlineCredentialForm(request.POST)
        if form.is_valid():
            wireless.ssid = form.cleaned_data['ssid']
            wireless.password = form.cleaned_data['password']
            wireless.save()
            if wireless.connectus():
                context = {'wireless':wireless}
                return biggarden(request)
            else:
                form = OnlineCredentialForm()
                context = {'warning' : "Motherbrain could not connect", 'form': form, 'wireless':wireless}
                return render(request, 'login/wireless.html', context)
    else:
        wireless = WirelessUser.objects.get(pk=1)
        form = OnlineCredentialForm()
        context = {'warning':"", 'form' : form, 'wireless':wireless}
        return render(request, 'login/wireless.html', context)
