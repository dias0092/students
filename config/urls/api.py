from django.urls import path, include

urlpatterns = [
    path("auth/", include("apps.authorization.urls")),
    path("studyplan/", include("apps.studyplan.urls")),
]
