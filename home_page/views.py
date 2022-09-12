from django.shortcuts import render
from django.db.models import Q, Count
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F, Value, CharField
import os
from datetime import datetime, timedelta
from decimal import Decimal
from backend.pagination import CustomPageNumberPagination
from blockchain.serializers import *
from blockchain.models import *
from blockchain.utils import validateEmail, scientific_to_float
from user.custom_permissions import IsEmailExist, IsApprovedUser
from user.models import User
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import viewsets
from user.serializers import UserCollectionSerializer
from user.utils import Utill
import boto3
from backend.settings import *
import calendar
import datetime




