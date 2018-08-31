"""portal app URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views, forms

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name="portal/login.html", authentication_form=forms.LoginForm, extra_context={ "page_name": "index" }, redirect_authenticated_user=True ), name='index'),
    path('faq', views.faq, name='faq'),
    path('connected', views.connected, name='connected'),
]
