from rest_framework.response import Response
from rest_framework import status
from blockchain.serializers import *
from blockchain.models import *
from user.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import viewsets
from user.custom_permissions import IsApprovedUser

class ListRetrieveNFTView(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        try:
            list_nft = NFT.objects.filter(nft_status="Approved")
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
            request.data['nft_owner'] = wallet_id.id
            nft = NFTViewSerializer(data=request.data)
            nft.is_valid(raise_exception=True)
            if request.data.get('documents'):
                nft.save()
                last_id = NFT.objects.order_by('-id')[0]
                all_docs = dict(request.data.lists())['documents']
                documents = NFTSupportingDocumentsSerializer(data=request.data)
                documents.is_valid(raise_exception=True)
                # for doc in all_docs:
                #     save_doc = {'nft_create_info':last_id.id, "documents":doc}
                #     documents
                return Response({
                    "status": True, "status_code": 200, 'msg': 'User Collection Created Successfully',
                    "data": ""}, status=status.HTTP_200_OK)
            else:
                return Response({'msg': 'upload docs'})
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        try:
            nft_id = self.kwargs.get('pk')
            nft_by_id = NFT.objects.get(id=nft_id)
            if request.user.id == nft_by_id.nft_owner.id:
                serializer = NFTViewSerializer(nft_by_id, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({
                    "status": True, "status_code": 200, 'msg': 'User NFTs Updated Successfully',
                    "data": serializer.data}, status=status.HTTP_200_OK)
            else:
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
    def retrieve(self, request, *args, **kwargs):
        try:
            user_id = self.kwargs.get('pk')
            user_wallet = UserWalletAddress.objects.filter(user_wallet=user_id).first()
            list_nft = NFT.objects.filter(nft_owner=user_wallet.id).filter(nft_status="Approved")
            serializer = NFTViewSerializer(list_nft, many=True)
            return Response({
                "status": True, "status_code": 200, 'msg': 'User NFTs Listed Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class NFTCategoryView(viewsets.ViewSet):

    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            nft_category = NFTCategory.objects.all()
            serializer = NFTCategorySerializer(nft_category, many=True)
            return Response({
                "status": True, "status_code": 200, 'msg': 'NFT Category Listed Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)



