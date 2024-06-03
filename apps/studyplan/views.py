import logging
from datetime import time
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from apps.studyplan.models import Subject, Semester, ClassSchedule, SubjectSemester, StudyPlan
from apps.authorization.models import UserProfile
from fuzzywuzzy import fuzz


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
            'id',
            'day_of_week',
            'start_time',
            'end_time',
            'subject_semester__subject__title',
            'subject_semester__subject__description',
            'subject_semester__subject__credits',
            'subject_semester__subject__university__name',
            'subject_semester_id'
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

                    # Check for existing schedule with the same subject_semester_id
                    if ClassSchedule.objects.filter(student=student, subject_semester=subject_semester).exists():
                        return Response({
                                            'error': f'Schedule with subject {subject_semester.subject.title} for semester {subject_semester.semester.term} {subject_semester.semester.year} already exists'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    # Check for time conflicts
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

        except (UserProfile.DoesNotExist, Semester.DoesNotExist, SubjectSemester.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request, pk=None):
        user_profile_id = UserProfile.objects.get(user=request.user).id
        subject_semester_id = pk

        if not subject_semester_id:
            return Response({'error': 'Schedule ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            schedule = ClassSchedule.objects.get(subject_semester_id=subject_semester_id, student_id=user_profile_id)
            schedule.delete()
            return Response({'message': 'Class schedule deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except ClassSchedule.DoesNotExist:
            return Response({'error': 'Class schedule not found'}, status=status.HTTP_404_NOT_FOUND)


class SimilarSubjectsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger = logging.getLogger(__name__)

        try:
            user_profile = request.user.userprofile
            user_university = user_profile.university

            if not user_university:
                print("User is not associated with any university")
                return Response({'error': 'User is not associated with any university'}, status=status.HTTP_400_BAD_REQUEST)

            university_name = request.data.get('university')
            faculty_name = request.data.get('faculty')
            term = request.data.get('term')
            year = request.data.get('year')

            filters = {}
            if university_name:
                filters['subjects__university__name'] = university_name
            if faculty_name:
                filters['subjects__faculty__name'] = faculty_name
            if term:
                filters['subjects__offered_semesters__term'] = term
            if year:
                filters['subjects__offered_semesters__year'] = year

            print(f"Filters: {filters}")

            user_class_schedules = ClassSchedule.objects.filter(student=user_profile).select_related('subject_semester__subject')
            user_subjects = [schedule.subject_semester.subject for schedule in user_class_schedules]

            print(f"User subjects: {[subject.title for subject in user_subjects]}")

            other_study_plans = StudyPlan.objects.filter(**filters).distinct()

            print(f"Other study plans count: {other_study_plans.count()}")

            other_university_subjects = set()
            for plan in other_study_plans:
                other_university_subjects.update(plan.subjects.all())

            print(f"Other university subjects: {[subject.title for subject in other_university_subjects]}")

            similar_subjects = []

            for user_subject in user_subjects:
                for other_subject in other_university_subjects:
                    similarity = fuzz.token_set_ratio(user_subject.description, other_subject.description)
                    if similarity >= 1:
                        subject_semester = other_subject.subjectsemester_set.filter(semester__term=term, semester__year=year).first()
                        if subject_semester:
                            similar_subjects.append({
                                'title': other_subject.title,
                                'description': other_subject.description,
                                'university': other_subject.university.name,
                                'faculty': other_subject.faculty.name if other_subject.faculty else None,
                                'term': f"{term} {year}",
                                'semester_id': subject_semester.semester.id,
                                'subject_semester_id': subject_semester.id,
                                'day_of_week': subject_semester.day_of_week,
                                'start_time': subject_semester.start_time,
                                'end_time': subject_semester.end_time,
                                'credits': other_subject.credits,
                                'similarity': similarity
                            })
            unique_subjects = {}
            for subject in similar_subjects:
                title = subject['title']
                if title not in unique_subjects or subject['similarity'] > unique_subjects[title]['similarity']:
                    unique_subjects[title] = subject

            similar_subjects = list(unique_subjects.values())

            if not similar_subjects:
                similar_subjects = "no subjects"

            return Response(similar_subjects, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error occurred: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
