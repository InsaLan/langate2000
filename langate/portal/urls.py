"""portal app URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.connected, name='connected'),
    path('management', views.management, name='management'),
    path('management/widgets', views.widgets, name='widgets'),
    path('faq', views.faq, name='faq'),
    path('disconnect', views.disconnect, name='disconnect') 
]