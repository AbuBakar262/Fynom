from django.db.models import Q, Count
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F, Value, CharField
from datetime import datetime
from decimal import Decimal
from backend.pagination import CustomPageNumberPagination
from blockchain.serializers import *
from blockchain.models import *
from blockchain.utils import validateEmail, scientific_to_float
from blockchain.serializers import FeatureNFTSerializer
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


class ListRetrieveNFTView(viewsets.ViewSet):
    """this is used for listing and retrive nfts"""
    def list(self, request, *args, **kwargs):
        """only approved nfts lists"""
        try:
            list_nft = NFT.objects.filter(nft_status="Approved").order_by('-id')
            serializer = NFTViewSerializer(list_nft, many=True)
            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFTs listed successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """nft will retrieve by providing nft id this is nft details view page show"""
        try:
            nft_id = self.kwargs.get('pk')
            nft_by_id = NFT.objects.filter(id=nft_id).first()

            creator_wallet = UserWalletAddress.objects.filter(user_wallet=nft_by_id.nft_creator.user_wallet.id).first()
            creator_user = User.objects.filter(id=creator_wallet.user_wallet.id).values("id", "username", "name", "discord_link",
                 user_picture = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("profile_picture"), output_field=CharField()))

            owner_wallet = UserWalletAddress.objects.filter(user_wallet=nft_by_id.nft_owner.user_wallet.id).first()
            owner_user = User.objects.filter(id=owner_wallet.user_wallet.id).values("id", "username", "name","discord_link",
                    user_picture=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("profile_picture"),output_field=CharField()))

            serializer = NFTViewSerializer(nft_by_id)

            visitor = VisiteNFT.objects.create(visite_nft=nft_by_id)
            visitor.save()

            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFTs retrieve successfully',
                "data": serializer.data, "creator_user":creator_user, "owner_user":owner_user}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class CreateUpdateNFTView(viewsets.ViewSet):

    permission_classes = [IsAuthenticated, IsApprovedUser]

    def create(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            wallet_id = UserWalletAddress.objects.filter(user_wallet=user_id).first()
            request.data._mutable = True
            request.data['nft_creator'] = wallet_id.id
            request.data['user'] = request.user.id
            request.data['nft_owner'] = wallet_id.id
            request.data['tags_title'] = request.data.get('tag_title').split(',')
            # request.data["starting_price"] = float(Decimal(str(request.data["starting_price"])))
            # request.data['tags'] = request.data.get('tags').split(',')
            nft_commission = Commission.objects.first()
            request.data["service_fee"] = nft_commission.set_commission   # hardcode set_commission
            # nft_teaser = request.data.get('teaser')
            # if nft_teaser == "null":
            #     nft_teaser = request.data.pop('teaser')
            serializer = NFTViewSerializer(data=request.data, context={'request':request})
            serializer.is_valid(raise_exception=True)
            nft = serializer.save()
            nft.tags_set.add(*request.data['tags_title'])
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT submitted successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400,
                'msg':[e.args[0]['non_field_errors'][0] if 'non_field_errors' in e.args[0] else e.args[0]][0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, *args, **kwargs):
        """
        this is used for update nft by id, docoments and tags will delete and auto insert
        """
        global body, listed
        try:
            nft_id = self.kwargs.get('pk')
            user_wallet =  UserWalletAddress.objects.filter(user_wallet=request.user.id).first()
            nft_by_id = NFT.objects.filter(id=nft_id, nft_owner__id=user_wallet.id).first()
            # nft_status = "Pending"
            nft_status = request.data['nft_status']
            if request.data['nft_status'] == 'Pending':
                pass
            else:
                listed = request.data['is_listed']
            type_a = request.data['nft_sell_type']
            request.data._mutable = True
            if nft_status == "Approved" and type_a=="Timed Auction" and listed.lower()=='true':
                request.data['e_mail'] = True
            # request.data._mutable = True
            # request.data['nft_status'] = nft_status

            # if nft_by_id.nft_owner != nft_by_id.nft_creator:
            #     nft_commission = Commission.objects.first()
            #     request.data["service_fee"] = nft_commission.set_commission  # hardcode set_commission

            if nft_by_id:
                serializer = NFTViewSerializer(nft_by_id, data=request.data, context={'request':request, 'user': request.user}, partial=True)
                # request.data._mutable = True
                if serializer.is_valid(raise_exception=True):
                    nft = serializer.save()
                    if request.data.get('tag_title'):
                        tags_id = [i.id for i in NFT.objects.get(id=nft_id).tags_set.all()]
                        for i in tags_id:
                               nft.tags_set.remove(i) # remove nft tags form tags table
                        tags_title = request.data.get('tag_title').split(',')
                        nft.tags_set.add(*tags_title)
                    if request.user.email:
                        if nft_status == 'Pending':
                            body = f"Your NFT '{nft_by_id.nft_title}' is Pending now due to some updates. To visit your " \
                                   f"NFT click on link given below " + os.getenv('FRONTEND_SITE_URL') + str(nft_id)

                            data = {
                                'subject': 'Your Phynom NFT Status',
                                'body': body,
                                'to_email': request.user.email
                            }
                            Utill.send_email(data)
                            return Response({
                                "status": True, "status_code": 200, 'msg': 'Requested for approval',
                                "data": serializer.data}, status=status.HTTP_200_OK)
                    # tags = Tags.objects.create()
                    # nft.tags_set.add(*request.data['tags_title'])
                    return Response({
                        "status": True, "status_code": 200, 'msg': 'User NFTs updated successfully',
                        "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({
            "status": False, "status_code": 400, 'msg': 'User not owner of this NFT',
            "data": []}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserNFTsListView(viewsets.ViewSet):
    """
    this view is for list/retrieve nfts of perticular user by its id
    """

    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        list_nft = ''
        try:

            user_id = request.query_params.get('user_id')
            user_nft = request.query_params.get('search')
            nft_category_id = request.query_params.get('category')
            if user_id and user_nft == 'mynft' or user_nft == 'listmynft' and nft_category_id and user_nft != 'admin':
                user_wallet = UserWalletAddress.objects.filter(user_wallet=user_id).first()
                if user_nft == "mynft":
                    if nft_category_id != 'all':
                        list_nft = NFT.objects.filter(Q(is_minted=True) | Q(is_minted=False), nft_owner=user_wallet.id,
                                       is_listed=False, nft_category=nft_category_id).values('id','nft_title',
                                           'fix_price','nft_sell_type','starting_price','ending_price','start_dateTime',
                                           'end_datetime','is_minted','is_listed','nft_status','nft_subject',
                                           'status_remarks',nft_user_id=F('user__id'),
                                           user_nft_collection=F('nft_collection__name'),
                                           user_nft_category=F('nft_category__category_name'),
                            nft_thumbnail = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("thumbnail"), output_field=CharField()),
                            nft_teaser = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("teaser"), output_field=CharField()),
                            nft_pic = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("nft_picture"), output_field=CharField()),
                            user_profile_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),
                                                F("user__profile_picture"),output_field=CharField())).order_by('-id')
                    else:
                        list_nft = NFT.objects.filter(Q(is_minted=True) | Q(is_minted=False), nft_owner=user_wallet.id,
                                        is_listed=False).values('id','nft_title','fix_price','nft_sell_type',
                                             'starting_price','ending_price','start_dateTime','end_datetime',
                                             'is_minted','is_listed','nft_status','nft_subject','status_remarks',
                                             nft_user_id=F('user__id'),user_nft_collection=F('nft_collection__name'),
                                             user_nft_category=F('nft_category__category_name'),
                                nft_thumbnail=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("thumbnail"),output_field=CharField()),
                                nft_teaser=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("teaser"),output_field=CharField()),
                                nft_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("nft_picture"),output_field=CharField()),
                                user_profile_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),
                                                    F("user__profile_picture"),output_field=CharField())).order_by('-id')

                if user_nft == "listmynft":
                    if nft_category_id != 'all':
                        list_nft = NFT.objects.filter(is_minted=True, nft_owner=user_wallet.id,
                                        is_listed=True, nft_category=nft_category_id).values('id','nft_title',
                                             'fix_price','nft_sell_type','starting_price','ending_price','start_dateTime',
                                             'end_datetime','is_minted','is_listed','nft_status','nft_subject',
                                             'status_remarks',nft_user_id=F('user__id'),
                                             user_nft_collection=F('nft_collection__name'),
                                             ser_nft_category=F('nft_category__category_name'),
                                nft_thumbnail = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("thumbnail"),output_field=CharField()),
                                ft_teaser=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("teaser"),output_field=CharField()),
                                nft_pic = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("nft_picture"),output_field=CharField()),
                                user_profile_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),
                                                    F("user__profile_picture"),output_field=CharField())).order_by('-id')
                    else:
                        list_nft = NFT.objects.filter(is_minted=True, nft_owner=user_wallet.id,
                                        is_listed=True).values('id','nft_title','fix_price','nft_sell_type','starting_price',
                                              'ending_price','start_dateTime','end_datetime','is_minted','is_listed',
                                              'nft_status','nft_subject','status_remarks',nft_user_id=F('user__id'),
                                              user_nft_collection=F('nft_collection__name'),
                                              user_nft_category=F('nft_category__category_name'),
                                nft_thumbnail=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("thumbnail"),output_field=CharField()),
                                nft_teaser=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("teaser"),output_field=CharField()),
                                nft_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("nft_picture"),output_field=CharField()),
                                user_profile_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),
                                                        F("user__profile_picture"),output_field=CharField())).order_by('-id')

                # price = list_nft.values_list
                for nft in list_nft:
                    if nft.get('nft_sell_type')=="Fixed Price":
                        usd_price = get_eth_price(nft.get('fix_price'))
                        nft["usd_price"] = usd_price
                        nft["fix_price"] = scientific_to_float(nft.get('fix_price'))

                    else:
                        bid = BidOnNFT.objects.filter(nft_detail=nft.get('id'), bid_status="Active",
                                                      seller_profile=nft.get('nft_user_id')).order_by('-id').first()
                        if bid:
                            usd_price = get_eth_price(bid.bid_price)
                            # bid.bid_price = scientific_to_float(bid.bid_price)
                        else:
                            usd_price = get_eth_price(nft.get('starting_price'))
                        nft["starting_price"] = scientific_to_float(nft.get('starting_price'))
                        nft["usd_price"] = usd_price


                paginator = CustomPageNumberPagination()
                result = paginator.paginate_queryset(list_nft, request)
                return paginator.get_paginated_response(result)
            elif user_nft == "admin":
                list_nft = NFT.objects.filter(nft_status='Pending')\
                    .annotate(document_count=Count('nft_in_supportingdocument')).values('id','nft_title','nft_status',
                                   'document_count',nft_user_id=F('user__id'),real_name=F('user__name'),
                                   display_name=F('user__username'),wallet_address=F('nft_owner__wallet_address'),
                                   user_nft_category=F('nft_category__category_name'),
                                    nft_thumbnail = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),
                                                           F("thumbnail"), output_field=CharField())).order_by('-id')
                paginator = CustomPageNumberPagination()
                result = paginator.paginate_queryset(list_nft, request)
                return paginator.get_paginated_response(result)

            else:
                return Response({
                    "status": False, "status_code": 400, 'msg': 'user_id, search and category params is required',
                    "data": []}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class ManageNFTsListView(viewsets.ViewSet):
    """
    this view is for list/retrieve nfts of perticular user by its id
    """

    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        list_nft = ''
        try:

            user_id = request.query_params.get('user_id')
            user_nft = request.query_params.get('search')
            nft_category_id = request.query_params.get('category')
            if user_id and user_nft == 'mynft' or user_nft == 'listmynft' and nft_category_id and user_nft != 'admin':
                user_wallet = UserWalletAddress.objects.filter(user_wallet=user_id).first()
                if user_nft == "mynft":
                    if nft_category_id != 'all':
                        list_nft = NFT.objects.filter(Q(is_minted=True) | Q(is_minted=False), nft_owner=user_wallet.id,
                                       is_listed=True, nft_category=nft_category_id).values('id','nft_title',
                                           'fix_price','nft_sell_type','starting_price','ending_price','start_dateTime',
                                           'end_datetime','is_minted','is_listed','nft_status','nft_subject',
                                           'status_remarks', 'featured_nft',nft_user_id=F('user__id'),
                                           user_nft_collection=F('nft_collection__name'),
                                           user_nft_category=F('nft_category__category_name'),
                            nft_thumbnail = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("thumbnail"), output_field=CharField()),
                            nft_teaser = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("teaser"), output_field=CharField()),
                            nft_pic = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("nft_picture"), output_field=CharField()),
                            user_profile_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),
                                                F("user__profile_picture"),output_field=CharField())).order_by('-featured_nft')
                    else:
                        list_nft = NFT.objects.filter(Q(is_minted=True) | Q(is_minted=False), nft_owner=user_wallet.id,
                                        is_listed=True).values('id','nft_title','fix_price','nft_sell_type',
                                             'starting_price','ending_price','start_dateTime','end_datetime',
                                             'is_minted','is_listed','nft_status','nft_subject','status_remarks', 'featured_nft',
                                             nft_user_id=F('user__id'),user_nft_collection=F('nft_collection__name'),
                                             user_nft_category=F('nft_category__category_name'),
                                nft_thumbnail=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("thumbnail"),output_field=CharField()),
                                nft_teaser=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("teaser"),output_field=CharField()),
                                nft_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("nft_picture"),output_field=CharField()),
                                user_profile_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),
                                                    F("user__profile_picture"),output_field=CharField())).order_by('-featured_nft')

                if user_nft == "listmynft":
                    if nft_category_id != 'all':
                        list_nft = NFT.objects.filter(is_minted=True, nft_owner=user_wallet.id,
                                        is_listed=True, nft_category=nft_category_id).values('id','nft_title',
                                             'fix_price','nft_sell_type','starting_price','ending_price','start_dateTime',
                                             'end_datetime','is_minted','is_listed','nft_status','nft_subject', 'featured_nft',
                                             'status_remarks',nft_user_id=F('user__id'),
                                             user_nft_collection=F('nft_collection__name'),
                                             ser_nft_category=F('nft_category__category_name'),
                                nft_thumbnail = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("thumbnail"),output_field=CharField()),
                                ft_teaser=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("teaser"),output_field=CharField()),
                                nft_pic = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("nft_picture"),output_field=CharField()),
                                user_profile_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),
                                                    F("user__profile_picture"),output_field=CharField())).order_by('-featured_nft')
                    else:
                        list_nft = NFT.objects.filter(is_minted=True, nft_owner=user_wallet.id,
                                        is_listed=True).values('id','nft_title','fix_price','nft_sell_type','starting_price',
                                              'ending_price','start_dateTime','end_datetime','is_minted','is_listed', 'featured_nft',
                                              'nft_status','nft_subject','status_remarks',nft_user_id=F('user__id'),
                                              user_nft_collection=F('nft_collection__name'),
                                              user_nft_category=F('nft_category__category_name'),
                                nft_thumbnail=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("thumbnail"),output_field=CharField()),
                                nft_teaser=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("teaser"),output_field=CharField()),
                                nft_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),F("nft_picture"),output_field=CharField()),
                                user_profile_pic=Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),
                                                        F("user__profile_picture"),output_field=CharField())).order_by('-featured_nft')

                # price = list_nft.values_list
                for nft in list_nft:
                    if nft.get('nft_sell_type')=="Fixed Price":
                        usd_price = get_eth_price(nft.get('fix_price'))
                        nft["usd_price"] = usd_price
                        nft["fix_price"] = scientific_to_float(nft.get('fix_price'))

                    else:
                        bid = BidOnNFT.objects.filter(nft_detail=nft.get('id'), bid_status="Active",
                                                      seller_profile=nft.get('nft_user_id')).order_by('-id').first()
                        if bid:
                            usd_price = get_eth_price(bid.bid_price)
                            # bid.bid_price = scientific_to_float(bid.bid_price)
                        else:
                            usd_price = get_eth_price(nft.get('starting_price'))
                        nft["starting_price"] = scientific_to_float(nft.get('starting_price'))
                        nft["usd_price"] = usd_price


                paginator = CustomPageNumberPagination()
                result = paginator.paginate_queryset(list_nft, request)
                return paginator.get_paginated_response(result)
            elif user_nft == "admin":
                list_nft = NFT.objects.filter(is_listed=True, nft_status='Approved')\
                    .annotate(document_count=Count('nft_in_supportingdocument')).values('id','nft_title','nft_status', 'featured_nft', 'is_listed',
                                   'document_count',nft_user_id=F('user__id'),real_name=F('user__name'),
                                   display_name=F('user__username'),wallet_address=F('nft_owner__wallet_address'),
                                   user_nft_category=F('nft_category__category_name'),
                                    nft_thumbnail = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),
                                                           F("thumbnail"), output_field=CharField()),
                                    user_profile_pic = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')),
                                    F("user__profile_picture"),output_field=CharField())).order_by('-featured_nft')
                paginator = CustomPageNumberPagination()
                result = paginator.paginate_queryset(list_nft, request)
                return paginator.get_paginated_response(result)

            else:
                return Response({
                    "status": False, "status_code": 400, 'msg': 'user_id, search and category params is required',
                    "data": []}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class NFTCategoryView(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            nft_category = NFTCategory.objects.all().order_by('-id')
            # nft_tags = Tags.objects.all()
            paginator = CustomPageNumberPagination()
            result = paginator.paginate_queryset(nft_category, request)
            serializer = NFTCategorySerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:

            # nft_category = NFTCategory.objects.all()
            category = request.data['category_name']
            all_category = NFTCategory.objects.all()
            for one in all_category:
                if category.lower() == one.category_name.lower():
                    return Response({
                        "status": True, "status_code": 200, 'msg': 'NFT category is already exist',
                        "data": []}, status=status.HTTP_200_OK)
            serializer = NFTCategorySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT category created successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            category = NFTCategory.objects.get(id=id)
            serializer = NFTCategorySerializer(category, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT category updated successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            category_id = self.kwargs.get('pk')
            category_by_id = NFTCategory.objects.get(id=category_id)
            category_by_id.delete()
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT category is deleted successfully',
                "data": {}}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self, *args, **kwargs):
        if self.request.method in ['GET']:
            return []
        else:
            return [IsAuthenticated()]


class NFTTagView(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            nft_tags = Tags.objects.all().order_by('-id')
            paginator = CustomPageNumberPagination()
            result = paginator.paginate_queryset(nft_tags, request)
            serializer = NftTagSerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)
    def create(self, request, *args, **kwargs):
        try:
            tag = request.data['tag_title']
            all_tag = Tags.objects.all()
            for one in all_tag:
                if tag.lower() == one.tag_title.lower():
                    return Response({
                        "status": True, "status_code": 200, 'msg': 'NFT tag is already exist',
                        "data": []}, status=status.HTTP_200_OK)
            serializer = NftTagSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT tag is created successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)
    def update(self, request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get('pk')
            tag_by_id = Tags.objects.get(id=tag_id)
            serializer = NftTagSerializer(tag_by_id, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT tag is updated successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400,'error':'Sorry Your data did not updated', 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get('pk')
            tag_by_id = Tags.objects.get(id=tag_id)
            tag_by_id.delete()
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT tag is deleted successfully',
                "data": {}}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self, *args, **kwargs):
        if self.request.method in ['GET']:
            return []
        else:
            return [IsAuthenticated()]


class UserNFTStatusUpdateView(viewsets.ViewSet):
    """
     This api is only use for Admin
     can change the status of user NFT
     """
    permission_classes = [IsAdminUser]
    def partial_update(self, request, *args, **kwargs):
        global nft_subject, status_reasons
        try:
            id = self.kwargs.get('pk')
            nft_instance = NFT.objects.get(id=id)
            # nft_instance = NFT.objects.filter(id = nft.id).first()
            user = User.objects.filter(id = nft_instance.user.id).first()
            profile_status = request.data['nft_status']
            nft_subject = request.data['nft_subject']
            status_reasons = request.data['status_remarks']

            serializer = UserNFTStatusUpdateViewSerializer(nft_instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if user.email:
            # send email
                body = None
                if profile_status == 'Approved':
                    body = f"Congratulations! your NFT '{nft_instance.nft_title}' has been Approved.\n" + nft_subject + \
                           "\n" + status_reasons + "\nPlease visit the website and launch the minting of your NFT ready " \
                                                   "for sale by click on the given link " + os.getenv(
                        'FRONTEND_SITE_URL') + str(id)

                    data = {
                        'subject': 'Your Phynom NFT Status',
                        'body': body,
                        'to_email': user.email
                    }
                    Utill.send_email(data)
                if profile_status == 'Disapproved':
                    body = f"We are Sorry! your NFT '{nft_instance.nft_title}' has been Disapproved. " + nft_subject + \
                           "\n" + status_reasons + "\nPlease visit the website and update your NFT by click on the " \
                                                   "given link " + os.getenv('FRONTEND_SITE_URL') + str(id)

                    data = {
                        'subject': 'Your Phynom NFT Status',
                        'body': body,
                        'to_email': user.email
                    }
                    Utill.send_email(data)
                # if profile_status == 'Pending':
                #     body = "Your NFT is Pending now due to some updates. "

            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFT status update successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class ListTransactionNFTView(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        try:
            nft_transaction = Transaction.objects.all().order_by("-id")
            filter_by = self.request.query_params.get('filter_by')
            if filter_by and filter_by != 'null':
                filter_by = int(filter_by)
                nft_transaction = nft_transaction.filter(created_at__gte=datetime.datetime.now()-datetime.timedelta(days=filter_by))
            # for transaction in nft_transaction:
            #     transaction['commission_amount'] = scientific_to_float(transaction.commission_amount)
            paginator = CustomPageNumberPagination()
            result = paginator.paginate_queryset(nft_transaction, request)
            serializer = TransactionNFTSerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class NFTCommissionView(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            set_commission = Commission.objects.first()
            serializer = NFTCommissionViewSerializer(set_commission)
            return Response({
                "status": True, "status_code": 200, 'msg': "Commission listed",
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)
    def create(self, request, *args, **kwargs):
        try:
            commission = Commission.objects.first()
            serializer = NFTCommissionViewSerializer(commission, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT commission update successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class BidOnNFTDetailsView(viewsets.ModelViewSet):
    queryset = BidOnNFT.objects.all()
    serializer_class = BidOnNFTDetailsSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            nft_id = self.kwargs.get('pk')
            nft_by_id = NFT.objects.filter(id=nft_id).first()
            # serializer = NFTViewSerializer(nft_by_id)
            queryset = self.queryset.filter(nft_detail=nft_id, bids_on_this_nft=True, seller_wallet=nft_by_id.nft_owner,
                                            seller_profile=nft_by_id.user).order_by("-id")

            serializer = self.serializer_class(queryset, many=True)
            return Response({
                "status": True, "status_code": 200, 'msg': 'Bid on NFT retrieve successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class DoBidOnNFTView(viewsets.ModelViewSet):
    queryset = BidOnNFT.objects.all()
    serializer_class = BidOnNFTDetailsSerializer
    permission_classes = [IsAuthenticated, IsEmailExist]

    def create(self, request, *args, **kwargs):
        try:
            # nft_id = self.kwargs.get('pk')
            wallet_id = UserWalletAddress.objects.filter(user_wallet=request.user.id).first()
            # request.data._mutable = True
            request.data['bidder_wallet'] = wallet_id.id
            request.data['bidder_profile'] = request.user.id

            nft = NFT.objects.get(id=request.data['nft_detail'])

            request.data['seller_wallet'] = nft.nft_owner.id
            request.data['seller_profile'] = nft.user.id

            serializer = self.serializer_class(data=request.data, context={'user': request.user})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'Bid successfully placed.',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400,
                'msg':[e.args[0]['non_field_errors'][0] if 'non_field_errors' in e.args[0] else e.args[0]][0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class ClaimNFTView(viewsets.ModelViewSet):
    queryset = NFT.objects.all()
    serializer_class = ClaimNFTSerializer
    permission_classes = [IsAuthenticated]
    def partial_update(self, request, *args, **kwargs):
        """
        this is used when user will claim his nft and shift ownership
        """
        global body
        try:
            nft_id = self.kwargs.get('pk')
            user_wallet =  UserWalletAddress.objects.filter(user_wallet=request.user.id).first()
            nft_by_id = NFT.objects.filter(id=nft_id, is_listed=True).first()

            request.data["nft"] = nft_by_id.id
            request.data["nft_token_id"] = nft_by_id.token_id
            request.data["seller"] = nft_by_id.nft_owner.id
            request.data["seller_user"] = nft_by_id.user.id
            request.data["buyer"] = user_wallet.id
            request.data["buyer_user"] = request.user.id
            request.data["commission_percentage"] = nft_by_id.service_fee
            request.data["royality_percentage"] = nft_by_id.royality
            request.data["category_of_nft"] = nft_by_id.nft_category.category_name
            request.data["nft_token_id"] = nft_by_id.token_id


            if nft_by_id.nft_sell_type == "Fixed Price":
                request.data["sold_price"] = nft_by_id.fix_price

            if nft_by_id.nft_sell_type == "Timed Auction":
                last_bid = BidOnNFT.objects.filter(nft_detail=nft_id, bidder_wallet=user_wallet.id,
                            bidder_profile=request.user.id, seller_wallet=nft_by_id.nft_owner.id, bids_on_this_nft=True,
                            seller_profile=nft_by_id.user.id, is_claimed=False).order_by('-id').first()
                request.data["sold_price"] = last_bid.bid_price
                last_bid.is_claimed=True
                last_bid.save()

                bids_on_nft = BidOnNFT.objects.filter(nft_detail=nft_id, seller_wallet=nft_by_id.nft_owner.id,
                         bids_on_this_nft=True, seller_profile=nft_by_id.user.id).order_by('-id')
                bids_on_nft.update(bids_on_this_nft=False)

            # nft_by_id.service_fee hardcoded in nft when nft created or ...
            request.data["commission_amount"] = float(Decimal(str(request.data["sold_price"]))/Decimal("100")*Decimal(str(nft_by_id.service_fee)))
            request.data["royality_amount"] = float(Decimal(str(request.data["sold_price"]))/Decimal("100")*Decimal(str(nft_by_id.royality)))
            request.data["seller_asset"] = float(Decimal(str(request.data["sold_price"]))-Decimal(str(request.data["commission_amount"]))-Decimal(str(request.data["royality_amount"])))

            serializer_transaction = TransactionNFTSerializer(data=request.data, context={'user': request.user})
            serializer_transaction.is_valid(raise_exception=True)
            serializer_transaction.save()

            request.data["is_listed"]= False
            request.data['user'] = request.user.id
            request.data['nft_owner'] = user_wallet.id

            nft_commission = Commission.objects.all().order_by('-id').first()
            request.data["service_fee"] = nft_commission.set_commission

            category = NFTCategory.objects.all().first()

            collection = Collection.objects.filter(create_by=request.user.id, name="Default").first()

            if collection is None:
                data = {
                    "name" : "Default",
                    "create_by": request.user.id,
                    "collection_category": category.id,
                    "website_url": "None",
                    "instagram_url": "None",
                    "description": "None"
                }
                serializer = UserCollectionSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

            collection = Collection.objects.filter(create_by=request.user.id, name="Default").first()

            request.data['nft_collection'] = collection.id
            # request.data['e_mail'] = False

            # request.data['nft_category'] = category.id


            if nft_by_id:
                serializer = ClaimNFTViewSerializer(nft_by_id, data=request.data, partial=True)
                # request.data._mutable = True
                serializer.is_valid(raise_exception=True)
                serializer.save()
                if request.user.email:
                    if serializer.validated_data['is_listed'] is False:
                        body = f"You have purchased NFT '{nft_by_id.nft_title}'. To visit your " \
                               f"NFT click on link given below " + os.getenv('FRONTEND_SITE_URL') + str(nft_id)

                        data = {
                            'subject': 'Your Phynom NFT Status',
                            'body': body,
                            'to_email': request.user.email
                        }
                        Utill.send_email(data)
                # tags = Tags.objects.create()
                # nft.tags_set.add(*request.data['tags_title'])
                return Response({
                    "status": True, "status_code": 200, 'msg': 'NFTs purchased successfully',
                    "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({
            "status": False, "status_code": 400, 'msg': 'Something wrong!',
            "data": []}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class DeleteDocs(viewsets.ViewSet):
    def destroy(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            doc = SupportingDocuments.objects.get(id=id)
            client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            bucket = AWS_STORAGE_BUCKET_NAME
            key = doc.documents
            if doc.documents:
                client.delete_object(Bucket=bucket, Key=str(key))
                doc.delete()
            return Response({
                "status": True, "status_code": 200, 'msg': 'Document delete successfully',
                "data": []}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': "Something is wrong with this document",
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class NFTExplorView(viewsets.ModelViewSet):
    queryset = NFT.objects.all()
    serializer_class = NFTExplorSerializer

    def list(self, request, *args, **kwargs):
        global queryset, nft_queryset, nft_tags_set
        try:
            nft_sort_by = self.request.query_params.get('sort_by')
            nft_min_price = self.request.query_params.get('min_price')
            nft_max_price = self.request.query_params.get('max_price')
            nft_tags = self.request.query_params.get('tags')
            nft_category = self.request.query_params.get('category')
            collection_id = self.request.query_params.get('collection')
            search = self.request.query_params.get('search')
            filter_by = self.request.query_params.get('filter_by')
            listingtime = self.request.query_params.get('listingtime')
            if nft_tags:
                nft_tags_list = nft_tags.split(',')
                nft_tags_set = set(list(map(int, nft_tags_list)))
            # nft_tags_set = set(nft_tags_list)
            # check = all(item in List1 for item in List2)
            # a =  NFT.objects.exclude(updated_at=)
            user = request.user.id
            collection = Collection.objects.filter(id=collection_id).first()

            if not nft_sort_by:
                if collection and user==collection.create_by.id:
                    queryset = self.queryset.filter(nft_collection__id=collection_id)
                else:
                    queryset = self.queryset.filter(nft_collection__id=collection_id, is_listed=True, is_minted=True)

            date = datetime.datetime.utcnow()
            utc_time = calendar.timegm(date.utctimetuple())

            if nft_sort_by=="newest_listed":
                queryset = self.queryset.filter(
                    Q(nft_sell_type="Timed Auction", end_datetime__gt=utc_time) | Q(nft_sell_type="Fixed Price"),
                    is_listed=True, is_minted=True, nft_status="Approved").order_by('-updated_at')
            elif nft_sort_by=="ascending":
                queryset = self.queryset.filter(
                    Q(nft_sell_type="Timed Auction", end_datetime__gt=utc_time) | Q(nft_sell_type="Fixed Price"),
                    is_listed=True, is_minted=True, nft_status="Approved").order_by('created_at')
            elif nft_sort_by=="descending":
                queryset = self.queryset.filter(
                    Q(nft_sell_type="Timed Auction", end_datetime__gt=utc_time) | Q(nft_sell_type="Fixed Price"),
                    is_listed=True, is_minted=True, nft_status="Approved").order_by('-created_at')

            if search:
                queryset = queryset.filter(nft_title__icontains=search, nft_status='Approved', is_listed=True)

            if nft_category!=None and nft_category!='all':
                queryset = queryset.filter(nft_category__id=nft_category)

            if filter_by:
                filter_by = int(filter_by)
                queryset = queryset.filter(created_at__gte=datetime.datetime.now()-datetime.timedelta(days=filter_by))

            if nft_min_price:
                queryset = queryset.filter(Q(fix_price__gte=nft_min_price) | Q(starting_price__gte=nft_min_price))

            if nft_max_price:
                queryset = queryset.filter(Q(fix_price__lte=nft_max_price) | Q(starting_price__lte=nft_max_price))

            if listingtime:
                if listingtime == "yesterday":
                    queryset = queryset.filter(created_at__gte=datetime.datetime.now() - datetime.timedelta(days=1))
                if listingtime == "last24hrs":
                    queryset = queryset.filter(created_at__gte=datetime.datetime.now() - datetime.timedelta(hours=24))
                if listingtime == "last7days":
                    queryset = queryset.filter(created_at__gte=datetime.datetime.now() - datetime.timedelta(days=7))
                if listingtime == "thismonth":
                    queryset = queryset.filter(created_at__gte=datetime.datetime.now() - datetime.timedelta(days=30))
                if listingtime == "thisyear":
                    queryset = queryset.filter(created_at__gte=datetime.datetime.now() - datetime.timedelta(days=365))

            # date = datetime.datetime.utcnow()
            # utc_time = calendar.timegm(date.utctimetuple())
            #
            # if nft_sort_by:
            #     queryset = queryset.filter(Q(nft_sell_type="Timed Auction", end_datetime__gt=utc_time) | Q(nft_sell_type="Fixed Price"))

        # data['tag_title'] = NftTagSerializer(instance.tags_set.filter(nft_create_info__id=instance.id), many=True).data

            if nft_tags:
                tags_list = []
                nft_queryset = []
                for one_nft in queryset:
                    nft_all_tags = Tags.objects.filter(nft_create_info__id=one_nft.id)
                    for one_tag in nft_all_tags:
                        tag_id = one_tag.id
                        tags_list.append(tag_id)
                    tags_list_set = set(tags_list)
                    check_subset = nft_tags_set.issubset(tags_list_set)
                    tags_list = []
                    if check_subset is True:
                        nft_queryset.append(one_nft)

                    # nft_tags_list.append(nft_all_tags)
            #     for tag in nft_tags:
            #         queryset = self.queryset.filter(fix_price__lte=nft_max_price, starting_price__lte=nft_max_price)

            # queryset = self.queryset.filter(Q(is_minted=True) | Q(is_minted=False),)

            paginator = CustomPageNumberPagination()
            if nft_tags:
                result = paginator.paginate_queryset(nft_queryset, request)
            else:
                result = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class(result, many=True)
            return paginator.get_paginated_response(serializer.data)
            # serializer = self.serializer_class(nft_queryset, many=True)
            # return Response({
            #     "status": True, "status_code": 200, 'msg': 'Explore NFTs listed successfully',
            #     "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


# class FindAuctionWinerUser(viewsets.ModelViewSet):
#     """will take some arguments from frontend and send the email to the duction winer user to claim nft"""
#     # queryset = UserWalletAddress.objects.all()
#
#     def SendEmailWinNFT(self, request, *args, **kwargs):
#         """send email to the action winer user, to claim nft"""
#         try:
#             user_wallet_no = 'newuser'
#             nft_token_id = '123456789'
#             price = '0.35895'
#
#             wallet_info = UserWalletAddress.objects.filter(wallet_address=user_wallet_no).first()
#             user = User.objects.filter(id=wallet_info.user_wallet.id).first()
#             nft = NFT.objects.filter(token_id=nft_token_id).first() #nft.nft_title
#             if user.email:
#                 body = f"You are the winer of '{nft.nft_title}' NFT. You win this NFT by bidding of {price} ETH. " \
#                        f"To visit and claim your " \
#                        f"NFT click on the given link " + os.getenv('FRONTEND_SHOW_NFT_URL') + str(nft.id)
#
#                 data = {
#                     'subject': 'Claim Your Phynom NFT',
#                     'body': body,
#                     'to_email': user.email
#                 }
#                 Utill.send_email(data)
#                 return Response({
#                     "status": True, "status_code": 200, 'msg': 'Email sent to the user for claim NFT.',
#                     "data": []}, status=status.HTTP_200_OK)
#             return Response({
#                 "status": True, "status_code": 200, 'msg': 'Your email not found.',
#                 "data": []}, status=status.HTTP_200_OK)
#
#         except Exception as e:
#             return Response({
#                 "status": False, "status_code": 400, 'msg': e.args[0],
#                 "data": []}, status=status.HTTP_400_BAD_REQUEST)


# class UserDisputeManagementView(viewsets.ViewSet):
#     """
#      This api is only use for Admin
#      can change the status of user NFT
#      """
#     # permission_classes = [IsAdminUser]
#     def dispute_email(self, request, *args, **kwargs):
#
#         try:
#             email_status = request.data['email_status']
#             if email_status == "general_query":
#                 user_name = request.data['user_name']
#                 email_address=request.data['email_address']
#                 email_body = request.data['email_body']
#
#                 email_validation = validateEmail(email_address)
#
#                 admin = User.objects.filter(is_superuser=True).first()
#
#                 if user_name and email_address and email_body and email_validation is True:
#                 # send email
#                     data = {
#                         'subject': f'Dispute notification on Phynom marketplace.',
#                         'body': f'Name of user: {user_name} \nEmail address of user: {email_address} \nDescription about dispute: {email_body}',
#                         'to_email': admin.email
#                     }
#                     Utill.send_email(data)
#
#                     return Response({
#                         "status": True, "status_code": 200, 'msg': 'Email send successfully to the admin.',
#                         "data": []}, status=status.HTTP_200_OK)
#
#                 return Response({
#                     "status": False, "status_code": 400, 'msg': 'Please enter correct information.',
#                     "data": []}, status=status.HTTP_400_BAD_REQUEST)
#             elif email_status == "dispute":
#                 user_name = request.data['user_name']
#                 email_address = request.data['email_address']
#                 email_body = request.data['email_body']
#                 wallet_address = request.data['wallet_address']
#                 contract_no_NFT = request.data['contract_no_NFT']
#
#                 email_validation = validateEmail(email_address)
#
#                 admin = User.objects.filter(is_superuser=True).first()
#
#                 if user_name and email_address and email_body and email_validation is True:
#                     # send email
#                     data = {
#                         'subject': f'Dispute notification on Phynom marketplace.',
#                         'body': f'Name of user: {user_name} \nEmail address of user: {email_address} \nDescription about dispute: {email_body} \nWallet address of user: {wallet_address} \nContract address of NFT: {contract_no_NFT}',
#                         'to_email': admin.email
#                     }
#                     Utill.send_email(data)
#
#                     return Response({
#                         "status": True, "status_code": 200, 'msg': 'Email send successfully to the admin.',
#                         "data": []}, status=status.HTTP_200_OK)
#                 return Response({
#                     "status": False, "status_code": 400, 'msg': 'Please enter correct information.',
#                     "data": []}, status=status.HTTP_400_BAD_REQUEST)
#
#         except Exception as e:
#             return Response({
#                 "status": False, "status_code": 400, 'msg': e.args[0],
#                 "data": []}, status=status.HTTP_400_BAD_REQUEST)

class ContactUsView(viewsets.ViewSet):
    serializer_class = ContactUsSerializer
    def contact_us(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            contact_status = serializer.validated_data['contact_status']
            user_name = serializer.validated_data['user_name']
            email_address = serializer.validated_data['email_address']
            email_body = serializer.validated_data['email_body']
            if contact_status == "Dispute":
                wallet_address = serializer.validated_data['wallet_address']
                contract_nft = serializer.validated_data['contract_nft']
                email_validation = validateEmail(email_address)
                admin = User.objects.filter(is_superuser=True).first()
                if user_name and email_address and email_body and email_validation is True:
            # send email
                    data = {
                        'subject': f'Dispute notification on Phynom marketplace.',
                        'body': f'Name of user: {user_name} \nEmail address of user: {email_address} \nDescription about dispute: {email_body} \nWallet address of user: {wallet_address} \nContract address of NFT: {contract_nft}',
                        'to_email': admin.email
                    }
                    Utill.send_email(data)
                    return Response({
                        "status": True, "status_code": 200, 'msg': 'Email send successfully to the admin.',
                        "data": []}, status=status.HTTP_200_OK)
                return Response({
                    "status": False, "status_code": 400, 'msg': 'Please enter correct information.',
                    "data": []}, status=status.HTTP_400_BAD_REQUEST)
            else:
                email_validation = validateEmail(email_address)
                admin = User.objects.filter(is_superuser=True).first()
                if user_name and email_address and email_body and email_validation is True:
            # send email
                    data = {
                        'subject': f'General Query notification on Phynom marketplace.',
                        'body': f'Name of user: {user_name} \nEmail address of user: {email_address} \nDescription about dispute: {email_body}',
                        'to_email': admin.email
                    }
                    Utill.send_email(data)
                    return Response({
                        "status": True, "status_code": 200, 'msg': 'Email send successfully to the admin.',
                        "data": []}, status=status.HTTP_200_OK)
                return Response({
                    "status": False, "status_code": 400, 'msg': 'Please enter correct information.',
                    "data": []}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class SearchAPIView(viewsets.ViewSet):
    def search_function(self, request, *args, **kwargs):
        try:
            item = self.request.query_params.get('item')
            date = datetime.datetime.utcnow()
            utc_time = calendar.timegm(date.utctimetuple())
            # queryset = NFT.objects.filter(nft_title__icontains=item, Q(nft_sell_type="Timed Auction", end_datetime__gt=utc_time) | Q(nft_sell_type="Fixed Price"),
            #         is_listed=True, is_minted=True, nft_status="Approved").order_by('-updated_at')
            queryset = NFT.objects.filter(nft_title__icontains=item, nft_status='Approved', is_listed=True).order_by('-updated_at')
            paginator = CustomPageNumberPagination()
            result = paginator.paginate_queryset(queryset, request)
            serializer = NFTExplorSerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0], "data": []}, status=status.HTTP_400_BAD_REQUEST)


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
