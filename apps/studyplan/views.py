from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from apps.studyplan.models import University, Subject


class UniversityListAPIView(APIView):
    def get(self, request):
        universities = University.objects.all()
        return JsonResponse(list(universities), safe=False, status=status.HTTP_200_OK)

    def post(self, request):
        name = request.data.get('name')
        code = request.data.get('code')
        description = request.data.get('description')
        if name and code and description:
            university = University.objects.create(name=name, code=code, description=description)
            return JsonResponse({'id': university.id, 'name': university.name, 'code': university.code, 'description': university.description}, status=status.HTTP_201_CREATED)
        return JsonResponse({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


class UniversityDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            university = University.objects.get(pk=pk)
            return JsonResponse(university, status=status.HTTP_200_OK)
        except University.DoesNotExist:
            return JsonResponse({'error': 'University not found'}, status=status.HTTP_404_NOT_FOUND)


class SubjectListAPIView(APIView):
    def get(self, request):
        subjects = Subject.objects.all()
        return JsonResponse(list(subjects), safe=False, status=status.HTTP_200_OK)

    def post(self, request):
        title = request.data.get('title')
        credits = request.data.get('credits')
        description = request.data.get('description')
        code = request.data.get('code')
        university_id = request.data.get('university_id')
        if title and credits and description and code and university_id:
            try:
                university = University.objects.get(pk=university_id)
                subject = Subject.objects.create(title=title, credits=credits, description=description, code=code, university=university)
                return JsonResponse({'id': subject.id, 'title': subject.title, 'credits': subject.credits, 'description': subject.description, 'code': subject.code, 'university_id': subject.university.id}, status=status.HTTP_201_CREATED)
            except University.DoesNotExist:
                return JsonResponse({'error': 'University not found'}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


class SubjectDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
            return JsonResponse(subject, status=status.HTTP_200_OK)
        except Subject.DoesNotExist:
            return JsonResponse({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
            subject.title = request.data.get('title', subject.title)
            subject.credits = request.data.get('credits', subject.credits)
            subject.description = request.data.get('description', subject.description)
            subject.code = request.data.get('code', subject.code)
            subject.save()
            return JsonResponse({'id': subject.id, 'title': subject.title, 'credits': subject.credits, 'description': subject.description, 'code': subject.code, 'university_id': subject.university.id}, status=status.HTTP_200_OK)
        except Subject.DoesNotExist:
            return JsonResponse({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
            subject.delete()
            return JsonResponse({'message': 'Subject deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Subject.DoesNotExist:
            return JsonResponse({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)

