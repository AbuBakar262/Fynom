from django.db import transaction
from django.db.models.functions import Concat
from rest_framework import serializers
import calendar
import datetime
from blockchain.models import *
from blockchain.utils import get_eth_price, scientific_to_float
from user.models import User
from django.utils.translation import gettext_lazy as _
from user.serializers import UserProfileDetailsViewSerializer


class NftTagSerializer(serializers.ModelSerializer):
    tag_title = serializers.CharField(required=True)
    class Meta:
        model = Tags
        fields = ["id", "tag_title", "created_at", "updated_at"]


class NFTCommissionViewSerializer(serializers.ModelSerializer):
    set_commission = serializers.CharField(required=True)
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
    thumbnail = serializers.ImageField(required=True)
    nft_picture = serializers.FileField(required=True)
    nft_title = serializers.CharField(required=True)
    # nft_collection = serializers.IntegerField(required=True)
    description = serializers.CharField(required=True)
    # nft_category = serializers.IntegerField(required=True)
    royality = serializers.FloatField(required=True)
    nft_sell_type = serializers.CharField(required=True)
    service_fee = serializers.CharField(required=True)


    class Meta:
        model = NFT
        fields = ["id", "thumbnail", "nft_picture", "teaser", "nft_title", "nft_collection", "nft_status", "user",
                  "description", "nft_category", "royality", "hash", "contract_id", "token_id", 'top_nft', "nft_creator",
                  "nft_owner", "starting_price", "ending_price","start_dateTime","end_datetime",
                  "nft_status", "nft_subject", "created_at", "updated_at", "service_fee", "e_mail",
                   "nft_subject", "status_remarks", "nft_sell_type", "fix_price", "is_minted", "is_listed", ]

    def validate(self, attrs):
        royalty = attrs.get('royality')
        nft_collection = attrs.get('nft_collection')
        nft_category = attrs.get('nft_category')
        if type(royalty%1) is float and royalty%1 != 0:
            raise serializers.ValidationError("Please enter an integer number.")
        if not nft_collection:
            raise serializers.ValidationError("please select nft collection.")
        if not nft_category:
            raise serializers.ValidationError("please select nft category.")
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            nft = NFT.objects.create(**validated_data)
            data = self.context['request'].data
            if 'documents' in data:
                nft_docs = dict(self.context['request'].data.lists())['documents']
                for doc in nft_docs:
                    SupportingDocuments.objects.create(nft_create_info=nft, documents=doc)
            return nft

    # def update(self, instance, validated_data): #user = self.context.get('user')
    #     status = validated_data['nft_status']
    #     listed = validated_data['is_listed']
    #     # minted = validated_data['is_minted']
    #     # valid_user =
    #     if status=="Approved" and listed==True:
    #         validated_data['e_mail'] = True
    #     instance.save()
    #     # obj = NFT.objects.update(nft_status = validated_data['nft_status'])
    #     # obj.update()
    #     return instance
        # with transaction.atomic():
        #     nft_docs = dict(self.context['request'].data.lists())['documents']
        #     prev_doc = SupportingDocuments.objects.filter(nft_create_info__id=instance.id)
        #     prev_doc.delete()
        #     for doc in nft_docs:
        #         SupportingDocuments.objects.create(nft_create_info=instance, documents=doc)
        #     return instance


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tag_title'] = NftTagSerializer(instance.tags_set.filter(nft_create_info__id=instance.id), many=True).data
        from django.db.models import F, Value, CharField
        import os
        data['documents'] = SupportingDocuments.objects.filter(nft_create_info_id=instance.id).values('id',
              'nft_create_info', nft_documents=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("documents"), output_field=CharField() ))
        data['user'] = UserDataSerializer(instance.user).data

        if instance.nft_sell_type == "Fixed Price" and "e" in str(instance.fix_price):
            data['fix_price'] = scientific_to_float(float(instance.fix_price))
        if instance.nft_sell_type == "Timed Auction" and "e" in str(instance.starting_price):
            data['starting_price'] = scientific_to_float(float(instance.starting_price))
        # data['nft_creator'] = UserWalletAddressSerializer(instance.user).data
        # data['nft_owner'] = UserWalletAddressSerializer(instance.user).data
        data['nft_collection'] = NFTCollectionSerializer(instance.nft_collection).data
        data['nft_category'] = NFTCategorySerializer(instance.nft_category).data
        return data


class NFTCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(required=True)
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

class UserNFTStatusUpdateViewSerializer(serializers.ModelSerializer):
    nft_status = serializers.CharField(required=True)
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
    # commission_amount = serializers.CharField(required=True)
    class Meta:
        model = Transaction
        # read_only_fields = ('nft_title','nft_picture', 'seller_address', 'seller_address', 'buyer_address')
        fields = ["id", "nft", "nft_token_id", "seller", "seller_user", "buyer", "buyer_user", "sold_price",
                  "commission_percentage","commission_amount", "category_of_nft","created_at", "royality_percentage",
                  "royality_amount", "seller_asset"]

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
        if instance.commission_amount:
            data['commission_amount'] = scientific_to_float(float(instance.commission_amount))
        return data
              # nft_documents=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("documents"), output_field=CharField() ))


class BidOnNFTDetailsSerializer(serializers.ModelSerializer):
    # nft_detail = serializers.IntegerField(required=True)
    # bid_price = serializers.FloatField(required=True)

    class Meta:
        model = BidOnNFT
        fields = ["id","nft_detail", "seller_wallet", "seller_profile", "bidder_wallet", "bidder_profile", "bid_price",
                  "bid_datetime", "created_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['bidder_wallet'] = UserWalletAddress.objects.filter(id=instance.bidder_wallet.id).values('id', "wallet_address")
        data['bidder_profile'] = User.objects.filter(id=instance.bidder_profile.id).values('id',"name", "username", "email")
        return data

#   context={'user': request.user}         password2 = attrs.get('password2')          user = self.context.get('user')
    def validate(self, attrs):
        nft_owner = attrs.get('seller_profile')
        bidder = attrs.get('bidder_profile')
        nft = NFT.objects.filter(id= attrs.get('nft_detail').id).first()
        if nft.nft_status == 'Approved' and nft.is_listed==True:
            # convert utc into unix
            date = datetime.datetime.utcnow()
            utc_time = calendar.timegm(date.utctimetuple())

            if int(nft.end_datetime) <= utc_time:
                raise serializers.ValidationError("NFT bid time expire")

            if int(nft.start_dateTime) > utc_time:
                raise serializers.ValidationError("Please wait for starting bid on this NFT.")

            if nft_owner == bidder:
                raise serializers.ValidationError("User can't bid on his/her NFT.")

            bid = BidOnNFT.objects.filter(nft_detail=attrs.get('nft_detail').id, seller_profile=nft_owner,
                                          bid_status="Active").order_by('-id').first()
            if bid:
                if float(attrs.get('bid_price')) <= bid.bid_price:
                    raise serializers.ValidationError("Current bid price should be higher then last bid price")

            if nft.starting_price > float(attrs.get('bid_price')):
                raise serializers.ValidationError("Bid price should be greater then or equal to starting price.")
        else:
            raise serializers.ValidationError("You can't bid now.")

        return attrs


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



class ClaimNFTViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = NFT
        fields = ["id", "thumbnail", "nft_picture", "teaser", "nft_title", "nft_collection", "nft_status", "user",
                  "description", "nft_category", "royality", "hash", "contract_id", "token_id", 'top_nft', "nft_creator",
                  "nft_owner", "starting_price", "ending_price","start_dateTime","end_datetime",
                  "nft_status", "nft_subject", "created_at", "updated_at", "service_fee", "e_mail",
                   "nft_subject", "status_remarks", "nft_sell_type", "fix_price", "is_minted", "is_listed"]

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


class ContactUsSerializer(serializers.Serializer):
    contact_status = serializers.CharField(required=True)
    user_name = serializers.CharField(required=True)
    email_address = serializers.EmailField(required=True)
    email_body = serializers.CharField(required=True)
    wallet_address = serializers.CharField(required=False)
    contract_nft = serializers.CharField(required=False)

    def validate(self, attrs):
        if attrs.get('contact_status') == "dispute":
            if not attrs.get('wallet_address'):
                raise serializers.ValidationError(
                    {'message': _('Wallet address is required for dispute.')})
            if not attrs.get('contract_nft'):
                raise serializers.ValidationError(
                    {'message': _('Contract nft is required for dispute.')})
        return attrs


class FeatureNFTSerializer(serializers.ModelSerializer):
    nft_id = serializers.IntegerField(required=True)
    is_featured = serializers.BooleanField(required=True)

    class Meta:
        model = NFT
        fields = ["nft_id", "is_featured"]

    # if any other nft is featured then raise error and return existing featured nft id
    def validate(self, attrs):
        if attrs['is_featured'] == True:
            nft = NFT.objects.filter(id=attrs['nft_id'])
            nft.update(featured_nft=attrs['is_featured'])
            already_featured_nft = NFT.objects.filter(featured_nft=True)
            already_featured_nft.update(featured_nft=False)
        return attrs