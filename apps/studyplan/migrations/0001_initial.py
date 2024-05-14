# Generated by Django 5.0.6 on 2024-05-14 15:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
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
                ('title', models.CharField(max_length=255)),
                ('credits', models.IntegerField()),
                ('description', models.TextField()),
                ('code', models.CharField(max_length=20, unique=True)),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='studyplan.university')),
            ],
        ),
    ]
