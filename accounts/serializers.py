from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("full_name", "national_id", "dob", "address")

class MeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ("id", "username", "email", "profile")

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        # update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # update profile nested fields
        if profile_data:
            prof = instance.profile
            for attr, value in profile_data.items():
                setattr(prof, attr, value)
            prof.save()
        return instance
