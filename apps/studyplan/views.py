from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from apps.studyplan.models import University, Subject, Semester, StudyPlan, ClassSchedule
from apps.authorization.models import UserProfile


class AddSubjectToStudyPlanAPIView(APIView):
    def post(self, request, semester_id, subject_id):
        user_profile_id = request.data.get('user_profile_id')
        try:
            student = UserProfile.objects.get(id=user_profile_id)
            semester = Semester.objects.get(id=semester_id)
            subject = Subject.objects.get(id=subject_id)

            if subject not in semester.subjects.all():
                return Response({'error': 'Subject not offered in this semester'}, status=status.HTTP_400_BAD_REQUEST)

            study_plan, created = StudyPlan.objects.get_or_create(student=student, semester=semester)
            if study_plan.total_credits() + subject.credits > semester.credit_limit:
                return Response({'error': 'Adding this subject exceeds credit limit'}, status=status.HTTP_400_BAD_REQUEST)

            study_plan.subjects.add(subject)
            study_plan.save()
            return Response({'success': f'Subject {subject.title} added successfully'}, status=status.HTTP_201_CREATED)
        except (UserProfile.DoesNotExist, Semester.DoesNotExist, Subject.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class AvailableSubjectsAPIView(APIView):
    def get(self, request, semester_id):
        try:
            semester = Semester.objects.get(id=semester_id)
            subjects = semester.subjects.all().values('id', 'code', 'title', 'credits', 'description', 'university__name')
            return Response(list(subjects), status=status.HTTP_200_OK)
        except Semester.DoesNotExist:
            return Response({'error': 'Semester not found'}, status=status.HTTP_404_NOT_FOUND)


class UniversityListAPIView(APIView):
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
            'id', 'day_of_week', 'time', 'subject__title', 'semester__year', 'semester__term'
        )
        return Response(list(schedules), status=status.HTTP_200_OK)

    def post(self, request):
        user_profile_id = request.data.get('user_profile_id')
        semester_id = request.data.get('semester_id')
        subject_id = request.data.get('subject_id')
        day_of_week = request.data.get('day_of_week')
        time = request.data.get('time')

        if not all([user_profile_id, semester_id, subject_id, day_of_week, time]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = UserProfile.objects.get(id=user_profile_id)
            semester = Semester.objects.get(id=semester_id)
            subject = Subject.objects.get(id=subject_id)

            if subject not in semester.subjects.all():
                return Response({'error': 'Subject not offered in this semester'}, status=status.HTTP_400_BAD_REQUEST)

            schedule, created = ClassSchedule.objects.get_or_create(
                student=student,
                semester=semester,
                subject=subject,
                day_of_week=day_of_week,
                time=time
            )

            if created:
                return Response({
                    'message': 'Class schedule created successfully',
                    'schedule_id': schedule.id
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Schedule already exists'}, status=status.HTTP_409_CONFLICT)

        except (UserProfile.DoesNotExist, Semester.DoesNotExist, Subject.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)