from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from user.models import User
from blockchain.models import Collection
from user.serializers import UserLoginSerializer, UserPassowrdResetSerializer, SendPasswordResetEmailSerializer, \
    UserChangePasswordSerializer, UserProfileSerializer, UserProfileStatusUpdateViewSerializer, \
    UserProfileStatusViewSerializer, UserCollectionSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class AdminLoginView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            if  User.objects.filter(email=email).exists():
                user = User.objects.filter(email=email).first()
                if user.is_superuser:
                    user = authenticate(email=email, password=password)
                    token = get_tokens_for_user(user)
                    return Response({"success": True, "status_code": 200, 'message': 'Login Success',
                                     "data": {"token": token}}, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "status_code": 400, "message": "user is not superuser!",
                                     "data": []}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": False, "status_code": 400, "message": "user does not exist!",
                                 "data": []}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "status_code": 400, "message": e.args[0],
                             "data": ["d"]}, status=status.HTTP_400_BAD_REQUEST)


class UserChangePasswrodView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        try:
            serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
            serializer.is_valid(raise_exception=True)
            return Response({
                "success": True, "status_code": 200, "message": "Password Reset Successfully",
                "data": []}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400,
                "message": e.args[0], "data": []}, status=status.HTTP_400_BAD_REQUEST)


class SendPasswordResetEmailView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = SendPasswordResetEmailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response({
                "success": True, "status_code": 200,
                'message': 'Password reset link send to the email please check your mail',
                "data": []}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": True, "status_code": 400,
                'message': e.args[0], "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetView(APIView):
    def post(self, request, uid, token, *args, **kwargs):
        try:
            serializer = UserPassowrdResetSerializer(data=request.data, context={'uid': uid, 'token': token})
            serializer.is_valid(raise_exception=True)
            return Response({
                "success": True, "status_code": 200, 'message': 'Password Reset Successfullly',
                "data": []}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": True, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileListView(viewsets.ViewSet):
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


class UserProfileUpdateView(viewsets.ViewSet):
    def patch(self, request, *args, **kwargs):
        try:
            user_id = User.objects.get(id=request.user.id)
            serializer = UserProfileSerializer(user_id, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success": True, "status_code": 200, 'message': 'User Profile Updated Successfull',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        try:
            user_id = User.objects.get(id=request.user.id)
            serializer = UserProfileSerializer(user_id, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success": True, "status_code": 200, 'message': 'User Profile Created Successfull',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserStatusView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileStatusUpdateViewSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_id = User.objects.get(id=request.user.id)
            # queryset = self.get_queryset(id=id)
            serializer = self.serializer_class(user_id)
            return Response({
                "success": True, "status_code": 200, 'message': 'User Status Retrieve Successfull',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
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
            user = User.objects.all()
            serializer = UserProfileStatusViewSerializer(user, many=True)
            return Response({
                "success": True, "status_code": 200, 'message': 'Users Profiles Listed Successfull',
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

    def partial_update(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            serializer = UserProfileStatusUpdateViewSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success": True, "status_code": 200, 'message': 'User Profiles Updated Successfull',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


class UserCollection(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            data = request.data
            data['create_by'] = request.user.id
            serializer = UserCollectionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success": True, "status_code": 200, 'message': 'User Collection Created Successfull',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            if pk is not None:
                collection = Collection.objects.get(id=pk)
                serializer = UserCollectionSerializer(collection)
                return Response({
                    "success": True, "status_code": 200, 'message': 'User Collection Retrieve Successfull',
                    "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        try:
            collection = Collection.objects.get(id=pk)
            serializer = UserCollectionSerializer(collection, data=request.data, partial=True)
            print(pk)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success": True, "status_code": 200, 'message': 'User Collection Update Successfull',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False, "status_code": 400, 'message': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)

