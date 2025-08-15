from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "national_id", "dob", "updated_at")
    search_fields = ("full_name", "national_id", "user__username", "user__email")
