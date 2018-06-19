from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import LanUser

admin.site.register(LanUser, UserAdmin)