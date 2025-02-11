from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from users.models import EmailVerificationToken
from django.utils import timezone

@api_view(["GET"])
def verify_email(request,token):
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)
        if token_obj.expires_at < timezone.now():
            return Response({"message":"link expired"},status=status.HTTP_400_BAD_REQUEST)
        user = token_obj.user
        user.is_active = True
        user.save()
        token_obj.delete()

        return Response({"message":"email verified successfully"},status=status.HTTP_200_OK)
    except EmailVerificationToken.DoesNotExist:
        return Response({"message":"verification unsuccessful"},status=status.HTTP_404_NOT_FOUND)