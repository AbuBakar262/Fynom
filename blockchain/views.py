from django.db.models import Q, Count
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F, Value, CharField
import os
from backend.pagination import CustomPageNumberPagination
from blockchain.serializers import *
from blockchain.models import *
from user.models import User
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import viewsets
from user.serializers import UserCollectionSerializer
from user.utils import Utill
import boto3
from backend.settings import *

class ListRetrieveNFTView(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        try:
            list_nft = NFT.objects.filter(nft_status="Approved").order_by('-id')
            serializer = NFTViewSerializer(list_nft, many=True)
            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFTs Listed Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
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

            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFTs Retrieve Successfully',
                "data": serializer.data, "creator_user":creator_user, "owner_user":owner_user}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class CreateUpdateNFTView(viewsets.ViewSet):

    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            wallet_id = UserWalletAddress.objects.filter(user_wallet=user_id).first()
            request.data._mutable = True
            request.data['nft_creator'] = wallet_id.id
            request.data['user'] = request.user.id
            request.data['nft_owner'] = wallet_id.id
            request.data['tags_title'] = request.data.get('tag_title').split(',')
            # request.data['tags'] = request.data.get('tags').split(',')
            nft_commission = Commission.objects.all().order_by('-id').first()
            request.data["service_fee"] = nft_commission.set_commission
            serializer = NFTViewSerializer(data=request.data, context={'request':request})
            serializer.is_valid(raise_exception=True)
            nft = serializer.save()
            nft.tags_set.add(*request.data['tags_title'])
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT submitted successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, *args, **kwargs):
        """
        this is used for update nft by id, docoments and tags will delete and auto insert
        """
        global body
        try:
            nft_id = self.kwargs.get('pk')
            user_wallet =  UserWalletAddress.objects.filter(user_wallet=request.user.id).first()
            nft_by_id = NFT.objects.filter(id=nft_id, nft_owner__id=user_wallet.id).first()
            # nft_status = "Pending"
            nft_status = request.data['nft_status']
            # request.data._mutable = True
            # request.data['nft_status'] = nft_status

            if nft_by_id:
                serializer = NFTViewSerializer(nft_by_id, data=request.data, context={'request':request}, partial=True)
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
                        "status": True, "status_code": 200, 'msg': 'User NFTs Updated Successfully',
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
                                                      is_listed=False, nft_category=nft_category_id).values('id',

                                                                                                 'nft_title',
                                                                                                 'fix_price',
                                                                                                 'nft_sell_type',
                                                                                                 'starting_price',
                                                                                                 'ending_price',
                                                                                                 'start_dateTime',
                                                                                                 'end_datetime',
                                                                                                 'is_minted',
                                                                                                 'is_listed',
                                                                                                 'nft_status',
                                                                                                 'nft_subject',
                                                                                                 'status_remarks',
                                                                                                nft_user_id=F('user__id'),
                                                                                                # user_profile_pic=
                                                                                                #  F('user__profile_picture'),
                                                                                                 user_nft_collection
                                                                                                =F('nft_collection__'
                                                                                                   'name'),
                                                                                                 user_nft_category
                                                                                                =F('nft_category__'
                                                                                                   'category_name'),
                        nft_thumbnail = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("thumbnail"), output_field=CharField()),
                        nft_teaser = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("teaser"), output_field=CharField()),
                                        nft_pic = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("nft_picture"),
                                                         output_field=CharField()),
                                                                                                        user_profile_pic=Concat(
                                                                                                                Value(
                                                                                                                    os.getenv(
                                                                                                                        'STAGING_PHYNOM_BUCKET_URL')),
                                                                                                                F("user__profile_picture"),
                                                                                                                output_field=CharField())
                        ).order_by('-id')
                    else:
                        list_nft = NFT.objects.filter(Q(is_minted=True) | Q(is_minted=False), nft_owner=user_wallet.id,
                                                      is_listed=False).values('id',

                                                                                                            'nft_title',
                                                                                                            'fix_price',
                                                                                                            'nft_sell_type',
                                                                                                            'starting_price',
                                                                                                            'ending_price',
                                                                                                            'start_dateTime',
                                                                                                            'end_datetime',
                                                                                                            'is_minted',
                                                                                                            'is_listed',
                                                                                                            'nft_status',
                                                                                                            'nft_subject',
                                                                                                            'status_remarks',
                                                                                                            nft_user_id=F(
                                                                                                                'user__id'),
                                                                                                            # user_profile_pic=
                                                                                                            #  F('user__profile_picture'),
                                                                                                            user_nft_collection
                                                                                                            =F('nft_collection__'
                                                                                                               'name'),
                                                                                                            user_nft_category
                                                                                                            =F('nft_category__'
                                                                                                               'category_name'),
                                                                                                            nft_thumbnail=Concat(
                                                                                                                Value(
                                                                                                                    os.getenv(
                                                                                                                        'STAGING_PHYNOM_BUCKET_URL')),
                                                                                                                F("thumbnail"),
                                                                                                                output_field=CharField()),
                                                                              nft_teaser=Concat(Value(os.getenv(
                                                                                  'STAGING_PHYNOM_BUCKET_URL')),
                                                                                                F("teaser"),
                                                                                                output_field=CharField()),
                                                                                                            nft_pic=Concat(
                                                                                                                Value(
                                                                                                                    os.getenv(
                                                                                                                        'STAGING_PHYNOM_BUCKET_URL')),
                                                                                                                F("nft_picture"),
                                                                                                                output_field=CharField()),
                                                                                                            user_profile_pic=Concat(
                                                                                                                Value(
                                                                                                                    os.getenv(
                                                                                                                        'STAGING_PHYNOM_BUCKET_URL')),
                                                                                                                F("user__profile_picture"),
                                                                                                                output_field=CharField())
                                                                                                            ).order_by(
                            '-id')

                if user_nft == "listmynft":
                    if nft_category_id != 'all':
                        list_nft = NFT.objects.filter(is_minted=True, nft_owner=user_wallet.id,
                                           is_listed=True, nft_category=nft_category_id).values('id',
                                                                                                # 'thumbnail',
                                                                                                #  'nft_picture',
                                                                                                 'nft_title',
                                                                                                 'fix_price',
                                                                                                 'nft_sell_type',
                                                                                                 'starting_price',
                                                                                                 'ending_price',
                                                                                                 'start_dateTime',
                                                                                                 'end_datetime',
                                                                                                 'is_minted',
                                                                                                 'is_listed',
                                                                                                 'nft_status',
                                                                                                'nft_subject',
                                                                                                 'status_remarks',
                                                                                                nft_user_id=F('user__id'),
                                                                                                # user_profile_pic=
                                                                                                #  F('user__profile_picture'),
                                                                                                 user_nft_collection
                                                                                                =F('nft_collection__'
                                                                                                   'name'),
                                                                                                 user_nft_category
                                                                                                =F('nft_category__'
                                                                                                   'category_name'),
                        nft_thumbnail = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("thumbnail"),
                                               output_field=CharField()),
                                                                                                nft_teaser=Concat(Value(
                                                                                                    os.getenv(
                                                                                                        'STAGING_PHYNOM_BUCKET_URL')),
                                                                                                                  F("teaser"),
                                                                                                                  output_field=CharField()),
                                        nft_pic = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("nft_picture"),
                                                         output_field=CharField()),
                                                                                                        user_profile_pic=Concat(
                                                                                                                Value(
                                                                                                                    os.getenv(
                                                                                                                        'STAGING_PHYNOM_BUCKET_URL')),
                                                                                                                F("user__profile_picture"),
                                                                                                                output_field=CharField())
                                                                                                ).order_by('-id')
                    else:
                        list_nft = NFT.objects.filter(is_minted=True, nft_owner=user_wallet.id,
                                                      is_listed=True).values('id',
                                                                                                           # 'thumbnail',
                                                                                                           #  'nft_picture',
                                                                                                           'nft_title',
                                                                                                           'fix_price',
                                                                                                           'nft_sell_type',
                                                                                                           'starting_price',
                                                                                                           'ending_price',
                                                                                                           'start_dateTime',
                                                                                                           'end_datetime',
                                                                                                           'is_minted',
                                                                                                           'is_listed',
                                                                                                           'nft_status',
                                                                                                           'nft_subject',
                                                                                                           'status_remarks',
                                                                                                           nft_user_id=F(
                                                                                                               'user__id'),
                                                                                                           # user_profile_pic=
                                                                                                           #  F('user__profile_picture'),
                                                                                                           user_nft_collection
                                                                                                           =F('nft_collection__'
                                                                                                              'name'),
                                                                                                           user_nft_category
                                                                                                           =F('nft_category__'
                                                                                                              'category_name'),
                                                                                                           nft_thumbnail=Concat(
                                                                                                               Value(
                                                                                                                   os.getenv(
                                                                                                                       'STAGING_PHYNOM_BUCKET_URL')),
                                                                                                               F("thumbnail"),
                                                                                                               output_field=CharField()),
                                                                             nft_teaser=Concat(Value(os.getenv(
                                                                                 'STAGING_PHYNOM_BUCKET_URL')),
                                                                                               F("teaser"),
                                                                                               output_field=CharField()),
                                                                                                           nft_pic=Concat(
                                                                                                               Value(
                                                                                                                   os.getenv(
                                                                                                                       'STAGING_PHYNOM_BUCKET_URL')),
                                                                                                               F("nft_picture"),
                                                                                                               output_field=CharField()),
                                                                                                           user_profile_pic=Concat(
                                                                                                               Value(
                                                                                                                   os.getenv(
                                                                                                                       'STAGING_PHYNOM_BUCKET_URL')),
                                                                                                               F("user__profile_picture"),
                                                                                                               output_field=CharField())
                                                                                                           ).order_by(
                            '-id')


                paginator = CustomPageNumberPagination()
                result = paginator.paginate_queryset(list_nft, request)
                return paginator.get_paginated_response(result)
            elif user_nft == "admin":
                list_nft = NFT.objects.filter(nft_status='Pending')\
                    .annotate(document_count=Count('nft_in_supportingdocument')).values('id',
                                                                                        'nft_title',
                                                                                        'nft_status',
                                                                                        'document_count',
                                                                                        nft_user_id=F('user__id'),
                                                                                        real_name=F('user__name'),
                                                                                        display_name=F('user__username'),
                                                                                        wallet_address=F('nft_owner__wallet_address'),
                                                                                        user_nft_category
                                                                                        =F('nft_category__'
                                                                                           'category_name'),
                nft_thumbnail = Concat(Value(os.getenv('STAGING_PHYNOM_BUCKET_URL')), F("thumbnail"), output_field=CharField())
                                                                                        ).order_by('-id')
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
            serializer = NFTCategorySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT Category Created Successfully',
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
                "status": True, "status_code": 200, 'msg': 'NFT Category Updated Successfully',
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
                "status": True, "status_code": 200, 'msg': 'NFT Category is deleted Successfully',
                "data": {}}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)



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
            data = request.data
            serializer = NftTagSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT Tag is Created Successfully',
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
                "status": True, "status_code": 200, 'msg': 'NFT Tag is Updated Successfully',
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
                "status": True, "status_code": 200, 'msg': 'NFT Tag is deleted Successfully',
                "data": {}}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

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
                "status": True, "status_code": 200, 'msg': 'User NFT Status Update Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class ListTransactionNFTView(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        try:
            nft_transaction = Transaction.objects.all().order_by("-id")
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
            set_commission = Commission.objects.all().order_by('-id').first()
            serializer = NFTCommissionViewSerializer(set_commission, many=True)
            return Response({
                "status": True, "status_code": 200, 'msg': "Commission listed",
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)
    def create(self, request, *args, **kwargs):
        try:
            serializer = NFTCommissionViewSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT Commission Created Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)
    def update(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            item_id = Commission.objects.get(id=id)
            serializer = NFTCommissionViewSerializer(item_id, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT Commission Updated Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400,'error':'Sorry Your data did not updated', 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class BidOnNFTDetailsView(viewsets.ModelViewSet):
    queryset = BidOnNFT.objects.all()
    serializer_class = BidOnNFTDetailsSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            nft_id = self.kwargs.get('pk')
            # nft_by_id = NFT.objects.get(id=nft_id)
            # serializer = NFTViewSerializer(nft_by_id)
            queryset = self.queryset.filter(nft_detail=nft_id).order_by("-id")

            serializer = self.serializer_class(queryset, many=True)
            return Response({
                "status": True, "status_code": 200, 'msg': 'Bid on NFT Retrieve Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class DoBidOnNFTView(viewsets.ModelViewSet):
    queryset = BidOnNFT.objects.all()
    serializer_class = BidOnNFTDetailsSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # nft_id = self.kwargs.get('pk')
            wallet_id = UserWalletAddress.objects.filter(user_wallet=request.user.id).first()
            # request.data._mutable = True
            request.data['bidder_wallet'] = wallet_id.id
            request.data['bidder_profile'] = request.user.id
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'Bid successfully created on NFT',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
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
            nft_by_id = NFT.objects.filter(id=nft_id).first()

            request.data["nft"] = nft_by_id.id
            request.data["nft_token_id"] = nft_by_id.token_id
            request.data["seller"] = nft_by_id.nft_owner.id
            request.data["seller_user"] = nft_by_id.user.id
            request.data["buyer"] = user_wallet.id
            request.data["buyer_user"] = request.user.id
            request.data["commission_percentage"] = nft_by_id.service_fee
            request.data["nft_category"] = nft_by_id.nft_category

            if nft_by_id.nft_sell_type == "Fixed Price":
                request.data["sold_price"] = nft_by_id.fix_price

            if nft_by_id.nft_sell_type == "Timed Auction":
                last_bid = BidOnNFT.objects.filter(nft_detail=nft_id, bidder_wallet=user_wallet.id,
                                                   bidder_profile=request.user.id).order_by('-id').first()
                request.data["sold_price"] = last_bid.bid_price

            request.data["commission_amount"] = (float(request.data["sold_price"])/100)*float(nft_by_id.service_fee)

            serializer_transaction = TransactionNFTSerializer(data=request.data)
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
            # request.data['nft_category'] = category.id


            if nft_by_id:
                serializer = NFTViewSerializer(nft_by_id, data=request.data, partial=True)
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
                    "status": True, "status_code": 200, 'msg': 'NFTs Purchased Successfully',
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

