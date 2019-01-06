"""helpdesk app URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
   path('new', views.open_ticket, name='open-ticket'),
   path('admin', views.admin, name='helpdesk-admin'),
   path('', views.view_tickets, name='helpdesk'),
   path('view/<int:ticket_id>', views.show_ticket, name='ticket_view')
]
