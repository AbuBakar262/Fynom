from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


STATE_CHOICES = (
    ('Pending', 'Pending'),
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
    # metamask_address = models.ForeignKey(UserWalletAddress, blank=True, null=True, related_name='user_in_wallet_address',
    #                                     on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username']



