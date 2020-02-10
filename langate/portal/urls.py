"""portal app URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

"""
    path('management/widgets', views.widgets, name='widgets'),
    path('blog/', views.allblogs , name='allblogs'),
    path('blog/articles', views.articles , name='articles'),
    path('blog/<int:blog_id>/', views.detail, name="detail"),
"""

urlpatterns = [
    path('', views.connected, name='connected'),
    path('management', views.management, name='management'),
    path('management/announces', views.announces, name='announces'),
    path('faq', views.faq, name='faq'),
    path('disconnect', views.disconnect, name='disconnect'),
]
