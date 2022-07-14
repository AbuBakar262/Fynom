from django.urls import path, include

from . import views
from .views import AdminLoginView, AdminChangePasswrodView, \
    UserLogin, UserProfileUpdateView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('user_profile_details_view', views.UserProfileDetailsView, basename='user_profile_details_view')
router.register('user_profile_status_update_view', views.UserProfileStatusUpdateView,
                basename='user_profile_status_update_view')
router.register('user_collection', views.UserCollection, basename='user_collection') # create and update
router.register('user_collection_list', views.UserCollectionListView, basename='user_collection_list') # list user collection by id
router.register('list_user_collection', views.ListUserCollection, basename='list_user_collection') # list user collection and retrieve
router.register('profile', views.UserProfileListView, basename='profile') # user profile list and retrieve
router.register('terms_policies', views.TermsAndPoliciesView, basename='terms_policies')

urlpatterns = [
    path('', include(router.urls)),
    path('profile_update/<int:pk>/', UserProfileUpdateView.as_view({'patch': 'patch'}), name="profile_update"),
    path('admin_login/', AdminLoginView.as_view(), name="login"),
    path('change_password/', AdminChangePasswrodView.as_view(), name="change_password"),
    path('user_login/', UserLogin.as_view(), name="user_login"),
]
