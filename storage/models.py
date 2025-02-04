from django.db import models
from users.models import User
from datetime import datetime

class Document(models.Model):
    FILE_TYPES = [('img', 'Image'), ('pdf', 'PDF'), ('doc', 'Document')]
    url = models.TextField()
    created_at = models.DateTimeField(default=datetime.now,null=True)
    obj_type = models.CharField(max_length=3,choices=FILE_TYPES)
    name = models.CharField(max_length = 50,blank=False,null=False)
    owner = models.ForeignKey(User,null=False,on_delete=models.DO_NOTHING)
