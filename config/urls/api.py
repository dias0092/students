from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("auth/", include("apps.authorization.urls")),
    path("studyplan/", include("apps.studyplan.urls")),
]