from django.urls import path
from apps.authorization.views import LoginAPIView, UserDetailAPIView


urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('user/', UserDetailAPIView.as_view(), name='user-detail'),
]