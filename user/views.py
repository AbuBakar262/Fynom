from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from user.models import User
from blockchain.models import Collection
from user.serializers import AdminLoginSerializer, AdminChangePasswordSerializer, \
    UserProfileSerializer, UserProfileStatusUpdateViewSerializer,\
    UserCollectionSerializer, UserProfileDetailsViewSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets


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
                        return Response({"success": False, "status_code": 400, "message": "Wrong email or password",
                                         "data": []}, status=status.HTTP_400_BAD_REQUEST)
                    token = get_tokens_for_user(user)
                    return Response({"success": True, "status_code": 200, 'message': 'Login Success',
                                     "data": {"token": token}}, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "status_code": 400, "message": "User is not Superuser!",
                                     "data": []}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": False, "status_code": 400, "message": "User does not exist!",
                                 "data": []}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "status_code": 400, "message": e.args[0],
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
                "success": True, "status_code": 200, "message": "Password Reset Successfully",
                "data": []}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400,
                "message": e.args[0], "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileListView(viewsets.ViewSet):
    """
    user can see his/her profile
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_id = User.objects.get(id=request.user.id)
            serializer = UserProfileSerializer(user_id)
            return Response({
                "success": True, "status_code": 200, 'message': 'User Profile Listed Successfull',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileCreateView(viewsets.ViewSet):
    """
    user can create his/her profile
    """
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            # user_id = User.objects.get(id=request.user.id)
            # serializer = UserProfileSerializer(user_id, data=request.data)
            serializer = UserProfileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success": True, "status_code": 200, 'message': 'User Profile Created Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateView(viewsets.ViewSet):
    """
    user can update some fields of his/her profile
    """
    # permission_classes = [IsAuthenticated]
    def patch(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            user_id = User.objects.get(id=id)
            serializer = UserProfileSerializer(user_id, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success": True, "status_code": 200, 'message': 'User Profile Updated Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


# class UserStatusView(ListAPIView):
#     """
#     only for user that can see his/her profile status
#     """
#     queryset = User.objects.all()
#     serializer_class = UserProfileStatusUpdateViewSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request, *args, **kwargs):
#         try:
#             user_id = User.objects.get(id=request.user.id)
#             # queryset = self.get_queryset(id=id)
#             serializer = self.serializer_class(user_id)
#             return Response({
#                 "success": True, "status_code": 200, 'message': 'User Status Retrieve Successfully',
#                 "data": serializer.data}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({
#                 "success": False, "status_code": 400, 'message': e.args[0],
#                 "data": []}, status=status.HTTP_400_BAD_REQUEST)

#
class UserProfileDetailsView(viewsets.ViewSet):
    """
    This api is only use for Admin
    admin can see the user profile details from admin panel
    """
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        try:
            user = User.objects.all()
            serializer = UserProfileDetailsViewSerializer(user, many=True)
            return Response({
                "success": True, "status_code": 200, 'message': 'Users Profiles Listed Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileStatusUpdateView(viewsets.ViewSet):
    """
     This api is only use for Admin
     can change the status of user profile
     """
    permission_classes = [IsAdminUser]
    def partial_update(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            user_id = User.objects.get(id=id)
            # user = User.objects.get(id=pk)
            serializer = UserProfileStatusUpdateViewSerializer(user_id, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success": True, "status_code": 200, 'message': 'User Profiles Updated Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserCollection(viewsets.ViewSet):
    """
    only user can creat collection, can retrieve, list and update
    """
    permission_classes = [IsAuthenticated]
    def list(self, request, *args, **kwargs):
        try:
            collections = Collection.objects.all()
            serializer = UserCollectionSerializer(collections, many=True)
            return Response({
                "success": True, "status_code": 200, 'message': 'User Collection Listed Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            data['create_by'] = request.user.id
            serializer = UserCollectionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success": True, "status_code": 200, 'message': 'User Collection Created Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            collection_id = Collection.objects.get(id=id)
            # collection = Collection.objects.get(id=pk)
            serializer = UserCollectionSerializer(collection_id)
            return Response({
                "success": True, "status_code": 200, 'message': 'User Collection Retrieve Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        try:
            id = self.kwargs.get('pk')
            collection_id = Collection.objects.get(id=id)
            # collection = Collection.objects.get(id=pk)
            serializer = UserCollectionSerializer(collection_id, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success": True, "status_code": 200, 'message': 'User Collection Update Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

