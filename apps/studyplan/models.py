from django.db import models


class University(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()


class Subject(models.Model):
    title = models.CharField(max_length=255)
    credits = models.IntegerField()
    description = models.TextField()
    code = models.CharField(max_length=20, unique=True)
    university = models.ForeignKey(University, related_name='subjects', on_delete=models.CASCADE)
