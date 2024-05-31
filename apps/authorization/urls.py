from django.urls import path
from apps.authorization.views import LoginAPIView, UserDetailAPIView, ChangeAvatarAPIView, ChangePasswordAPIView


urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('user/', UserDetailAPIView.as_view(), name='user-detail'),
    path('change-avatar/', ChangeAvatarAPIView.as_view(), name='change-avatar'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
]