"""portal app URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.connected, name='connected'),
    path('management/users', views.management, name='management'),
    path('management/devices', views.devices, name='devices'),
    path('management/announces', views.announces, name='announces'),
    path('management/whitelist', views.whitelist, name='whitelist'),
    path('faq', views.faq, name='faq'),
    path('disconnect', views.disconnect, name='disconnect'),

]
