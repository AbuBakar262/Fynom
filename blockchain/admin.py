from django.contrib import admin
# from models import UserWalletAddress, Collection, CreateNFT, SupportingDocuments, Tags, NFTCategory, \
#     NFTSubCategory, BidOnNFT
# Register your models here.
from blockchain.models import UserWalletAddress, Collection, NFT, SupportingDocuments, Tags, \
    NFTCategory, NFTSubCategory, BidOnNFT

admin.site.register(UserWalletAddress)
admin.site.register(Collection)
admin.site.register(NFT)
admin.site.register(SupportingDocuments)
admin.site.register(Tags)
admin.site.register(NFTCategory)
admin.site.register(NFTSubCategory)
admin.site.register(BidOnNFT)