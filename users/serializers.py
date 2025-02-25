from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8)
    
    class Meta:
        model = User
        fields = ["email", "f_name", "l_name", "password"]
    
    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            f_name=validated_data["f_name"],
            auth_type="local",
            l_name= "" if "l_name" not in validated_data else validated_data['l_name']
        )

class GoogleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "f_name", "l_name", "picture"]
    
    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            f_name=validated_data["f_name"],
            auth_type="google",
            picture="" if "picture" not in validated_data else validated_data['picture'],
            l_name="" if "l_name" not in validated_data else validated_data['l_name']
        )