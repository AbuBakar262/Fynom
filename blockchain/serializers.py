from django.db import transaction
from django.db.models.functions import Concat
from rest_framework import serializers

from blockchain.models import *
from blockchain.utils import get_eth_price
from user.models import User
from user.serializers import UserProfileDetailsViewSerializer


class NftTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ["id", "tag_title", "created_at", "updated_at"]


class NFTCommissionViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        fields = ["id", "set_commission", "created_at", "updated_at"]

# class NftSupportingDocumentsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SupportingDocuments
#         fields = ['id', 'documents', 'nft_create_info']


class UserDataSerializer(serializers.ModelSerializer):
    user_address = serializers.SerializerMethodField('get_metamask')

    class Meta:
        model = User
        fields = ["id", "profile_picture", "name", "username", "user_address", "created_at", "status", "block"]

    def get_metamask(self, obj):
        try:
            wallet = UserWalletAddress.objects.filter(user_wallet__id=obj.id).first()
            if wallet:
                return wallet.wallet_address
        except:
            return None

class UserWalletAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWalletAddress
        fields = "__all__"

class NFTCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "name", "create_by"]

class NFTViewSerializer(serializers.ModelSerializer):
    # tags = serializers.ListField(child=serializers.CharField(required=True), allow_empty=False)
    # tags = serializers.SerializerMethodField('get_tag')

    class Meta:
        model = NFT
        fields = ["id", "thumbnail", "nft_picture", "teaser", "nft_title", "nft_collection", "nft_status", "user",
                  "description", "nft_category", "royality", "hash", "contract_id", "token_id", 'top_nft', "nft_creator",
                  "nft_owner", "starting_price", "ending_price","start_dateTime","end_datetime",
                  "nft_status", "nft_subject", "created_at", "updated_at", "service_fee",
                   "nft_subject", "status_remarks", "nft_sell_type", "fix_price", "is_minted", "is_listed", ]

    def create(self, validated_data):
        with transaction.atomic():
            nft_docs = dict(self.context['request'].data.lists())['documents']
            nft = NFT.objects.create(**validated_data)
            for doc in nft_docs:
                SupportingDocuments.objects.create(nft_create_info=nft, documents=doc)
            return nft

    # def update(self, instance, validated_data):
    #     # obj = NFT.objects.update(
    #     #     nft_status = validated_data['nft_status']
    #     # )
    #     # obj.update()
    #     with transaction.atomic():
    #         nft_docs = dict(self.context['request'].data.lists())['documents']
    #         prev_doc = SupportingDocuments.objects.filter(nft_create_info__id=instance.id)
    #         prev_doc.delete()
    #         for doc in nft_docs:
    #             SupportingDocuments.objects.create(nft_create_info=instance, documents=doc)
    #         return instance


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tag_title'] = NftTagSerializer(instance.tags_set.filter(nft_create_info__id=instance.id), many=True).data
        from django.db.models import F, Value, CharField
        import os
        data['documents'] = SupportingDocuments.objects.filter(nft_create_info_id=instance.id).values('id',
              'nft_create_info', nft_documents=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("documents"), output_field=CharField() ))
        data['user'] = UserDataSerializer(instance.user).data
        # data['nft_creator'] = UserWalletAddressSerializer(instance.user).data
        # data['nft_owner'] = UserWalletAddressSerializer(instance.user).data
        data['nft_collection'] = NFTCollectionSerializer(instance.nft_collection).data
        data['nft_category'] = NFTCategorySerializer(instance.nft_category).data
        return data


class NFTCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NFTCategory
        fields = ["id", "category_name"]

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

class UserNFTStatusUpdateViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFT
        fields = ["id", "nft_status", "nft_subject", "status_remarks"]


class TransactionNFTSerializer(serializers.ModelSerializer):
    # nft_picture = serializers.SlugRelatedField(read_only=True, slug_field='nft.nft_picture')
    # nft_title = serializers.ReadOnlyField(source='nft.nft_title')
    # nft_picture = serializers.URLField(source='nft.nft_picture')
    # # nft_thumbnail = serializers.ReadOnlyField(source='nft.thumbnail')
    # seller_address = serializers.ReadOnlyField(source='seller.wallet_address')
    # buyer_address = serializers.ReadOnlyField(source='buyer.wallet_address')
    class Meta:
        model = Transaction
        # read_only_fields = ('nft_title','nft_picture', 'seller_address', 'seller_address', 'buyer_address')
        fields = ["id", "nft", "nft_token_id", "seller", "seller_user", "buyer", "buyer_user", "sold_price",
                  "commission_percentage","commission_amount", "category_of_nft","created_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        from django.db.models import F, Value, CharField
        import os
        data['nft'] = NFT.objects.filter(id=instance.nft.id).values('id', 'nft_title')[0]
        data['seller'] = UserWalletAddress.objects.filter(id=instance.seller.id).values('id', 'wallet_address')[0]
        data['seller_user'] = User.objects.filter(id=instance.seller_user.id).values("id", "name", "username",
                                user_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("profile_picture"),
                                                             output_field=CharField()))[0]
        data['buyer'] = UserWalletAddress.objects.filter(id=instance.buyer.id).values('id', 'wallet_address')[0]
        data['buyer_user'] = User.objects.filter(id=instance.buyer_user.id).values("id", "name", "username",
                                user_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("profile_picture"),
                                                             output_field=CharField()))[0]
        return data
              # nft_documents=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("documents"), output_field=CharField() ))


class BidOnNFTDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = BidOnNFT
        fields = ["id","nft_detail", "bidder_wallet", "bidder_profile", "bid_price", "bid_datetime", "created_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['bidder_wallet'] = UserWalletAddress.objects.filter(id=instance.bidder_wallet.id).values('id', "wallet_address")
        data['bidder_profile'] = User.objects.filter(id=instance.bidder_profile.id).values('id',"name", "username")
        return data

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['nft_creator'] = UserDataSerializer(instance.creator).data
    #     data['nft_owner'] = UserDataSerializer(instance.owner).data

class ClaimNFTSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFT
        fields = ["id","nft_status", "nft_creator", "nft_owner", "user", "nft_sell_type", "is_listed", "updated_at"]


class NFTExplorSerializer(serializers.ModelSerializer):
    nft_pic = serializers.SerializerMethodField('get_pic')
    nft_thumbnail = serializers.SerializerMethodField('get_nft_thumbnail')
    nft_teaser = serializers.SerializerMethodField('get_nft_teaser')
    class Meta:
        model = NFT
        fields = ["id", "nft_thumbnail",'nft_pic', "nft_teaser", "user", "nft_title", "nft_category", "fix_price",
                  "starting_price", "nft_collection",
                  "nft_sell_type", "is_minted", "is_listed", "nft_status", "start_dateTime","end_datetime", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        from django.db.models import F, Value, CharField
        import os

        owner = User.objects.filter(id=instance.user.id).values("id", "name", "username",
                                user_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("profile_picture"),
                                                             output_field=CharField()))[0]

        data['nft_category'] = NFTCategorySerializer(instance.nft_category).data

        if instance.nft_sell_type == "Fixed Price":
            data["usd_price"] = get_eth_price(instance.fix_price)
        if instance.nft_sell_type == "Timed Auction":
            data["usd_price"] = get_eth_price(instance.starting_price)

        items = Transaction.objects.filter(nft=instance.id).order_by("-id")[:3]
        owners = []
        owners.append(owner)
        for item in items:
            owner = User.objects.filter(id=item.seller_user.id).values("id",user_pic=Concat(Value(os.getenv(
                'STAGING_PHYNOM_BUCKET_URL')),F("profile_picture"),output_field=CharField()))[0]

            owners.append(owner)
        data['owners'] = owners
        return data

    def get_pic(self, obj):
        try:
            return obj.nft_picture.url
        except Exception as e:
            return None

    def get_nft_thumbnail(self, obj):
        try:
            return obj.thumbnail.url
        except Exception as e:
            return None

    def get_nft_teaser(self, obj):
        try:
            return obj.teaser.url
        except Exception as e:
            return None