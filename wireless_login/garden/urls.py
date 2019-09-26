# gardens/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.garden, name='garden'),
    path('toggler', views.toggler, name='toggler'),
    path('<int:outlet_num>', views.outlet, name='outlet'),
    path('<int:outlet_num>/outlet_template', views.outlet_template, name='outlet_template'),
    path('<str:garden_serial>/variable_change',views.variable_change,name='variable_change'),
]