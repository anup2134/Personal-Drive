from rest_framework.views import APIView 
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed

from django.utils import timezone
from django.conf import settings

from users.auth_class import AccessTokenAuthentication
from ..models import File
from ..tasks.doc_parsing import process_text

import boto3
import os

def upload_to_s3(file):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    s3_key = f"uploads/{file.name}"
    s3_client.upload_fileobj(
        file, 
        settings.AWS_STORAGE_BUCKET_NAME, 
        s3_key,
        ExtraArgs={"ContentType": file.content_type}
    )
    
    file_url = f"{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_key}"
    return file_url

def save_uploaded_file_temporarily(uploaded_file):
    if not uploaded_file:
        return
    try:
        os.makedirs("temp_files", exist_ok=True)
        filename = os.path.basename(uploaded_file.name)
        destination_path = os.path.join("temp_files", filename)

        with open(destination_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        return destination_path
    
    except Exception as e:
        print(f"Error saving file: {e}")
        return None


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [AccessTokenAuthentication]
    def post(self, request):
        uploaded_file = request.FILES.get('file')
            
        if not uploaded_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        if not user:
            raise AuthenticationFailed("no user found")
        
        
        file_size = uploaded_file.size / (1024 * 1024)
        file = File.objects.create(
            name=uploaded_file.name,url="https://www.dummyurl.com",obj_type=uploaded_file.content_type,user=user
        )

        user.limit = user.limit + file_size

        ALLOWED_TYPES = {
            "application/pdf",  # PDF files
            "application/msword",  # DOC (old Word format)
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX (new Word format)
            "text/plain",  # Plain text files
        }
        
        if uploaded_file.content_type in ALLOWED_TYPES:
            path = save_uploaded_file_temporarily(uploaded_file)
            print(path)
        else:
            upload_to_s3(uploaded_file)
        try:
            user.save() 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        file.save()
        

        response = Response({'file_name': uploaded_file.name,'file type':uploaded_file.content_type}, status=status.HTTP_201_CREATED)
        response.set_cookie(
            key="access_token",
            value=request.COOKIES.get("access_token"),
            httponly=True,
            secure=True,
            samesite="None",
            max_age=15 * 60
        )
        return response
    
    def get(self,request):
        if not settings.DEBUG:  
            return Response({"message": "This endpoint is disabled in production"}, status=status.HTTP_403_FORBIDDEN)
        files = File.objects.all()
        files = [{"url":doc.url,"user":doc.user.email} for doc in files]
        
        return Response({'all documents':files},status=status.HTTP_200_OK)

    def delete(self,request):
        if not settings.DEBUG:
            return Response({"message": "This endpoint is disabled in production"}, status=status.HTTP_403_FORBIDDEN)

        File.objects.all().delete()
        return Response({"message":"all docs deleted successfully"},status=status.HTTP_204_NO_CONTENT)