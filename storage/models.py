from django.db import models
from users.models import User
from users.models import Group
from django.core.exceptions import ValidationError
from django.utils import timezone


class Folder(models.Model):
    name = models.CharField(max_length=50,blank=False,null=False)
    owner = models.ForeignKey(User, blank=True, null=True, related_name="folders",on_delete=models.CASCADE)
    shared = models.ManyToManyField(User, related_name="shared_folders", blank=True)
    group = models.ForeignKey(Group, blank=True,null=True, related_name="folders",on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'parent', 'owner'], name='unique_name_parent_user'),
            models.UniqueConstraint(fields=['name', 'parent', 'group'], name='unique_name_parent_group'),
        ]

    def clean(self):
        if self.owner and self.group:
            raise ValidationError("Only one of user_owner or group_owner should be set.")
        if not self.owner and not self.group:
            raise ValidationError("One of user_owner or group_owner must be set.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)



class File(models.Model):
    ACCESS_CHOICE = [
        ("ANYONE", "Anyone"),
        ("PRIVATE", "Private"),
    ]

    created_at = models.DateTimeField(default=timezone.now)
    obj_type = models.CharField(blank=False,null=False)
    name = models.CharField(max_length = 50,blank=False,null=False)
    access = models.CharField(max_length=7,choices=ACCESS_CHOICE,default=ACCESS_CHOICE[1][0])
    owner = models.ForeignKey(User, blank=True, null=True, related_name="files",on_delete=models.CASCADE)
    shared = models.ManyToManyField(User, related_name="shared_files", blank=True)
    group = models.ForeignKey(Group, blank=True,null=True, related_name="files",on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files', null=True,blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'folder', 'owner'], name='unique_name_folder_user'),
            models.UniqueConstraint(fields=['name', 'folder', 'group'], name='unique_name_folder_group'),
        ]

    def clean(self):
        if self.owner and self.group:
            raise ValidationError("Only one of user or group should be set.")
        if not self.owner and not self.group:
            raise ValidationError("One of user or group must be set.")
        if not self.folder:
            raise ValidationError("File must belong to a folder.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


