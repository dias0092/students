from django.urls import path
from apps.studyplan.views import UniversityListAPIView, UniversityDetailAPIView, SubjectListAPIView, SubjectDetailAPIView


urlpatterns = [
    path('api/universities/', UniversityListAPIView.as_view(), name='university_list'),
    path('api/universities/<int:pk>/', UniversityDetailAPIView.as_view(), name='university_detail'),
    path('api/subjects/', SubjectListAPIView.as_view(), name='subject_list'),
    path('api/subjects/<int:pk>/', SubjectDetailAPIView.as_view(), name='subject_detail'),
]