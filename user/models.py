from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserWalletAddress(models.Model):
    walletAddress = models.CharField(max_length=50, blank=False, null=False, unique=True, default=None)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.walletAddress


STATE_CHOICES = (
    ('Panding', 'Panding'),
    ('Approve', 'Approve'),
    ('Disapprove', 'Disapprove'),
    ('Suspend', 'Suspend'),
)


class User(AbstractUser):
    profilePicture = models.ImageField(upload_to='image/', null=True, blank=True)
    coverPicture = models.ImageField(upload_to='image/', null=True, blank=True)
    name = models.CharField(max_length=50, blank=False, null=False, unique=False)
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)  # use as display name
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)
    facebookLink = models.URLField(null=True, blank=True)
    twitterLink = models.URLField(null=True, blank=True)
    discordLink = models.URLField(null=True, blank=True)
    instagramLink = models.URLField(null=True, blank=True)
    redditLink = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATE_CHOICES, default='Pending')
    statusReasons = models.TextField(blank=True, null=True)
    metamaskAddress = models.ForeignKey(UserWalletAddress, blank=True, null=True, related_name='wallet_address',
                                        on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username']


class NFTCategory(models.Model):
    categoryName = models.CharField(max_length=50, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.categoryName


class NFTSubCategory(models.Model):
    subCategoryName = models.CharField(max_length=50, blank=True, null=True)
    mainCategory = models.ForeignKey(NFTCategory, blank=True, null=True, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subCategoryName


class Collection(models.Model):
    logoImage = models.ImageField(upload_to='image/', null=True, blank=True)
    featuredImage = models.ImageField(upload_to='image/', null=True, blank=True)
    coverImage = models.ImageField(upload_to='image/', null=True, blank=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    websiteURL = models.URLField(null=True, blank=True)
    instagramURL = models.URLField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    madeBy = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    collectionCategory = models.ForeignKey(NFTCategory, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


NFT_STATUS = (
    ('Panding', 'Panding'),
    ('Approve', 'Approve'),
    ('Disapprove', 'Disapprove'),
    ('Suspend', 'Suspend'),
)

NFT_SELL_TYPE = (
    ('Fixed Price', 'Fixed Price'),
    ('Timed Auction', 'Timed Auction'),
)

SOLD_STSTUS = (
    ('Listed', 'Listed'),
    ('Sold', 'Sold'),
    ('Cancel', 'Cancel'),
)


class CreateNFT(models.Model):
    thumbnail = models.ImageField(upload_to='image/', null=True, blank=True)
    nftPicture = models.ImageField(upload_to='image/', null=True, blank=True)
    teaser = models.FileField(upload_to='video/', null=True, blank=True)
    nftTitle = models.CharField(max_length=50, blank=True, null=True)
    nftCollection = models.ForeignKey(Collection, blank=True, null=True, related_name='nft_collection',
                                      on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    nftCategory = models.ForeignKey(NFTCategory, blank=True, null=True, related_name='nft_category',
                                    on_delete=models.CASCADE)
    royality = models.FloatField(blank=True, null=True)
    hash = models.CharField(max_length=50, blank=True, null=True)
    contractID = models.CharField(max_length=50, blank=True, null=True)
    nftOwner = models.ForeignKey(UserWalletAddress, blank=True, null=True, related_name='nftOwner_wallet_address',
                                 on_delete=models.CASCADE)
    nftStatus = models.CharField(max_length=50, choices=NFT_STATUS, default='Pending')
    statusRemarks = models.TextField(blank=True, null=True)
    topNFT = models.BooleanField()
    nftSellType = models.CharField(max_length=50, choices=NFT_SELL_TYPE, default='Pending')
    fixPrice = models.FloatField(blank=True, null=True)
    startingPrice = models.FloatField(blank=True, null=True)
    startDateTime = models.DateTimeField(blank=True, null=True)
    endDateTime = models.DateTimeField(blank=True, null=True)
    soldStatus = models.CharField(max_length=50, choices=SOLD_STSTUS, default='Pending')
    soldPrice = models.FloatField(blank=True, null=True)
    serviceFee = models.FloatField(blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nftTitle


class SupportingDocuments(models.Model):
    documents = models.FileField(upload_to='document/', null=True, blank=True)
    nftCreateInfo = models.ForeignKey(CreateNFT, blank=True, null=True, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class Tags(models.Model):
    tagTitle = models.CharField(max_length=50, blank=True, null=True)
    nftCreateInfo = models.ForeignKey(CreateNFT, blank=True, null=True, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tagTitle


class BidOnNFT(models.Model):
    nftDetail = models.ForeignKey(CreateNFT, blank=True, null=True, on_delete=models.CASCADE)
    bidBy = models.ForeignKey(UserWalletAddress, blank=True, null=True, on_delete=models.CASCADE)
    bidPrice = models.FloatField(blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


# class SoldNFTHistory(models.Model):
#
