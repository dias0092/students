from django.urls import path
from apps.studyplan.views import(
    UniversityListAPIView,
    UniversityDetailAPIView,
    SubjectListAPIView,
    SubjectDetailAPIView,
    AvailableSubjectsAPIView,
    AddSubjectToStudyPlanAPIView,
    ClassScheduleListCreateAPIView
)


urlpatterns = [
    path('api/universities/', UniversityListAPIView.as_view(), name='university_list'),
    path('api/universities/<int:pk>/', UniversityDetailAPIView.as_view(), name='university_detail'),
    path('api/subjects/', SubjectListAPIView.as_view(), name='subject_list'),
    path('api/subjects/<int:pk>/', SubjectDetailAPIView.as_view(), name='subject_detail'),
    path('available-subjects/<int:semester_id>/', AvailableSubjectsAPIView.as_view(), name='available-subjects'),
    path('add-subject/<int:semester_id>/', AddSubjectToStudyPlanAPIView.as_view(), name='add-subject-to-study-plan'),
    path('class-schedules/', ClassScheduleListCreateAPIView.as_view(), name='class-schedules-list-create'),
]