# Generated by Django 5.0.6 on 2024-05-16 15:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studyplan', '0002_alter_semester_term'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semester',
            name='term',
            field=models.CharField(choices=[('Қыс', 'Winter'), ('Көктем', 'Spring'), ('Жаз', 'Summer'), ('Күз', 'Fall')], max_length=9),
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faculties', to='studyplan.university')),
            ],
        ),
        migrations.AddField(
            model_name='subject',
            name='faculty',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='studyplan.faculty'),
        ),
    ]