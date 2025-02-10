from django.db import models
from users.models import User
from users.models import Group
from django.core.exceptions import ValidationError
from datetime import datetime

class Document(models.Model):
    ACCESS_CHOICE = [
        ("ANYONE", "Anyone"),
        ("SHARED", "Shared"),
        ("PRIVATE", "Private"),
    ]
    FILE_TYPES = [('img', 'Image'), ('pdf', 'PDF'), ('doc', 'Document')]
    url = models.URLField(blank=False,null=False)
    created_at = models.DateTimeField(default=datetime.now)
    obj_type = models.CharField(max_length=3,choices=FILE_TYPES)
    name = models.CharField(max_length = 50,blank=False,null=False)
    access = models.CharField(max_length=7,choices=ACCESS_CHOICE,default=ACCESS_CHOICE[2][0])
    users = models.ManyToManyField(User, blank=True, related_name="documents")
    groups = models.ManyToManyField(Group, blank=True, related_name="documents")

    def clean(self):
        if (not self.users.exists()) and (not self.groups.exists()):
            raise ValidationError("A document must be associated with at least one user or one group.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)