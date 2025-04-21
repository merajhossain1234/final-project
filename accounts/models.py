# Create your models here.
import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from uuid import uuid4

class ParentModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150,null=True,blank=True)
    last_name = models.CharField(max_length=150,null=True,blank=True)
    whatsapp_number = models.CharField(max_length=50,null=True,blank=True)
    is_trial = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    attributes = models.JSONField(default=dict, null=True, blank=True)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        unique_together = ['email', "username"]
        db_table = 'auth_user'