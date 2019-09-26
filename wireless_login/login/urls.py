# login/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.wireless, name='wireless'),
    path('success',views.success, name='success'),
]