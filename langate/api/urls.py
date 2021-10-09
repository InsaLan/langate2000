"""portal app URL Configuration
"""
from django.contrib import admin
from django.urls import path, include


from .views import *

urlpatterns = [

    path('auth/isconnected/', IsConnected.as_view()),
    path('auth/disconnect/', Disconnect.as_view()),
    path('auth/register/', RegisterAPI.as_view(), name='register'),
    path('auth/login/', LoginAPI.as_view(), name='login'),

    path('devices_list/', DeviceList.as_view()),

    path('user_devices_list/<int:pk>', UserDeviceList.as_view()),
    path('user_device_details/<int:ident>/', UserDeviceDetails.as_view()),
    path('device_status/<int:ident>/', DeviceStatus.as_view()),



    path('user_list/', UserList.as_view()),
    path('user_details/<int:pk>', UserDetails.as_view()),
    path('user_password/<int:pk>', UserPasswordManager.as_view()),

    path('announces_list/', AnnounceList.as_view()),
    path('announces_details/<int:pk>', AnnounceDetails.as_view()),

    path('markdown_preview/', MarkdownPreview.as_view()),
    path('change_mark/<int:ident>/<int:mark>', ChangeMark.as_view()),
    path('whitelist_device/', WhitelistList.as_view()),
    path('whitelist_device/<int:pk>', WhitelistDetails.as_view()),
]
