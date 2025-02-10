from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email).lower()
        user = self.model(email=email, auth_type=User.LOCAL, **extra_fields)
        
        if password:
            user.set_password(password)  # Hash password
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    LOCAL = "local"
    GOOGLE = "google"

    AUTH_CHOICES = [
        (LOCAL, "Local Authentication"),
        (GOOGLE, "Google OAuth2.0"),
    ]
    email = models.EmailField(unique=True)
    f_name = models.CharField(max_length=20,blank=False,null=False)
    l_name = models.CharField(max_length=20,blank=True)
    auth_type = models.CharField(max_length=10, choices=AUTH_CHOICES,default=LOCAL) 
    password = models.CharField(max_length=128, blank=True, null=True)  # Only for local users
    google_id = models.CharField(max_length=255, unique=True, blank=True, null=True) # Only for google users
    is_active = models.BooleanField(default=True)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['f_name']


class Group(models.Model):
    owner = models.ForeignKey(User,null=False,on_delete=models.CASCADE)
    name = models.CharField(max_length=20,blank=False,null=False)
    admins = models.ManyToManyField(User, blank=True, related_name="admin_groups")
    users = models.ManyToManyField(User, blank=True, related_name="user_groups")