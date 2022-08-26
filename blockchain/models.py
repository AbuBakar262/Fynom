from django.db import models
from user.models import User


class UserWalletAddress(models.Model):
    wallet_address = models.CharField(max_length=250, blank=False, null=False, unique=True, default=None)
    user_wallet = models.ForeignKey(User, blank=True, null=True, related_name='user_in_wallet_address',
                                    on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wallet_address


class NFTCategory(models.Model):
    category_name = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.category_name:
            return self.category_name
        else:
            return str(self.id)


class NFTSubCategory(models.Model):
    sub_category_name = models.CharField(max_length=250, blank=True, null=True)
    main_category = models.ForeignKey(NFTCategory, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sub_category_name


class Collection(models.Model):
    logo_image = models.ImageField(upload_to='collection/', null=True, blank=True)
    featured_image = models.ImageField(upload_to='collection/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='collection/', null=True, blank=True)
    name = models.CharField(max_length=150, blank=False, null=False)
    website_url = models.CharField(max_length=250, null=True, blank=True)
    instagram_url = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    create_by = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    collection_category = models.ForeignKey(NFTCategory, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


NFT_STATUS = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Disapproved', 'Disapproved')
)

NFT_SELL_TYPE = (
    ('Fixed Price', 'Fixed Price'),
    ('Timed Auction', 'Timed Auction'),
)

SOLD_STATUS = (
    ('Sold', 'Sold'),
    ('Cancel', 'Cancel'),
)


class NFT(models.Model):
    thumbnail = models.ImageField(upload_to='nft/', null=True, blank=True)
    nft_picture = models.FileField(upload_to='nft/', null=True, blank=True)
    teaser = models.FileField(upload_to='nft/', null=True, blank=True)
    nft_title = models.CharField(max_length=150, blank=True, null=True)
    nft_collection = models.ForeignKey(Collection, blank=True, null=True, related_name='nft_collection',
                                       on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    nft_category = models.ForeignKey(NFTCategory, blank=True, null=True, related_name='nft_category',
                                     on_delete=models.CASCADE)
    royality = models.FloatField(blank=True, null=True)
    hash = models.CharField(max_length=250, blank=True, null=True)
    contract_id = models.CharField(max_length=250, blank=True, null=True)
    token_id = models.CharField(max_length=250, blank=True, null=True)
    commission = models.FloatField(blank=True, null=True)
    nft_creator = models.ForeignKey(UserWalletAddress, blank=True, null=True, related_name='nft_creator_in_create_nft',
                                  on_delete=models.CASCADE)
    nft_owner = models.ForeignKey(UserWalletAddress, blank=True, null=True, related_name='nft_owner_in_create_nft',
                                  on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, related_name='user_in_nft', on_delete=models.CASCADE)
    nft_status = models.CharField(max_length=50, choices=NFT_STATUS, default='Pending')
    nft_subject = models.CharField(max_length=250, blank=True, null=True)
    status_remarks = models.TextField(blank=True, null=True)
    top_nft = models.BooleanField(default=False)
    nft_sell_type = models.CharField(max_length=50, choices=NFT_SELL_TYPE)
    fix_price = models.FloatField(blank=True, null=True)
    starting_price = models.FloatField(blank=True, null=True)
    ending_price = models.FloatField(blank=True, null=True)
    start_dateTime = models.CharField(max_length=50, blank=True, null=True)
    end_datetime = models.CharField(max_length=50, blank=True, null=True)
    sold_price = models.FloatField(blank=True, null=True)
    service_fee = models.FloatField(blank=True, null=True)
    is_minted = models.BooleanField(default=False)
    is_listed = models.BooleanField(default=False)
    e_mail = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nft_title


class SupportingDocuments(models.Model):
    documents = models.FileField(upload_to='supporting_document/', null=True, blank=True)
    # documents = models.CharField(max_length=255, null=True, blank=True)
    nft_create_info = models.ForeignKey(NFT, blank=True, related_name='nft_in_supportingdocument', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tags(models.Model):
    tag_title = models.CharField(max_length=50, blank=True, null=True)
    nft_create_info = models.ManyToManyField(NFT, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tag_title


BID_STATUS = (
    ('Active', 'Active'),
    ('Closed', 'Closed'),
)
class BidOnNFT(models.Model):
    nft_detail = models.ForeignKey(NFT, blank=True, null=True, on_delete=models.CASCADE)
    seller_wallet = models.ForeignKey(UserWalletAddress, blank=True, null=True, related_name='seller_in_bidonnft',
                               on_delete=models.CASCADE)
    seller_profile = models.ForeignKey(User, blank=True, null=True, related_name='seller_user_in_bidonnft',
                                    on_delete=models.CASCADE)
    bidder_wallet = models.ForeignKey(UserWalletAddress, blank=True, null=True, on_delete=models.CASCADE)
    bidder_profile = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    bid_price = models.FloatField(blank=True, null=True)
    bid_datetime = models.CharField(max_length=50, blank=True, null=True)
    is_email = models.BooleanField(default=False)
    is_winner = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bid_status = models.CharField(max_length=50, choices=BID_STATUS, default='Active')
    is_claimed = models.BooleanField(default=False)
    bids_on_this_nft = models.BooleanField(default=True)



STATUS = (
    ('Sold', 'Sold'),
    ('Listed', 'Listed'),
)
class Transaction(models.Model):
    nft = models.ForeignKey(NFT, blank=True, null=True, related_name='nft_in_transaction', on_delete=models.CASCADE)
    nft_token_id = models.CharField(max_length=250, blank=True, null=True)
    seller = models.ForeignKey(UserWalletAddress, blank=True, null=True,  related_name='seller_in_transaction', on_delete=models.CASCADE)
    seller_user = models.ForeignKey(User, blank=True, null=True,  related_name='seller_user_in_transaction', on_delete=models.CASCADE)
    buyer = models.ForeignKey(UserWalletAddress, blank=True, null=True,  related_name='buyer_in_transaction', on_delete=models.CASCADE)
    buyer_user = models.ForeignKey(User, blank=True, null=True,  related_name='buyer_user_in_transaction', on_delete=models.CASCADE)
    sold_price = models.FloatField(blank=True, null=True)
    commission_percentage = models.FloatField(blank=True, null=True)
    commission_amount = models.FloatField(blank=True, null=True)
    category_of_nft = models.CharField(max_length=250, blank=True, null=True)
    nft_status = models.CharField(max_length=50, choices=STATUS, default='Sold')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return str(self.id)


class Commission(models.Model):
    set_commission = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)