from django.urls import path
from apps.studyplan.views import(
    SubjectListAPIView,
    AvailableSubjectSemestersAPIView,
    ClassScheduleListCreateAPIView
)


urlpatterns = [
    path('api/subjects/', SubjectListAPIView.as_view(), name='subject_list'),
    path('available-subjects/', AvailableSubjectSemestersAPIView.as_view(), name='available-subjects'),
    path('class-schedules/', ClassScheduleListCreateAPIView.as_view(), name='class-schedules-list-create'),
]