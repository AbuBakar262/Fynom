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
]
