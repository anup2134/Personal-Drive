from rest_framework import serializers
from .models import File,Folder
from users.serializers import FileOwnerSerializer

class FileSerializer(serializers.ModelSerializer):    
    type = serializers.CharField(source="obj_type")
    is_shared = serializers.BooleanField(read_only=True)
    url = serializers.CharField(read_only=True)

    class Meta:
        model = File
        fields = ["name", "type", "created_at", "size", "id", "is_shared", "url"]
    
class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['name', 'id', 'created_at']

class SharedFileSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="obj_type")
    is_shared = serializers.BooleanField(read_only=True)
    url = serializers.CharField(read_only=True)
    owner_data = FileOwnerSerializer(source='owner', read_only=True)

    class Meta:
        model = File
        fields = ["name", "type", "created_at", "size", "id", "is_shared", "url", "owner_data"]
