from django.db import models
from django.contrib.auth.models import User

# create accounts models(profile)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=120)
    national_id = models.CharField(max_length=32, unique=True)
    dob = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"
