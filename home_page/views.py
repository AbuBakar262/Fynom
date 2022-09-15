from django.shortcuts import render
from django.db.models import Q, Count
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F, Value, CharField
import os
from datetime import datetime, timedelta
from decimal import Decimal
from backend.pagination import CustomPageNumberPagination
from blockchain.serializers import *
from blockchain.models import *
from blockchain.utils import validateEmail, scientific_to_float
from home_page.serializers import *
from user.custom_permissions import IsEmailExist, IsApprovedUser
from user.models import User
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import viewsets
from user.serializers import UserCollectionSerializer
from user.utils import Utill
import boto3
from backend.settings import *
import calendar
import datetime


class FeaturedNftView(viewsets.ViewSet):
    """this is used for listing and retrive nfts"""

    def list(self, request, *args, **kwargs):
        """only approved nfts lists"""
        try:
            featured_nft = NFT.objects.filter(featured_nft=True, is_listed=True).first()
            if featured_nft is None:
                count_dic = {}
                visited_nft = VisiteNFT.objects.filter(
                    created_at__gte=datetime.datetime.now() - datetime.timedelta(days=7))
                # unique_no = visited_nft.distinct()
                for visite in visited_nft:
                    nft = visite.visite_nft_id
                    # hear keys is nft id's and values is visitor number against nft
                    if nft not in count_dic.keys():
                        count_dic[nft] = 1
                    else:
                        # a.update({1: a[1] + 1})
                        count_dic.update({nft: count_dic[nft] + 1})
                sorted_list = {k: v for k, v in sorted(count_dic.items(), key=lambda item: item[1], reverse=True)}
                # nft_id = list(count_dic.keys())[0]

                # if featured_nft is None:
                count_dic_list = list(sorted_list.keys())
                for i in count_dic_list:
                    featured_nft = NFT.objects.filter(id=i, is_listed=True).first()
                    if featured_nft:
                        break

            serializer = CountNftVisiorViewSerializer(featured_nft)
            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFTs listed successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class HighestBiddedNftView(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        try:
            nft_list = []
            bid_dic = {}
            bid_list = []
            bids_on_nft = BidOnNFT.objects.filter(updated_at__gte=datetime.datetime.now() - datetime.timedelta(days=7),
                                                  bid_status="Active").order_by('-id')
            query_s = bids_on_nft.first()
            for bid in bids_on_nft:
                nft = bid.nft_detail_id
                # hear keys is nft id's and values is visitor number against nft
                if nft not in nft_list:
                    nft_list.append(nft)
                    # bid_list.append(bid)
                    bid_dic[bid.id] = bid.bid_price
            sorted_list = {k: v for k, v in sorted(bid_dic.items(), key=lambda item: item[1], reverse=True)}
            count_dic_list = list(sorted_list.keys())

            for i in count_dic_list:
                height_bid_nft = BidOnNFT.objects.filter(id=i, bid_status="Active").first()
                if height_bid_nft:
                    bid_list.append(height_bid_nft)

            serializer = HighestBiddedNftViewSerializer(bid_list[:4], many=True)
            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFTs listed successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class TopNftView(viewsets.ViewSet):
    """by visitor"""
    def list(self, request, *args, **kwargs):

        try:
            count_dic = {}
            featured_nft = []
            visited_nft = VisiteNFT.objects.filter(created_at__gte=datetime.datetime.now() - datetime.timedelta(days=7))
            # unique_no = visited_nft.distinct()
            for visite in visited_nft:
                nft = visite.visite_nft_id
                # hear keys is nft id's and values is visitor number against nft
                if nft not in count_dic.keys():
                    count_dic[nft] = 1
                else:
                    # a.update({1: a[1] + 1})
                    count_dic.update({nft: count_dic[nft] + 1})
            sorted_list = {k: v for k, v in sorted(count_dic.items(), key=lambda item: item[1], reverse=True)}
            # nft_id = list(count_dic.keys())[0]

            # if featured_nft is None:
            count_dic_list = list(sorted_list.keys())
            for i in count_dic_list:
                featured_nft_one = NFT.objects.filter(id=i, is_listed=True).first()
                if featured_nft_one:
                    featured_nft.append(featured_nft_one)
                if len(featured_nft) >= 8:
                    break

            serializer = CountNftVisiorViewSerializer(featured_nft[:4], many=True)
            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFTs listed successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class CollectionFeaturedNftView(viewsets.ViewSet):
    """this is used for listing and retrive nfts"""

    def list(self, request, *args, **kwargs):
        """only approved nfts lists"""
        try:
            colletions = []
            count_dic = {}
            visited_nft = VisiteNFT.objects.filter(
                created_at__gte=datetime.datetime.now() - datetime.timedelta(days=7))
            # unique_no = visited_nft.distinct()
            for visite in visited_nft:
                nft = visite.visite_nft_id
                # hear keys is nft id's and values is visitor number against nft
                nft_collection_id = NFT.objects.get(id=nft).nft_collection_id
                if nft_collection_id not in count_dic.keys():
                    count_dic[nft_collection_id] = 1
                else:
                    # a.update({1: a[1] + 1})
                    count_dic.update({nft_collection_id: count_dic[nft_collection_id] + 1})
            sorted_list = {k: v for k, v in sorted(count_dic.items(), key=lambda item: item[1], reverse=True)}
            # nft_id = list(count_dic.keys())[0]

            # if featured_nft is None:

            count_dic_list = list(sorted_list.keys())
            for i in count_dic_list[:3]:
                colletion = Collection.objects.filter(id=i).first()
                if colletion:
                    colletions.append(colletion)
            serializer = CollectionFeaturedNftViewSerializer(colletions, many=True)
            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFTs listed successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class TrendingNftsView(viewsets.ViewSet):
    """this is used for listing and retrive nfts"""

    def list(self, request, *args, **kwargs):
        """only approved nfts lists"""
        try:
            count_dic = {}
            trending_nft =[]
            visited_nft = VisiteNFT.objects.filter(
                created_at__gte=datetime.datetime.now() - datetime.timedelta(days=7))
            # unique_no = visited_nft.distinct()
            for visite in visited_nft:
                nft = visite.visite_nft_id
                # hear keys is nft id's and values is visitor number against nft
                if nft not in count_dic.keys():
                    count_dic[nft] = 1
                else:
                    # a.update({1: a[1] + 1})
                    count_dic.update({nft: count_dic[nft] + 1})
            sorted_list = {k: v for k, v in sorted(count_dic.items(), key=lambda item: item[1], reverse=True)}
            # nft_id = list(count_dic.keys())[0]

            # if featured_nft is None:
            count_dic_list = list(sorted_list.keys())
            for i in count_dic_list:
                featured_nft = NFT.objects.filter(id=i, is_listed=True).first()
                if featured_nft:
                    trending_nft.append(featured_nft)
            updated_listed_nft = NFT.objects.filter(is_listed=True).order_by('-updated_at')
            for nft in updated_listed_nft:
                trending_nft.append(nft)

            paginator = CustomPageNumberPagination()
            result = paginator.paginate_queryset(trending_nft, request)
            serializer = NFTExplorSerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

class FeatureNFTView(viewsets.ViewSet):
    queryset = NFT.objects.all()
    serializer_class = FeatureNFTSerializer
    permission_classes = [AllowAny]

    # admin can make any nft featured or unfeatured
    def featureNFT(self, request, *args, **kwargs):
        try:
            serializers = self.serializer_class(data=request.data)
            if not serializers.is_valid():
                return Response({
                    "status": False, "status_code": 400, 'msg': serializers.errors,
                    "data": []}, status=status.HTTP_400_BAD_REQUEST)
            nft_id = serializers.validated_data['nft_id']
            is_featured = serializers.validated_data['is_featured']
            nft = NFT.objects.filter(id=nft_id).first()
            if is_featured == True:
                nft.featured_nft = True
                nft.save()
                return Response({
                    "status": True, "status_code": 200, 'msg': 'NFT featured successfully',
                    "data": []}, status=status.HTTP_200_OK)
            if is_featured == False:
                nft.featured_nft = False
                nft.save()
                return Response({
                    "status": True, "status_code": 200, 'msg': 'NFT unfeatured successfully',
                    "data": []}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)
