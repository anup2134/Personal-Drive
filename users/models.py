from django.db import models
from django.contrib.postgres.fields import ArrayField

class User(models.Model):
    email = models.CharField(max_length=256,blank=False,null=False,unique=True)
    f_name = models.CharField(max_length = 15)
    l_name = models.CharField(max_length = 15,blank=True)