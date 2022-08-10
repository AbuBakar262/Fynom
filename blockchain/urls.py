from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register('list_retrieve_nft_view', views.ListRetrieveNFTView, basename='list_retrieve_nft_view')
router.register('create_update_nft_view', views.CreateUpdateNFTView, basename='create_update_nft_view')
router.register('user_nfts_list', views.UserNFTsListView, basename='user_nfts_list')
router.register('nfts_category', views.NFTCategoryView, basename='nfts_category')
# router.register('nfts_category', views.NFTCategoryView, basename='nfts_category')
router.register('nfts_tags', views.NFTTagView, basename='nfts_tags')
router.register('user_nft_status_update', views.UserNFTStatusUpdateView, basename='user_nft_status_update')
router.register('list_transactions_of_nft', views.ListTransectionNFTView, basename='list_transactions_of_nft')
router.register('nft_commission', views.NFTCommissionView, basename='nft_commission')
router.register('delete_doc', views.DeleteDocs, basename='delete_doc')

urlpatterns = [
    path('', include(router.urls)),
    path('claim_nft/<int:pk>/', ClaimNFTView.as_view({'patch': 'partial_update'}), name="claim_nft"),
    path('bid_on_nft_details/<int:pk>/', BidOnNFTDetailsView.as_view({'get': 'retrieve'}), name="bid_on_nft_details"),
    path('do_bid_on_nft/', DoBidOnNFTView.as_view({'post': 'create'}), name="do_bid_on_nft"),
    # path('profile/', UserProfileListView.as_view({'get': 'get'}), name="profile"),
]
