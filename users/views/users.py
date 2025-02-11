from rest_framework import viewsets
from rest_framework.response import Response
from ..serializers import UserSerializer
from ..models import User
from rest_framework import status
from rest_framework.routers import DefaultRouter
from django.conf import settings
from rest_framework.decorators import api_view

class RegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({"message": "user registered successfully"}, status=status.HTTP_201_CREATED)
    
    # disabled in production
    def list(self, request):
        if not settings.DEBUG: 
            return Response({"message": "This endpoint is disabled in production"}, status=status.HTTP_403_FORBIDDEN)
        
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# disabled in production
@api_view(["DELETE"])
def destroy(request):
    if not settings.DEBUG:  
        return Response({"message": "This endpoint is disabled in production"}, status=status.HTTP_403_FORBIDDEN)
    email = request.query_params.get("email")
    # print(email)
    if not email:
        return Response({"message":"failed to delete"},status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
        user.delete()
        return Response({"message":"user deleted successfully"},status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({"message": "user not found"}, status=status.HTTP_404_NOT_FOUND)

router = DefaultRouter()
router.register("api/v1/user/register",RegisterViewSet,basename="user-register")
