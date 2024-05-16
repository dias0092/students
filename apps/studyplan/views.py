from datetime import time
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from apps.studyplan.models import Subject, Semester, ClassSchedule, SubjectSemester
from apps.authorization.models import UserProfile


class AvailableSubjectSemestersAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            subject_semesters = SubjectSemester.objects.all().values(
                'id',
                'subject__id',
                'subject__code',
                'subject__title',
                'subject__credits',
                'subject__description',
                'subject__university__name',
                'subject__faculty__name',
                'semester__id',
                'semester__year',
                'semester__term',
                'day_of_week',
                'start_time',
                'end_time'
            )
            return Response(list(subject_semesters), status=status.HTTP_200_OK)
        except Semester.DoesNotExist:
            return Response({'error': 'Semester not found'}, status=status.HTTP_404_NOT_FOUND)


class SubjectListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        subjects = Subject.objects.all()
        subject_list = []

        for subject in subjects:
            offered_terms = subject.offered_semesters.all().values_list('term', 'year')
            offered_terms_list = [f"{term} {year}" for term, year in offered_terms]
            subject_data = {
                'id': subject.id,
                'title': subject.title,
                'credits': subject.credits,
                'description': subject.description,
                'code': subject.code,
                'university_name': subject.university.name,
                'faculty_name': subject.faculty.name,
                'offered_terms': offered_terms_list
            }
            subject_list.append(subject_data)

        return Response(subject_list, status=status.HTTP_200_OK)


class ClassScheduleListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_profile_id = UserProfile.objects.get(user=request.user).id
        if not user_profile_id:
            return Response({'error': 'User profile ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        schedules = ClassSchedule.objects.filter(student_id=user_profile_id).values(
            'id', 'day_of_week', 'start_time', 'end_time', 'subject_semester__subject__title', 'semester__year', 'semester__term'
        )
        return Response(list(schedules), status=status.HTTP_200_OK)

    def post(self, request):
        schedules_data = request.data.get('schedules', [])

        if not schedules_data:
            return Response({'error': 'No schedules provided'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        try:
            student = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                added_schedules = []
                for schedule_data in schedules_data:
                    semester_id = schedule_data.get('semester_id')
                    subject_semester_id = schedule_data.get('subject_semester_id')
                    day_of_week = schedule_data.get('day_of_week')
                    start_time = schedule_data.get('start_time')
                    end_time = schedule_data.get('end_time')

                    if not all([semester_id, subject_semester_id, day_of_week, start_time, end_time]):
                        return Response({'error': 'Missing required fields in one or more schedules'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    start_time = time.fromisoformat(start_time)
                    end_time = time.fromisoformat(end_time)

                    semester = Semester.objects.get(id=semester_id)
                    subject_semester = SubjectSemester.objects.get(id=subject_semester_id)

                    if student.university == subject_semester.subject.university:
                        return Response({'error': 'Cannot add subject from the same university'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    existing_classes = ClassSchedule.objects.filter(
                        student=student,
                        semester=semester,
                        subject_semester__subject__university__ne=student.university
                    )

                    if existing_classes.exists():
                        return Response(
                            {'error': 'You can only add one subject from a different university per semester'},
                            status=status.HTTP_400_BAD_REQUEST)

                    time_conflicts = ClassSchedule.objects.filter(
                        student=student,
                        semester=semester,
                        day_of_week=day_of_week,
                        start_time__lt=end_time,
                        end_time__gt=start_time
                    )

                    if time_conflicts.exists():
                        conflicting_class = time_conflicts.first()
                        return Response(
                            {'error': f'Time conflict with {conflicting_class.subject_semester.subject.title}'},
                            status=status.HTTP_400_BAD_REQUEST)

                    new_schedule = ClassSchedule.objects.create(
                        student=student,
                        semester=semester,
                        subject_semester=subject_semester,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time
                    )
                    added_schedules.append({
                        'id': new_schedule.id,
                        'user_profile_id': student.id,
                        'semester_id': semester_id,
                        'subject_semester_id': subject_semester_id,
                        'day_of_week': day_of_week,
                        'start_time': start_time.isoformat(),
                        'end_time': end_time.isoformat(),
                        'subject_title': subject_semester.subject.title,
                        'semester_term': semester.term,
                        'semester_year': semester.year
                    })

                return Response({'success': 'Classes added to schedule successfully', 'schedules': added_schedules},
                                status=status.HTTP_201_CREATED)

        except (Semester.DoesNotExist, SubjectSemester.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)