from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("auth/", include("apps.authorization.urls")),
    path("studyplan/", include("apps.studyplan.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.AVATAR_URL, document_root=settings.AVATAR_ROOT)