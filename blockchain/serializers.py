from django.db import transaction
from rest_framework import serializers

from blockchain.models import *
from user.models import User

class NftTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = "__all__"

class NFTSupportingDocumentsSerializer(serializers.ModelSerializer):
    documents = serializers.ListField(child=serializers.FileField(required=True))
    class Meta:
        model = SupportingDocuments
        fields = ["id", "documents", "nft_create_info"]


class NFTViewSerializer(serializers.ModelSerializer):
    documents = NFTSupportingDocumentsSerializer(many=True, write_only=True)
    class Meta:
        model = NFT
        fields = ["id", "thumbnail", "documents", "nft_picture", "teaser", "nft_title", "nft_collection",
                  "description", "nft_category", "royality", "hash", "contract_id", "nft_creator", "nft_owner",
                  "nft_status", "status_remarks", "nft_sell_type", "fix_price",]

    def create(self, validated_data):
        with transaction.atomic():
            documents = validated_data.pop('documents')
            # nft_title = validated_data.get('nft_title')
            nft = NFT.objects.create(**validated_data)
            # send_otp(validated_data.get('phone'), "Your Confirmation code is : ")
            for doc in documents:
                SupportingDocuments.objects.create(nft=nft, **doc)
            return NFT

class NFTCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NFTCategory
        fields = "__all__"
