"""portal app URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('devices_list/<int:pk>', DeviceList.as_view()),
    path('device_details/<int:ident>/', DeviceDetails.as_view()),
    path('device_status/<int:ident>/', DeviceStatus.as_view()),

    path('user_list/', UserList.as_view()),
    path('user_details/<int:pk>', UserDetails.as_view()),
    path('user_password/<int:pk>', UserPasswordManager.as_view()),

    path('widgets/announce/', AnnounceWidgetList.as_view()),
    path('widgets/announce/<int:pk>', AnnounceWidgetDetails.as_view()),
    path('widgets/status/', RealtimeStatusWidgetManager.as_view()),

    path('widgets/pizzas/', PizzaWidgetManager.as_view()),
    path('widgets/pizzas/slots/', PizzaSlotList.as_view()),
    path('widgets/pizzas/slots/<int:pk>', PizzaSlotDetails.as_view())

]
