import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.utils import timezone
from datetime import timedelta

class UserManager(BaseUserManager):
    def create_user(self, email,auth_type, password=None,**extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email).lower()
        user = self.model(email=email, auth_type=User.LOCAL if auth_type == 'local' else User.GOOGLE, **extra_fields)

        if password and auth_type == 'local':
            user.set_password(password)
        elif not password and auth_type == 'google':
            user.set_unusable_password()
            user.is_active = True
        else:
            raise ValueError("password error")
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    LOCAL = "local"
    GOOGLE = "google"

    AUTH_CHOICES = [
        (LOCAL, "Local Authentication"),
        (GOOGLE, "Google OAuth2.0"),
    ]
    email = models.EmailField(unique=True,db_index=True)
    f_name = models.CharField(max_length=20,blank=False,null=False)
    l_name = models.CharField(max_length=20,blank=True)
    auth_type = models.CharField(max_length=10, choices=AUTH_CHOICES,default=LOCAL)
    password = models.CharField(max_length=128, blank=True, null=True)
    picture = models.URLField(blank=True,null=True)
    is_active = models.BooleanField(default=False)
    limit = models.FloatField(default=0.0)
    @property
    def full_name(self):
        return self.f_name + ((" " + self.l_name) if self.l_name != "" else "")

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['f_name']

class Group(models.Model):
    owner = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name="group_owner")
    name = models.CharField(max_length=20,blank=False,null=False)
    admins = models.ManyToManyField(User, blank=True, related_name="group_admin")
    users = models.ManyToManyField(User, blank=True, related_name="group_users")

def one_hour_from_now():
    return timezone.now() + timedelta(hours=1)

class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True, default=uuid.uuid4,db_index=True)
    expires_at = models.DateTimeField(default=one_hour_from_now)