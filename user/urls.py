from django.urls import path, include
from django.conf.urls.static import static
from backend import settings
from . import views
from .views import UserLoginView, UserChangePasswrodView, SendPasswordResetEmailView, UserPasswordResetView, \
    UserProfileListView, UserProfileUpdateView, UserCollection

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('user-profile-details-view', views.UserProfileDetailsView, basename='user_profile_details_view')
router.register('user-profile-status-update-view', views.UserProfileStatusUpdateView, basename='user_profile_status_update_view')
router.register('user-collection', views.UserCollection, basename='user_collection')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileListView.as_view({'get': 'get'}), name=""),
    path('profile-update/', UserProfileUpdateView.as_view({'patch': 'patch', 'post': 'post'}), name=""),
    path('login/', UserLoginView.as_view(), name="login"),
    path('change-password/', UserChangePasswrodView.as_view(), name="change_password"),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name="send_reset_password_email"),
    path('rest-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='rest_password'),
    path('user-status/<int:pk>/', views.UserStatusView.as_view(), name="user_status"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
