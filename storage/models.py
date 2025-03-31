from django.db import models
from users.models import User
from users.models import Group
from django.core.exceptions import ValidationError
from django.utils import timezone


class Folder(models.Model):
    name = models.CharField(max_length=50,blank=False,null=False)
    user = models.ForeignKey(User, blank=True, null=True, related_name="folders",on_delete=models.CASCADE)
    group = models.ForeignKey(Group, blank=True,null=True, related_name="folders",on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')

    class Meta:
        unique_together = ('name', 'parent', 'group', 'user')

    def clean(self):
        if self.user_owner and self.group_owner:
            raise ValidationError("Only one of user_owner or group_owner should be set.")
        if not self.user_owner and not self.group_owner:
            raise ValidationError("One of user_owner or group_owner must be set.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)



class File(models.Model):
    ACCESS_CHOICE = [
        ("ANYONE", "Anyone"),
        ("PRIVATE", "Private"),
    ]
    url = models.URLField(blank=False,null=False)
    created_at = models.DateTimeField(default=timezone.now)
    obj_type = models.CharField(blank=False,null=False)
    name = models.CharField(max_length = 50,blank=False,null=False)
    access = models.CharField(max_length=7,choices=ACCESS_CHOICE,default=ACCESS_CHOICE[1][0])
    user = models.ForeignKey(User, blank=True, null=True, related_name="files",on_delete=models.CASCADE)
    group = models.ForeignKey(Group, blank=True,null=True, related_name="files",on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files', null=True, blank=True)

    class Meta:
        unique_together = ('name', 'folder', 'user', 'group')

    def clean(self):
        if self.user_owner and self.group_owner:
            raise ValidationError("Only one of user_owner or group_owner should be set.")
        if not self.user_owner and not self.group_owner:
            raise ValidationError("One of user_owner or group_owner must be set.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


