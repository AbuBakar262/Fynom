from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


STATE_CHOICES = (
    ('Not Requested', 'Not Requested'),
    ('Pending', 'Pending'),
    ('Approve', 'Approve'),
    ('Disapprove', 'Disapprove'),
    ('Suspend', 'Suspend'),
)


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile/', null=True, blank=True)
    cover_picture = models.ImageField(upload_to='profile/', null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True, unique=False)
    username = models.CharField(max_length=50, null=True, blank=True, unique=True)  # use as display name
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    password = models.CharField(_('password'), max_length=128, blank=True, null=True)
    facebook_link = models.CharField(max_length=50, null=True, blank=True)
    twitter_link = models.CharField(max_length=50, null=True, blank=True)
    discord_link = models.CharField(max_length=50, null=True, blank=True)
    instagram_link = models.CharField(max_length=50, null=True, blank=True)
    reddit_link = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATE_CHOICES, default='Not Requested')
    status_reasons = models.TextField(blank=True, null=True)
    terms_policies = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.id)



