from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from users.models import EmailVerificationToken
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from storage.models import Folder

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

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
        tokens = get_tokens_for_user(user)
        response = Response({"message":"email verified successfully"},status=status.HTTP_200_OK)
        
        Folder.objects.create(name="root",user=user)

        response.set_cookie(
            key="access_token",
            value=tokens['access'],
            httponly=True,  
            secure=True,   
            samesite="None",
            max_age=15 * 60
        )

        response.set_cookie(
            key="refresh_token",
            value=tokens['refresh'],
            httponly=True,
            secure=True, 
            samesite="None",
            max_age=7 * 24 * 60 * 60
        )

        return response
    except EmailVerificationToken.DoesNotExist:
        return Response({"message":"invalid token"},status=status.HTTP_404_NOT_FOUND)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)