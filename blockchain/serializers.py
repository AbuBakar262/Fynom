from rest_framework import serializers

from blockchain.models import *
from user.models import User

class NFTViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFT
        fields = "__all__"