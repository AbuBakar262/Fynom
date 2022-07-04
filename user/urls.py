from django.urls import path, include

from . import views
from .views import AdminLoginView, AdminChangePasswrodView, SendPasswordResetEmailView, UserPasswordResetView, \
    UserProfileListView, UserProfileCreateView, UserProfileUpdateView

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('user_profile_details_view', views.UserProfileDetailsView, basename='user_profile_details_view')
router.register('user_profile_status_update_view', views.UserProfileStatusUpdateView,
                basename='user_profile_status_update_view')
router.register('user_collection', views.UserCollection, basename='user_collection')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileListView.as_view({'get': 'get'}), name="profile"),
    path('profile_create/', UserProfileCreateView.as_view({'post': 'post'}), name="profile_create"),
    path('profile_update/<int:pk>/', UserProfileUpdateView.as_view({'patch': 'patch'}), name="profile_update"),
    path('admin_login/', AdminLoginView.as_view(), name="login"),
    path('change_password/', AdminChangePasswrodView.as_view(), name="change_password"),

    # path('user_status/', views.UserStatusView.as_view(), name="user_status"),
]
