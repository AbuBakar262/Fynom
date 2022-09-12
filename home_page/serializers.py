from django.db.models import F
from rest_framework import serializers
from user.models import User
from blockchain.models import Collection, UserWalletAddress


# class AdminLoginSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['email', 'password']
