"""portal app URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

from . import views
from .views import UserDeviceListView, UserDeviceView

urlpatterns = [
    path('user_devices/', UserDeviceListView.as_view()),
    path('user_devices/<int:ident>/', UserDeviceView.as_view()),
]
