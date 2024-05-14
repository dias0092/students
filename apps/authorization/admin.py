from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gpa', 'balance')
    search_fields = ('user__username', 'user__email')
    list_filter = ('gpa', 'balance')


admin.site.register(UserProfile, UserProfileAdmin)
