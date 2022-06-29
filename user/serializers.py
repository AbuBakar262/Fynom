from rest_framework.exceptions import ValidationError

from user.utils import *
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import serializers
from user.models import User, Collection


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password']


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password1 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        # print(user.password)
        old_password = attrs.get('old_password')
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if not user.check_password(old_password):
            raise serializers.ValidationError("Old Password does't match")
        if password1 != password2:
            raise serializers.ValidationError("Password and Confirm Password does't match")
        user.set_password(password1)
        user.save()
        return attrs


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=225)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://website.url/api/user/reset/' + uid + '/' + token + '/'
            # send email
            body = "Click following link to reset your password " + link
            data = {
                'subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email
            }
            Utill.send_email(data)
            return attrs
        else:
            raise ValidationError("You are not registerd user")


class UserPassowrdResetSerializer(serializers.Serializer):
    password1 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password1', 'password2']

    def validate(self, attrs):
        try:
            password1 = attrs.get('password1')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password1 != password2:
                raise serializers.ValidationError("Password and Confirm Password does't match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationError("token is not valid ro expire")
            user.set_password(password1)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise ValidationError("token is not valid ro expire")



class UserProfileSerializer(serializers.ModelSerializer):
    # metamaskAddress = UserWalletAddressSerializer(many=False)
    metamask = serializers.SerializerMethodField('get_metamask')

    class Meta:
        model = User
        fields = ["id", "profile_picture", "cover_picture", "name", "username", "email", "facebook_link", "twitter_link",
                  "discord_link", "instagram_link", "reddit_link", "metamask"]
        # fields = "__all__"

    def get_metamask(self, obj):
        try:
            return obj.metamaskAddress.walletAddress
        except:
            return None


class UserStatusViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "status"]


class UserProfileStatusViewSerializer(serializers.ModelSerializer):
    wallet_addres = serializers.SerializerMethodField('get_metamask')

    class Meta:
        model = User
        fields = ["id", "name", "username", "wallet_addres", "created_at", "status"]

    def get_metamask(self, obj):
        try:
            return obj.metamask_address.wallet_address
        except:
            return None


class UserProfileStatusUpdateViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "status", "status_reasons"]

    # def validate_status(self, attrs):
    #     if attrs == 'Disapprove' or attrs == 'Suspend':
    #         reason


class UserCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "name"]
