from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('list_retrieve_nft_view', views.ListRetrieveNFTView, basename='list_retrieve_nft_view')
router.register('create_update_nft_view', views.CreateUpdateNFTView, basename='create_update_nft_view')
router.register('user_nfts_list', views.UserNFTsListView, basename='user_nfts_list')
router.register('nfts_category', views.NFTCategoryView, basename='nfts_category')
# router.register('nfts_category', views.NFTCategoryView, basename='nfts_category')
router.register('nfts_tags', views.NFTTagView, basename='nfts_tags')

urlpatterns = [
    path('', include(router.urls)),
    # path('profile/', UserProfileListView.as_view({'get': 'get'}), name="profile"),
]
