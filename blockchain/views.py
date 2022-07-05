from rest_framework.response import Response
from rest_framework import status
from user.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import viewsets
from user.custom_permissions import IsApprovedUser

# class ListNFTView(viewsets.ViewSet):

