from django.urls import path, include
from .views import *
from . import views

urlpatterns = [
    path('admin_forgot_password/', AdminForgetPassword.as_view(), name='admin_forgot_password'),
    path('admin_reset_password/<uidb64>/<token>/', AdminResetPassword.as_view(), name='admin_reset_password')
]
