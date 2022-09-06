from django.urls import path, include
from .views import *
from . import views

urlpatterns = [
    path('admin_forgot_password/', AdminForgetPassword.as_view(), name='admin_forgot_password'),
    path('admin_reset_password/<uidb64>/<token>/', AdminResetPassword.as_view(), name='admin_reset_password'),
    path('about_us/', AboutUsView.as_view({'get': 'show_items'}), name="about_us"),
    path('about_us/<int:pk>/', AboutUsView.as_view({'get': 'show_item', 'put':'update_item'}), name="about_us_id")
    # path('about_us/', AboutUsView.as_view({'get': 'list'}), name='admin_reset_password')
]
