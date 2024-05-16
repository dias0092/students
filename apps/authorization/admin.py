from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gpa', 'balance', 'university')
    search_fields = ('user__username', 'university__name')
    list_filter = ('gpa', 'balance')


admin.site.register(UserProfile, UserProfileAdmin)
