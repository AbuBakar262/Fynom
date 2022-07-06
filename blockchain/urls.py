from django.urls import path, include

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# router.register('list_user_collection', views.ListUserCollection, basename='list_user_collection')

urlpatterns = [
    path('', include(router.urls)),
    # path('profile/', UserProfileListView.as_view({'get': 'get'}), name="profile"),
]
