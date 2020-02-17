"""portal app URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('devices_list/<int:pk>', DeviceList.as_view()),
    path('device_details/<int:ident>/', DeviceDetails.as_view()),
    path('device_details/<int:ident>/', DeviceDetails.as_view()),
    path('device_status/<int:ident>/', DeviceStatus.as_view()),

    path('user_list/', UserList.as_view()),
    path('user_details/<int:pk>', UserDetails.as_view()),
    path('user_password/<int:pk>', UserPasswordManager.as_view()),

    path('announces_list/', AnnounceList.as_view()),
    path('announces_details/<int:pk>', AnnounceDetails.as_view()),

    path('markdown_preview/', MarkdownPreview.as_view()),
    path('change_mark/<int:ident>/<int:mark>', ChangeMark.as_view()),
    path('create_whitelist_device/<str:mac>', WhiteList.as_view()),
]
