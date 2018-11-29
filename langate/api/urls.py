"""portal app URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('user_devices/', UserDeviceList.as_view()),
    path('user_devices/<int:ident>/', UserDevice.as_view()),
    path('user_list/', UserList.as_view()),
    path('user_details/<int:pk>', UserDetails.as_view()),
    path('user_password/<int:ident>', UserPasswordGenerator.as_view())
]
