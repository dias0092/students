from django.contrib.auth.models import User
from rest_framework import serializers
from apps.authorization.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    university_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['gpa', 'avatar', 'balance', 'university_name']

    def get_university_name(self, obj):
        return obj.university.name if obj.university else None


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile']