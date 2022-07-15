from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate

from backend.pagination import CustomPageNumberPagination
from user.models import User
# from .pagination import CustomPagination
from blockchain.models import Collection, UserWalletAddress
from user.serializers import AdminLoginSerializer, AdminChangePasswordSerializer, \
    UserProfileSerializer, UserProfileStatusUpdateViewSerializer, \
    UserCollectionSerializer, UserProfileDetailsViewSerializer, UserLoginSerializer, TermsAndPoliciesViewSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import viewsets
from user.custom_permissions import IsApprovedUser

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class AdminLoginView(APIView):
    """
    this login is only for admin that provide email and password for login
    """
    def post(self, request, *args, **kwargs):
        try:
            serializer = AdminLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            if  User.objects.filter(email=email).exists():
                user = User.objects.filter(email=email).first()
                if user.is_superuser:
                    user = authenticate(email=email, password=password)
                    if not user:
                        return Response({"status": False, "status_code": 400, "msg": "Wrong email or password",
                                         "data": []}, status=status.HTTP_400_BAD_REQUEST)
                    token = get_tokens_for_user(user)
                    return Response({"status": True, "status_code": 200, 'msg': 'Login Successfully',
                                     "data": {"token": token}}, status=status.HTTP_200_OK)
                else:
                    return Response({"status": False, "status_code": 400, "msg": "User is not Superuser!",
                                     "data": []}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"status": False, "status_code": 400, "msg": "User does not exist!",
                                 "data": []}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": False, "status_code": 400, "msg": e.args[0],
                             "data": []}, status=status.HTTP_400_BAD_REQUEST)



class AdminChangePasswrodView(APIView):
    """
    only for admin that can change his/her admin login password by login admin dashboard
    """
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        try:
            serializer = AdminChangePasswordSerializer(data=request.data, context={'user': request.user})
            serializer.is_valid(raise_exception=True)
            return Response({
                "status": True, "status_code": 200, "msg": "Password Reset Successfully",
                "data": []}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400,
                "msg": e.args[0], "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    """
    login with matamask for user, give it access token if user create or not created then create
    """
    # permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        try:
            wallet_address = request.data.get('wallet_address')
            address = UserWalletAddress.objects.filter(wallet_address=wallet_address)
            if address.exists():
                wallet_address = UserWalletAddress.objects.filter(wallet_address=wallet_address).first()
                serializer = UserLoginSerializer(wallet_address)
                profile_id = User.objects.filter(id=wallet_address.user_wallet.id).first()
                serializer_user = UserProfileSerializer(profile_id)
                token = get_tokens_for_user(profile_id)
                return Response({
                    "status": True, "status_code": 200, 'msg': 'User address exists already',
                    "data": serializer.data,"profile": serializer_user.data, "token": token}, status=status.HTTP_200_OK)
            else:
                data = {'name': None}
                serializer_user = UserProfileSerializer(data=data)
                serializer_user.is_valid(raise_exception=True)
                serializer_user.save()
                last_id = User.objects.order_by('-id')[0]
                profile_id = User.objects.filter(id=last_id.id).first()
                serializer = UserLoginSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user_wallet=profile_id)
                # wallet_address = UserWalletAddress.objects.get(wallet_address=wallet_address)
                token = get_tokens_for_user(profile_id)
                return Response({
                    "status": True, "status_code": 200, 'msg': 'User address saved successfully and profile created',
                    "data": serializer.data, "profile": serializer_user.data, "token": token}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileListView(viewsets.ViewSet):
    """
    any user can see his/her profile or the profile of other user, also gust user perform this task
    """
    permission_classes = [AllowAny]
    # pagination_class = CustomPagination
    def list(self, request, *args, **kwargs):
        try:
            users = User.objects.all()
            # serializer = UserProfileSerializer(users, many=True)
            # return Response({
            #     "status": True, "status_code": 200, 'msg': 'User Profile Listed Successfully',
            #     "data": serializer.data}, status=status.HTTP_200_OK)
            paginator = CustomPageNumberPagination()
            result = paginator.paginate_queryset(users, request)
            serializer = UserProfileSerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            user = User.objects.get(id=id)
            serializer = UserProfileSerializer(user)
            return Response({
                "status": True, "status_code": 200, 'msg': 'User Profile Retrieve Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateView(viewsets.ViewSet):
    """
    user can update some fields of his/her profile
    """
    permission_classes = [IsAuthenticated]
    def patch(self, request, *args, **kwargs):
        try:
            user = request.user
            if user.status!="Pending" and user.status!="Disapprove":
                if user.status!="Approve":
                    id = self.kwargs.get('pk')
                    user_id = User.objects.get(id=id)
                    serializer = UserProfileSerializer(user_id, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response({
                        "status": True, "status_code": 200, 'msg': 'User Profile Updated Successfully',
                        "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    id = self.kwargs.get('pk')
                    user_id = User.objects.get(id=id)
                    profile_picture = request.data.get('profile_picture')
                    cover_picture = request.data.get('cover_picture')
                    name = request.data.get('name')
                    username = request.data.get('username')
                    email = request.data.get('email')
                    context ={
                        "profile_picture" : profile_picture,
                        "cover_picture" : cover_picture,
                        "name" : name,
                        "username" : username,
                        "email" : email
                    }
                    serializer = UserProfileSerializer(user_id, data=context, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response({
                        "status": True, "status_code": 200, 'msg': 'User Profile Updated Successfully',
                        "data": serializer.data}, status=status.HTTP_200_OK)

            else:
                return Response({
                    "status": False, "status_code": 400, 'msg': "Your Profile is not Approved",
                    "data": []}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

#
class UserProfileDetailsView(viewsets.ViewSet):
    """
    This api is only use for Admin
    admin can see the user profile details from admin panel
    """
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        try:
            # user = User.objects.all().order_by('-id')
            user = User.objects.exclude(status="Not Requested").order_by('-id')
            # serializer = UserProfileDetailsViewSerializer(user, many=True)
            # return Response({
            #     "status": True, "status_code": 200, 'msg': 'Users Profiles Listed Successfully',
            #     "data": serializer.data}, status=status.HTTP_200_OK)
            paginator = CustomPageNumberPagination()
            result = paginator.paginate_queryset(user, request)
            serializer = UserProfileDetailsViewSerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileStatusUpdateView(viewsets.ViewSet):
    """
     This api is only use for Admin
     can change the status of user profile
     """
    permission_classes = [IsAuthenticated]
    def partial_update(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            user_id = User.objects.get(id=id)
            # user = User.objects.get(id=pk)
            serializer = UserProfileStatusUpdateViewSerializer(user_id, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'User Profiles Updated Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserCollection(viewsets.ViewSet):
    """
    only user can creat collection, and update
    """
    permission_classes = [IsApprovedUser, IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            data['create_by'] = request.user.id
            serializer = UserCollectionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'User Collection Created Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            collection_id = Collection.objects.get(id=id)
            if request.user.id == collection_id.create_by.id:
                # collection = Collection.objects.get(id=pk)
                serializer = UserCollectionSerializer(collection_id, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({
                    "status": True, "status_code": 200, 'msg': 'User Collection Update Successfully',
                    "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": False, "status_code": 400, 'msg': 'User not creator of this Collection',
                    "data": []}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

class ListUserCollection(viewsets.ViewSet):
    """
    any user can see(list) collection, and retrieve
    """
    permission_classes = [AllowAny]
    # pagination_class = PageNumberPagination
    def list(self, request, *args, **kwargs):
        try:
            collections = Collection.objects.all()
            # serializer = UserCollectionSerializer(collections, many=True)
            paginator = CustomPageNumberPagination()
            result = paginator.paginate_queryset(collections, request)
            serializer = UserCollectionSerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)
            # return Response({
            #     "status": True, "status_code": 200, 'msg': 'User Collection Listed Successfully',
            #     "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            collection_id = Collection.objects.get(id=id)
            serializer = UserCollectionSerializer(collection_id)
            return Response({
                "status": True, "status_code": 200, 'msg': 'User Collection Retrieve Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserCollectionListView(viewsets.ViewSet):
    """
    this view is for list/retrieve nfts of perticular user by its id
    """
    permission_classes = [AllowAny]
    def retrieve(self, request, *args, **kwargs):
        try:
            user_id = self.kwargs.get('pk')
            collections = Collection.objects.filter(create_by=user_id)
            # serializer = UserCollectionSerializer(collections, many=True)
            # return Response({
            #     "status": True, "status_code": 200, 'msg': 'User Collections Listed Successfully',
            #     "data": serializer.data}, status=status.HTTP_200_OK)
            paginator = CustomPageNumberPagination()
            result = paginator.paginate_queryset(collections, request)
            serializer = UserCollectionSerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

class TermsAndPoliciesView(viewsets.ViewSet):
    """
     This api is only use for user he/she will agree to the terms and condition
     """
    permission_classes = [IsAuthenticated]
    def partial_update(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            user_id = User.objects.get(id=id)
            # user = User.objects.get(id=pk)
            serializer = TermsAndPoliciesViewSerializer(user_id, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'User Agreed with terms and policies',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)