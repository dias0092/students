from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gpa = models.FloatField(default=0.0, verbose_name="GPA")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    university = models.ForeignKey('studyplan.University', related_name='user_profiles', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.user)