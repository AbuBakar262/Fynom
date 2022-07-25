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
    tag_title = serializers.CharField(required=True)

    class Meta:
        model = NFT
        fields = ["id", "thumbnail", "nft_picture", "teaser", "nft_title", "nft_collection",
                  "description", "nft_category", "royality", "hash", "contract_id", 'top_nft', "nft_creator", "nft_owner",
                  "nft_status", "status_remarks", "nft_sell_type", "fix_price", 'tag_title']

    def create(self, validated_data):
        with transaction.atomic():
            nft_docs = dict(self.context['request'].data.lists())['documents']
            nft_tags = validated_data.pop('tag_title').split(',')
            # nft_tags = validated_data.pop('tags')
            # document = validated_data.pop('document')
            # nft_title = validated_data.get('nft_title')
            nft = NFT.objects.create(**validated_data)
            # send_otp(validated_data.get('phone'), "Your Confirmation code is : ")
            for doc in nft_docs:
                SupportingDocuments.objects.create(nft_create_info=nft, documents=doc)
            # tag_obj = Tags.objects.create()
            # for tag in nft_tags:
            #     # Tags.objects.set(nft_create_info=nft, tag_title=tag)
            #     # add_tag = Tags.objects.filter(tag_title__in=tag)
            #     instance = Tags.objects.create(tag_title=tag)
            #     instance.nft_create_info.add(*nft)
            print()
            nft.tags_set.add(*nft_tags)
            return nft


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['documents'] = SupportingDocuments.objects.filter(nft_create_info_id=instance.id).values('id', 'documents', 'nft_create_info')
        # data['tag_title'] = Tags.objects.filter(nft_create_info__nft_id=instance.id)
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