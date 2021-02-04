from django.contrib import admin

from .models import Profile

class RoleAdmin(admin.ModelAdmin):
    fields = ['role']

# Register your models here.
admin.site.register(Profile, RoleAdmin)
