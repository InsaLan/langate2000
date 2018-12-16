"""helpdesk app URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
   path('', views.helpdesk, name='helpdesk'),
   path('admin', views.admin, name='helpdesk-admin')
]
