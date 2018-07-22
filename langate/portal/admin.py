from django.contrib import admin

# Register your models here.

from django.contrib.auth.admin import UserAdmin
from .models import LanUser

admin.site.register(LanUser, UserAdmin)

