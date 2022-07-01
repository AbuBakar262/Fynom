from django.urls import path, include

from . import views
from .views import AdminLoginView, UserChangePasswrodView, SendPasswordResetEmailView, UserPasswordResetView, \
    UserProfileListView, UserProfileUpdateView

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('user_profile_details_view', views.UserProfileDetailsView, basename='user_profile_details_view')
router.register('user_profile_status_update_view', views.UserProfileStatusUpdateView,
                basename='user_profile_status_update_view')
router.register('user-collection', views.UserCollection, basename='user_collection')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileListView.as_view({'get': 'get'}), name=""),
    path('profile_update/', UserProfileUpdateView.as_view({'patch': 'patch', 'post': 'post'}), name=""),
    path('admin_login/', AdminLoginView.as_view(), name="login"),
    path('change_password/', UserChangePasswrodView.as_view(), name="change_password"),
    path('send_reset_password-email/', SendPasswordResetEmailView.as_view(), name="send_reset_password_email"),
    path('rest_password/<uid>/<token>/', UserPasswordResetView.as_view(), name='rest_password'),
    path('user_status/<int:pk>/', views.UserStatusView.as_view(), name="user_status"),
]
