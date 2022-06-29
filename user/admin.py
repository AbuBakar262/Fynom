from django.contrib import admin
from .models import User, UserWalletAddress, Collection, CreateNFT, SupportingDocuments, Tags, NFTCategory, \
    NFTSubCategory, BidOnNFT

# Register your models here.

admin.site.register(User)
admin.site.register(UserWalletAddress)
admin.site.register(Collection)
admin.site.register(CreateNFT)
admin.site.register(SupportingDocuments)
admin.site.register(Tags)
admin.site.register(NFTCategory)
admin.site.register(NFTSubCategory)
admin.site.register(BidOnNFT)

