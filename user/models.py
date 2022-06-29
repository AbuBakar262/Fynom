from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserWalletAddress(models.Model):
    wallet_address = models.CharField(max_length=50, blank=False, null=False, unique=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wallet_address


STATE_CHOICES = (
    ('Panding', 'Panding'),
    ('Approve', 'Approve'),
    ('Disapprove', 'Disapprove'),
    ('Suspend', 'Suspend'),
)


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='image/', null=True, blank=True)
    cover_picture = models.ImageField(upload_to='image/', null=True, blank=True)
    name = models.CharField(max_length=50, blank=False, null=False, unique=False)
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)  # use as display name
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)
    facebook_link = models.CharField(max_length=50, null=True, blank=True)
    twitter_link = models.CharField(max_length=50, null=True, blank=True)
    discord_link = models.CharField(max_length=50, null=True, blank=True)
    instagram_link = models.CharField(max_length=50, null=True, blank=True)
    reddit_link = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATE_CHOICES, default='Pending')
    status_reasons = models.TextField(blank=True, null=True)
    metamask_address = models.ForeignKey(UserWalletAddress, blank=True, null=True, related_name='user_in_wallet_address',
                                        on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username']


class NFTCategory(models.Model):
    category_name = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name


class NFTSubCategory(models.Model):
    sub_category_name = models.CharField(max_length=50, blank=True, null=True)
    main_category = models.ForeignKey(NFTCategory, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sub_category_name


class Collection(models.Model):
    logo_image = models.ImageField(upload_to='image/', null=True, blank=True)
    featured_image = models.ImageField(upload_to='image/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='image/', null=True, blank=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    website_url = models.CharField(max_length=80, null=True, blank=True)
    instagramURL = models.CharField(max_length=80, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
    nft_picture = models.ImageField(upload_to='image/', null=True, blank=True)
    teaser = models.FileField(upload_to='video/', null=True, blank=True)
    nft_title = models.CharField(max_length=50, blank=True, null=True)
    nft_collection = models.ForeignKey(Collection, blank=True, null=True, related_name='nft_collection',
                                      on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    nft_category = models.ForeignKey(NFTCategory, blank=True, null=True, related_name='nft_category',
                                    on_delete=models.CASCADE)
    royality = models.FloatField(blank=True, null=True)
    hash = models.CharField(max_length=50, blank=True, null=True)
    contract_id = models.CharField(max_length=50, blank=True, null=True)
    nft_owner = models.ForeignKey(UserWalletAddress, blank=True, null=True, related_name='nftOwner_wallet_address',
                                 on_delete=models.CASCADE)
    nft_status = models.CharField(max_length=50, choices=NFT_STATUS, default='Pending')
    status_remarks = models.TextField(blank=True, null=True)
    top_nft = models.BooleanField()
    nft_sell_type = models.CharField(max_length=50, choices=NFT_SELL_TYPE, default='Pending')
    fix_price = models.FloatField(blank=True, null=True)
    starting_rice = models.FloatField(blank=True, null=True)
    start_dateTime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)
    sold_status = models.CharField(max_length=50, choices=SOLD_STSTUS, default='Pending')
    sold_price = models.FloatField(blank=True, null=True)
    service_fee = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nft_title


class SupportingDocuments(models.Model):
    documents = models.FileField(upload_to='document/', null=True, blank=True)
    nft_create_info = models.ForeignKey(CreateNFT, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tags(models.Model):
    tag_title = models.CharField(max_length=50, blank=True, null=True)
    nft_create_info = models.ForeignKey(CreateNFT, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tag_title


class BidOnNFT(models.Model):
    nft_detail = models.ForeignKey(CreateNFT, blank=True, null=True, on_delete=models.CASCADE)
    bid_by = models.ForeignKey(UserWalletAddress, blank=True, null=True, on_delete=models.CASCADE)
    bid_price = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# class SoldNFTHistory(models.Model):
#
