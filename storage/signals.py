from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import File
from utils.s3_utils import delete_from_s3

@receiver(post_delete,sender=File)
def delete_file(sender, instance, **kwargs):
    # delete_from_s3(f"uploads/{instance.id}")
    pass
    