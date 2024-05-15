# Generated by Django 5.0.6 on 2024-05-15 13:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authorization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(help_text='The academic year, e.g., 2024')),
                ('term', models.CharField(help_text='E.g., Fall, Spring, Summer', max_length=100)),
                ('credit_limit', models.IntegerField(help_text='Maximum credits a student can enroll in this semester.')),
            ],
        ),
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('credits', models.IntegerField()),
                ('description', models.TextField(blank=True)),
                ('offered_semesters', models.ManyToManyField(related_name='subjects', to='studyplan.semester')),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='studyplan.university')),
            ],
        ),
        migrations.CreateModel(
            name='StudyPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='study_plans', to='studyplan.semester')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='study_plans', to='authorization.userprofile')),
                ('subjects', models.ManyToManyField(related_name='study_plans', to='studyplan.subject')),
            ],
        ),
    ]
