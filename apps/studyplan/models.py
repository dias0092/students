from django.db import models
from apps.authorization.models import UserProfile
from datetime import time
DAY_CHOICES = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday')
]

TERM_CHOICES = [
    ('Қыс', 'Winter'),
    ('Көктем', 'Spring'),
    ('Жаз', 'Summer'),
    ('Күз', 'Fall')
]


class Semester(models.Model):
    year = models.IntegerField(help_text="The academic year, e.g., 2024")
    term = models.CharField(max_length=9, choices=TERM_CHOICES)
    credit_limit = models.IntegerField(help_text="Maximum credits a student can enroll in this semester.")

    def __str__(self):
        return self.term + " " + str(self.year)


class University(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Faculty(models.Model):
    name = models.CharField(max_length=255)
    university = models.ForeignKey(University, related_name='faculties', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Subject(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=255)
    credits = models.IntegerField()
    description = models.TextField(blank=True)
    offered_semesters = models.ManyToManyField(Semester, related_name='subjects')
    university = models.ForeignKey(University, related_name='subjects', on_delete=models.CASCADE)
    capacity = models.IntegerField(default=30, help_text="Maximum number of students that can enroll.")
    faculty = models.ForeignKey(Faculty, related_name='subjects', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class SubjectSemester(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=9, choices=DAY_CHOICES)
    start_time = models.TimeField(help_text="Start time of the class")
    end_time = models.TimeField(help_text="End time of the class")

    class Meta:
        unique_together = ('subject', 'semester', 'day_of_week', 'start_time')

    def __str__(self):
        return f"{self.subject.title} ({self.subject.university.name}) ({self.semester.term} {self.semester.year}) on {self.day_of_week} from {self.start_time} to {self.end_time}"


class StudyPlan(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='study_plans')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='study_plans')
    subjects = models.ManyToManyField(Subject, related_name='study_plans')

    def total_credits(self):
        return sum(subject.credits for subject in self.subjects.all())


class ClassSchedule(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='class_schedules')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='class_schedules')
    subject_semester = models.ForeignKey(SubjectSemester, on_delete=models.CASCADE, related_name='class_schedules', default=1)
    day_of_week = models.CharField(max_length=9, choices=DAY_CHOICES)
    start_time = models.TimeField(help_text="Start time of the class", default=time(12, 0))
    end_time = models.TimeField(help_text="End time of the class", default=time(13, 0))

    class Meta:
        unique_together = ('student', 'semester', 'day_of_week', 'start_time')

    def __str__(self):
        return f"{self.subject_semester.subject.title} ({self.subject_semester.semester.term} {self.subject_semester.semester.year}) on {self.day_of_week} from {self.start_time} to {self.end_time}"

