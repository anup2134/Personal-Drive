from django.utils import timezone
from datetime import timedelta
import uuid
from ..models import EmailVerificationToken,User
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task

@shared_task
def send_email(user_id):
    user = User.objects.get(id=user_id)

    if not user:
        raise ValueError("No user found")
    token = str(uuid.uuid4())
    EmailVerificationToken.objects.create(
        user=user,
        token=token,
        expires_at=timezone.now() + timedelta(hours=1)
    )
    try:
        send_mail(
            subject="Email Verification Personal Drive",
            message=f"Welcome to Personal Drive. Click or copy the following link in your browser to verify you email.\nhttp://localhost:5173/verify_email/?token={token}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        print("smtp error: ",e)