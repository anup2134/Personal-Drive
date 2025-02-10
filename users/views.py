from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User
from rest_framework import status
from rest_framework.routers import DefaultRouter

class RegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

router = DefaultRouter()
router.register("api/v1/user/register",RegisterViewSet,basename="user-register")
