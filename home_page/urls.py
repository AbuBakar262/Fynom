from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

# router.register('user_block_unblock', views.UserProfileBlockedView, basename='user_block_unblock')


urlpatterns = [
    path('', include(router.urls)),
    # path('do_bid_on_nft/', DoBidOnNFTView.as_view({'post': 'create'}), name="do_bid_on_nft"),
    # path('contact_us/', UserDisputeManagementView.as_view({'post': 'dispute_email'}), name="contact_us"),
    path('featured_nft/', FeaturedNftView.as_view({'get': 'list'}), name="featured_nft"),
    path('top_nft/', TopNftView.as_view({'get': 'list'}), name="top_nft"),
    path('highest_bidded/', HighestBiddedNftView.as_view({'get': 'list'}), name="highest_bidded"),
    path('collection_featured_nft/', CollectionFeaturedNftView.as_view({'get': 'list'}), name="collection_featured_nft"),
    # used for tranding and discoverd nfts two in one
    path('trending_nft/', TrendingNftsView.as_view({'get': 'list'}), name="trending_nft"),
    path('feature_nft/', FeatureNFTView.as_view({'post': 'featureNFT'}), name="feature_nft"),
]
