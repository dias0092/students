from django.db import models
from apps.authorization.models import UserProfile


class Semester(models.Model):
    year = models.IntegerField(help_text="The academic year, e.g., 2024")
    term = models.CharField(max_length=100, help_text="E.g., Fall, Spring, Summer")
    credit_limit = models.IntegerField(help_text="Maximum credits a student can enroll in this semester.")


class University(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()


class Subject(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=255)
    credits = models.IntegerField()
    description = models.TextField(blank=True)
    offered_semesters = models.ManyToManyField(Semester, related_name='subjects')
    university = models.ForeignKey(University, related_name='subjects', on_delete=models.CASCADE)


class StudyPlan(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='study_plans')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='study_plans')
    subjects = models.ManyToManyField(Subject, related_name='study_plans')

    def total_credits(self):
        return sum(subject.credits for subject in self.subjects.all())


class ClassSchedule(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday')
    ]

    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='class_schedules')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='class_schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_schedules')
    day_of_week = models.CharField(max_length=9, choices=DAY_CHOICES)
    time = models.TimeField(help_text="Start time of the class")

    class Meta:
        unique_together = ('student', 'semester', 'day_of_week', 'time')

