# /garden/admin.py
from django.contrib import admin
from .models import Garden, Outlet, Picture

admin.site.register(Garden)
admin.site.register(Outlet)
admin.site.register(Picture)
# Register your models here.
