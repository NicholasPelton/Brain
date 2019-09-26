"""wireless_login URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from apscheduler.schedulers.background import BackgroundScheduler
from garden import tasks
from django.contrib import admin
from django.urls import path, include
from login.models import WirelessUser
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login', include('login.urls')),
    path('', include('garden.urls')),
]

tasks.start_up()

wifi = WirelessUser.objects.get(pk=1)

if wifi.start_wifi_check()==False:
    # This gets the data since it refuses to store dictionaries
    print("Trying to Log in")
    #tasks.start_up()
    wifi.connectus()
    scheduler = BackgroundScheduler()
    scheduler.add_job(tasks.update_check, 'cron', second=0, id="update_check")
    scheduler.add_job(tasks.new_day, 'cron', hour=0)

    scheduler.start()
