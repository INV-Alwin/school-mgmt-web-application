from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("role", "phone_number")}),
    )

admin.site.register(User, UserAdmin)