from rest_framework import viewsets
from rest_framework.response import Response
from ..serializers import UserSerializer,GoogleUserSerializer
from ..models import User
from rest_framework import status
from rest_framework.routers import DefaultRouter
from django.conf import settings
from rest_framework.decorators import api_view,authentication_classes
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from ..auth_class import AccessTokenAuthentication

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class RegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            if 'email' in serializer.errors:
                return Response({"message":"user already exists"},status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({"message": "user registered successfully"}, status=status.HTTP_201_CREATED)
    
    # disabled in production
    def list(self, request):
        if not settings.DEBUG: 
            return Response({"message": "This endpoint is disabled in production"}, status=status.HTTP_403_FORBIDDEN)
        
        users = User.objects.all()
        # print(request.user)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

router = DefaultRouter()
router.register("api/v1/user/register",RegisterViewSet,basename="user-register")

# disabled in production
@api_view(["DELETE"])
def destroy(request):
    if not settings.DEBUG:  
        return Response({"message": "This endpoint is disabled in production"}, status=status.HTTP_403_FORBIDDEN)
    # print(email)

    User.objects.all().delete()
    return Response({"message":"all users deleted successfully"},status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def get_verified_users(request):
    if not settings.DEBUG:  
        return Response({"message": "This endpoint is disabled in production"}, status=status.HTTP_403_FORBIDDEN)
    verified = User.objects.filter(is_active=True)
    verified_users = [{"password": user.password, "email": user.email,"limit":user.limit,"id":user.id} for user in verified]
    # print(verified_users)
    return Response({'verified users':verified_users},status=status.HTTP_200_OK)

@api_view(["GET"])
def get_users_id(request):
    if not settings.DEBUG:  
        return Response({"message": "This endpoint is disabled in production"}, status=status.HTTP_403_FORBIDDEN)
    users = User.objects.all()
    user_list = [{"id": user.id, "email": user.email} for user in users]
    
    return Response({'users':user_list},status=status.HTTP_200_OK)

@api_view(["POST"])
def google_user_signup(request):
    if 'access_token' not in request.data:
        return Response({"message":"invalid token"},status=status.HTTP_400_BAD_REQUEST)
    access_token = request.data['access_token']
    user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
    response = requests.get(user_info_url)
    if response.status_code != 200:
        return Response({"message":"google auth failed"},status=status.HTTP_400_BAD_REQUEST)
    response = response.json()
    data = {
        "email": response["email"],
        "f_name": response["given_name"],
        "l_name": response["family_name"],
        "picture": response["picture"],
    }
    serializer = GoogleUserSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.save()
    tokens = get_tokens_for_user(user)
    response = Response({"message":"google auth successful"},status=status.HTTP_200_OK)
    response.set_cookie(
        key="access_token",
        value=tokens['access'],
        httponly=True,  
        secure=True,   # set true in production 
        samesite="None",
        max_age=15 * 60
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens['refresh'],
        httponly=True,
        secure=True,   #set true in production
        samesite="None",
        max_age=7 * 24 * 60 * 60
    )

    return response


@api_view(["GET"])
@authentication_classes([AccessTokenAuthentication])
def get_user(request):
    if not request.user:
        return Response({"message":"not user found"},status=status.HTTP_204_NO_CONTENT)
    user  = request.user
    user = {
        "f_name":user.f_name,
        "l_name":user.l_name,
        "id":user.id,
        "email":user.email,
        "picture":user.picture,
        "limit":user.limit
    }

    response = Response({"user":user})
    response.set_cookie(
        key="access_token",
        value=request.COOKIES.get("access_token"),
        httponly=True,
        secure=True,
        samesite="None",
        max_age=15 * 60
    )

    return response

@api_view(["POST"])
@authentication_classes([AccessTokenAuthentication])
def logout(request):
    response = Response({"message":"user logged out successfully"},status=status.HTTP_204_NO_CONTENT)
    response.set_cookie(
        key='access_token',
        value='',
        httponly=True,
        secure=True,
        samesite="None",
        max_age=0
    )
    response.set_cookie(
        key='refresh_token',
        value='',
        httponly=True,
        secure=True,
        samesite="None",
        max_age=0
    )
    return response