from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .tasks.send_email import send_email
from .models import User,Group
from storage.models import Folder

@receiver(post_save, sender=User)
def create_verification_token(sender, instance, created, **kwargs):
    if instance.auth_type == User.GOOGLE and created:
        Folder.objects.create(
            name="root",
            owner=instance
        )
        return
    if created:
        send_email.delay(instance.id)

@receiver(pre_save, sender=User)
def before_user_update(sender, instance, **kwargs):
    if instance.limit > 100:
        raise Exception("You have exceeded the storage limit.")
    
@receiver(post_save,sender=Group)
def create_root_folder(sender,instance,created,**kwargs):
    if created:
        group = Group.objects.get(pk=instance.id)
        Folder.objects.create(
            name="root",
            group=group
        )

        