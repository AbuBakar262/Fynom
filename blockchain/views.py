from rest_framework.response import Response
from rest_framework import status

from backend.pagination import CustomPageNumberPagination
from blockchain.serializers import *
from blockchain.models import *
from user.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import viewsets
from user.custom_permissions import IsApprovedUser
from user.utils import Utill


class ListRetrieveNFTView(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        try:
            list_nft = NFT.objects.filter(nft_status="Pending").order_by('-id')
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
            nft_by_id = NFT.objects.get(id=nft_id)
            serializer = NFTViewSerializer(nft_by_id)
            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFTs Retrieve Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class CreateUpdateNFTView(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

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
            serializer = NFTViewSerializer(data=request.data, context={'request':request})
            serializer.is_valid(raise_exception=True)
            nft = serializer.save()
            nft.tags_set.add(*request.data['tags_title'])
            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFT Created Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, *args, **kwargs):
        """
        this is used for update nft by id, docoments and tags will delete and auto insert
        """
        try:
            nft_id = self.kwargs.get('pk')
            user_wallet =  UserWalletAddress.objects.filter(user_wallet=request.user.id).first()
            nft_by_id = NFT.objects.filter(id=nft_id, nft_creator__id=user_wallet.id).first()
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
        try:
            user_id = request.query_params.get('pk')
            user_wallet = UserWalletAddress.objects.filter(user_wallet=user_id).first()
            list_nft = NFT.objects.filter(nft_owner=user_wallet.id).filter(nft_status="Pending")
            serializer = NFTViewSerializer(list_nft, many=True)
            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFTs Listed Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
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
                "status": True, "status_code": 200, 'msg': 'NFT Tag is deleted Successfully',
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
    # permission_classes = [IsAdminUser]
    def partial_update(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            nft_instance = NFT.objects.filter(id=id).first()
            # nft_instance = NFT.objects.filter(id = nft.id).first()
            user = User.objects.filter(id = nft_instance.user.id).first()
            profile_status = request.data['nft_status']
            status_reasons = request.data['status_remarks']
            serializer = UserNFTStatusUpdateViewSerializer(nft_instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if user.email:
            # send email
                body = None
                if profile_status == 'Approved':
                    body = "Congratulations! your NFT has been Approved. " + status_reasons
                if profile_status == 'Disapproved':
                    body = "We are Sorry! your NFT has been Disapproved. " + status_reasons
                data = {
                    'subject': 'Your Phynom NFT Status',
                    'body': body,
                    'to_email': user.email
                }
                Utill.send_email(data)
            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFT Status Update Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)