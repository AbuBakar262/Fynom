from django.db import transaction
from rest_framework import serializers

from blockchain.models import *
from user.models import User

class NftTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = "__all__"

# class NftSupportingDocumentsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SupportingDocuments
#         fields = ['id', 'documents', 'nft_create_info']



class NFTViewSerializer(serializers.ModelSerializer):
    # tags = serializers.ListField(child=serializers.CharField(required=True), allow_empty=False)
    # tags = serializers.SerializerMethodField('get_tag')

    class Meta:
        model = NFT
        fields = ["id", "thumbnail", "nft_picture", "teaser", "nft_title", "nft_collection",
                  "description", "nft_category", "royality", "hash", "contract_id", 'top_nft', "nft_creator", "nft_owner",
                  "nft_status", "status_remarks", "nft_sell_type", "fix_price"]

    def create(self, validated_data):
        with transaction.atomic():
            nft_docs = dict(self.context['request'].data.lists())['documents']

            nft = NFT.objects.create(**validated_data)
            for doc in nft_docs:
                SupportingDocuments.objects.create(nft_create_info=nft, documents=doc)
            return nft

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tag_title'] = NftTagSerializer(instance.tags_set.filter(nft_create_info__id=instance.id), many=True).data
        data['documents'] = SupportingDocuments.objects.filter(nft_create_info_id=instance.id).values('id', 'documents', 'nft_create_info')
        return data





class NFTCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NFTCategory
        fields = "__all__"

# class NFTSerializerNew(serializers.ModelSerializer):
#     document = serializers.SerializerMethodField('get_doc')
#     class Meta:
#         model = NFT
#         fields = '__all__'
#
#     def get_doc(self,obj):
#         try:
#             doc = SupportingDocuments.objects.filter(nft_create_info__id=obj.id)
#             serializer = NftSupportingDocumentsSerializer(doc, many=True)
#             return serializer.data
#         except Exception as e:
#             return None