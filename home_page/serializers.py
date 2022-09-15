import os
import datetime
import calendar
from django.db.models import F
from rest_framework import serializers
from django.db.models.functions import Concat
from blockchain.serializers import UserDataSerializer
from blockchain.utils import scientific_to_float
from user.models import User
from blockchain.models import Collection, UserWalletAddress, NFT, BidOnNFT


# class AdminLoginSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['email', 'password']
class CountNftVisiorViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = NFT
        fields = ["id", "thumbnail", "nft_picture", "teaser", "nft_title", "nft_status", "user",
                  "contract_id", "token_id", 'top_nft', "nft_creator",
                  "nft_owner", "starting_price", "ending_price","start_dateTime","end_datetime",
                  "nft_status", "nft_subject", "created_at", "updated_at", "service_fee", "e_mail",
                   "nft_subject", "status_remarks", "nft_sell_type", "fix_price", "is_minted", "is_listed"]

    def to_representation(self, instance):
        highest_bid = ''
        data = super().to_representation(instance)
        data['user'] = UserDataSerializer(instance.user).data
        data['highest_bidded'] = BidOnNFT.objects.filter(nft_detail=instance).get().bid_price
        if instance.nft_sell_type == "Fixed Price" and "e" in str(instance.fix_price):
            data['fix_price'] = scientific_to_float(float(instance.fix_price))
        if instance.nft_sell_type == "Timed Auction":
            data['starting_price'] = BidOnNFT.objects.filter(bid_status="Active").order_by('-id').values('bid_price')[0]
            if "e" in str(data['starting_price']):
                data['starting_price'] = scientific_to_float(float(instance.starting_price))
        return data


class HighestBiddedNftViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = BidOnNFT
        fields = ["nft_detail", "bid_price", "created_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        from django.db.models import F, Value, CharField
        data["nft_detail"] = NFT.objects.filter(id=instance.nft_detail.id).values('id',
                                    nft_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),
                                             F("nft_picture"), output_field=CharField()))[0]
        data['title'] = NFT.objects.filter(id=instance.nft_detail.id).first().nft_title
        data['percentage'] = NFT.objects.filter(id=instance.nft_detail.id).first().royality
        return data


class CollectionFeaturedNftViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "name", "logo_image", "featured_image", "cover_image"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserDataSerializer(instance.create_by).data
        data['nfts'] = NFT.objects.filter(nft_collection=instance, is_listed=True).values('id','thumbnail','nft_picture', 'nft_title')
        return data

