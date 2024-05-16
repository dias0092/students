from datetime import time

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from apps.studyplan.models import University, Subject, Semester, StudyPlan, ClassSchedule, SubjectSemester
from apps.authorization.models import UserProfile
from django.db import transaction


class AddSubjectToStudyPlanAPIView(APIView):
    def post(self, request, semester_id):
        user_profile_id = request.data.get('user_profile_id')
        subject_ids = request.data.get('subject_ids')

        if not subject_ids:
            return Response({'error': 'No subjects provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = UserProfile.objects.get(id=user_profile_id)
            semester = Semester.objects.get(id=semester_id)
            added_subjects = []

            with transaction.atomic():
                study_plan, created = StudyPlan.objects.get_or_create(student=student, semester=semester)

                for subject_id in subject_ids:
                    subject = Subject.objects.get(id=subject_id)

                    if subject not in semester.subjects.all():
                        continue

                    current_enrollment = StudyPlan.objects.filter(subjects=subject, semester=semester).count()
                    if current_enrollment >= subject.capacity:
                        continue

                    if study_plan.total_credits() + subject.credits > semester.credit_limit:
                        continue

                    study_plan.subjects.add(subject)
                    added_subjects.append({
                        'id': subject.id,
                        'title': subject.title,
                        'code': subject.code,
                        'credits': subject.credits,
                        'description': subject.description,
                    })

                study_plan.save()

            return Response({'success': 'Subjects added successfully', 'subjects': added_subjects}, status=status.HTTP_201_CREATED)

        except (UserProfile.DoesNotExist, Semester.DoesNotExist, Subject.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AvailableSubjectsAPIView(APIView):
    def get(self, request, semester_id):
        try:
            semester = Semester.objects.get(id=semester_id)
            subjects = semester.subjects.all().values('id', 'code', 'title', 'credits', 'description', 'university__name')
            return Response(list(subjects), status=status.HTTP_200_OK)
        except Semester.DoesNotExist:
            return Response({'error': 'Semester not found'}, status=status.HTTP_404_NOT_FOUND)


class UniversityListAPIView(APIView):
    # permission_classes = (IsAuthenticated,)
    def get(self, request):
        universities = University.objects.all().values('id', 'name', 'code', 'description')
        return Response(list(universities), status=status.HTTP_200_OK)


class UniversityDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            university = University.objects.values('id', 'name', 'code', 'description').get(pk=pk)
            return Response(university, status=status.HTTP_200_OK)
        except University.DoesNotExist:
            return Response({'error': 'University not found'}, status=status.HTTP_404_NOT_FOUND)


class SubjectListAPIView(APIView):
    def get(self, request):
        subjects = Subject.objects.all().values('id', 'title', 'credits', 'description', 'code', 'university_id')
        return Response(list(subjects), status=status.HTTP_200_OK)


class SubjectDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
            return Response(subject, status=status.HTTP_200_OK)
        except Subject.DoesNotExist:
            return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)


class ClassScheduleListCreateAPIView(APIView):
    def get(self, request):
        user_profile_id = request.query_params.get('user_profile_id')
        if not user_profile_id:
            return Response({'error': 'User profile ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        schedules = ClassSchedule.objects.filter(student_id=user_profile_id).values(
            'id', 'day_of_week', 'start_time', 'end_time', 'subject_semester__subject__title', 'semester__year', 'semester__term'
        )
        return Response(list(schedules), status=status.HTTP_200_OK)

    def post(self, request):
        user_profile_id = request.data.get('user_profile_id')
        semester_id = request.data.get('semester_id')
        subject_semester_id = request.data.get('subject_semester_id')
        day_of_week = request.data.get('day_of_week')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')

        if not all([user_profile_id, semester_id, subject_semester_id, day_of_week, start_time, end_time]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        start_time = time.fromisoformat(start_time)
        end_time = time.fromisoformat(end_time)

        try:
            student = UserProfile.objects.get(id=user_profile_id)
            semester = Semester.objects.get(id=semester_id)
            subject_semester = SubjectSemester.objects.get(id=subject_semester_id)

            if subject_semester.semester != semester:
                return Response({'error': 'Subject semester does not match the given semester'}, status=status.HTTP_400_BAD_REQUEST)

            # Check for time conflicts
            existing_classes = ClassSchedule.objects.filter(
                student=student,
                semester=semester,
                day_of_week=day_of_week
            )

            for existing_class in existing_classes:
                if start_time < existing_class.end_time and end_time > existing_class.start_time:
                    return Response({'error': f'Time conflict with {existing_class.subject_semester.subject.title}'}, status=status.HTTP_400_BAD_REQUEST)

            ClassSchedule.objects.create(
                student=student,
                semester=semester,
                subject_semester=subject_semester,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )

            return Response({'success': 'Class added to schedule successfully'}, status=status.HTTP_201_CREATED)

        except (UserProfile.DoesNotExist, Semester.DoesNotExist, SubjectSemester.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)