from rest_framework import serializers
from user.models import User
from blockchain.models import Collection, UserWalletAddress


class AdminLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password']


class AdminChangePasswordSerializer(serializers.Serializer):
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


class UserLoginSerializer(serializers.ModelSerializer):
    wallet_address = serializers.CharField(max_length=255)
    user_wallet = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="id", required=False)
    class Meta:
        model = UserWalletAddress
        # fields = '__all__'
        fields = ["id", "wallet_address", "user_wallet"]


class UserProfileDetailsViewSerializer(serializers.ModelSerializer):
    user_address = serializers.SerializerMethodField('get_metamask')

    class Meta:
        model = User
        fields = ["id", "profile_picture", "name", "username", "user_address", "created_at", "status"]

    def get_metamask(self, obj):
        try:
            wallet = UserWalletAddress.objects.filter(user_wallet__id=obj.id).first()
            if wallet:
                return wallet.wallet_address
        except:
            return None


class UserProfileSerializer(serializers.ModelSerializer):
    # user_in_wallet_address = UserProfileDetailsViewSerializer(many=False)
    user_wallet_address = serializers.SerializerMethodField('get_metamask')

    class Meta:
        model = User
        fields = ["id", "user_wallet_address", "profile_picture", "cover_picture", "name", "username", "email",
                  "facebook_link", "twitter_link", "discord_link", "instagram_link", "reddit_link", "status"]
        # fields = "__all__"
    def get_metamask(self, obj):
        try:
            wallet = UserWalletAddress.objects.filter(user_wallet__id=obj.id).first()
            if wallet:
                return wallet.wallet_address
        except:
            return None



class UserProfileStatusUpdateViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "status", "status_reasons"]


class UserCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "logo_image", "featured_image", "cover_image", "name", "website_url", "instagram_url",
                  "collection_category", "create_by"]


class TermsAndPoliciesViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "terms_policies"]