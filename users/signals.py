from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import User, EmailVerificationToken
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=User)
def create_verification_token(sender, instance, created, **kwargs):
    if created:  
        token = str(uuid.uuid4())
        EmailVerificationToken.objects.create(
            user=instance,
            token=token,
            expires_at=timezone.now() + timedelta(hours=1)
        )
        try:
            send_mail(
                subject="Email Verification Personal Drive",
                # message=f"Welcome to Personal Drive.Click or copy the following link in your browser to verify you email.\nhttp://127.0.0.1:8000/api/v1/user/verify_email/{token}", # edit in prod to be a frontend app link
                message=f"Welcome to Personal Drive. Click or copy the following link in your browser to verify you email.\nhttp://localhost:5173/verify_email/?token={token}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[instance.email],
                fail_silently=False,
            )
        except Exception as e:
            print("smtp error: ",e)
        