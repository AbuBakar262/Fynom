from rest_framework import serializers
from phynom_admin.models import AboutUS



class AboutUsViewSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    class Meta:
        model = AboutUS
        fields = "__all__"