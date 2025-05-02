from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import File
from utils.s3_utils import delete_from_s3
from pinecone import Pinecone
from django.conf import settings

@receiver(post_delete,sender=File)
def delete_file(sender, instance, **kwargs):
    try:
        pc = Pinecone(settings.PINECONE_API_KEY)
        index = pc.Index("personal-drive-hf")
        index.delete(delete_all=True, namespace=str(instance.id))
        delete_from_s3(f"uploads/{instance.id}")
    except:
        return
    return
    