"""portal app URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.connected, name='connected'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('faq', views.faq, name='faq'),
]
