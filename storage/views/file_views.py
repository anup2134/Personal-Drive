from rest_framework.views import APIView 
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed,NotFound
from rest_framework.decorators import api_view,authentication_classes

from django.conf import settings

from users.auth_class import AccessTokenAuthentication
from ..models import File
from ..tasks.doc_parsing import process_text
from utils.upload_to_s3 import upload_to_s3

import os

def save_uploaded_file_temporarily(uploaded_file,file_id):
    if not uploaded_file:
        return
    try:
        os.makedirs("temp_files", exist_ok=True)
        if '.' in uploaded_file.name:
            file_type = uploaded_file.name.split('.')[-1]
        else:
            file_type = ""
        filename = os.path.basename(f"{str(file_id)}.{file_type}")
        destination_path = os.path.join("temp_files", filename)

        with open(destination_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        return destination_path
    
    except Exception as e:
        print(f"Error saving file: {e}")
        return


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [AccessTokenAuthentication]
    def post(self, request):
        uploaded_file = request.FILES.get('file')
        folder_name = request.data.get("folder_name","root")

        if not uploaded_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        if not user:
            raise AuthenticationFailed("no user found")
        
        folder = user.folders.filter(name=folder_name).first()
        if not folder:
            raise NotFound("Folder not found.")

        file_size = uploaded_file.size / (1024 * 1024)
        file = File.objects.create(
            name=uploaded_file.name,url="https://www.dummyurl.com",obj_type=uploaded_file.content_type,user=user,folder=folder
        )
        file_id = file.id

        user.limit = user.limit + file_size

        ALLOWED_TYPES = {
            "application/pdf",  # PDF files
            "application/msword",  # DOC (old Word format)
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX (new Word format)
            "text/plain",  # Plain text files
        }
        
        if uploaded_file.content_type in ALLOWED_TYPES:
            path = save_uploaded_file_temporarily(uploaded_file,file_id)
            process_text.delay(path,file_id,uploaded_file.content_type)
        else:
            file.url = upload_to_s3(file_id,uploaded_file,uploaded_file.content_type)
            file.save()

        try:
            user.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        

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
        files = request.user.files.all()
        files = [{
                    "url":file.url,
                    "name":file.name,
                    'id':file.id,
                    "user_id":file.user.id,
                    "group_id": "no group" if not file.group else file.group.id,
                    "folder_id":file.folder.id
                } for file in files]
        
        response = Response({'all documents':files},status=status.HTTP_200_OK)
        response.set_cookie(
            key="access_token",
            value=request.COOKIES.get("access_token"),
            httponly=True,
            secure=True,
            samesite="None",
            max_age=15 * 60
        )
        return response

    def delete(self,request):
        if not settings.DEBUG:
            return Response({"message": "This endpoint is disabled in production"}, status=status.HTTP_403_FORBIDDEN)

        request.user.files.all().delete()
        request.user.limit = 0
        request.user.save()
        response = Response({"message":"all docs deleted successfully"},status=status.HTTP_204_NO_CONTENT)
        response.set_cookie(
            key="access_token",
            value=request.COOKIES.get("access_token"),
            httponly=True,
            secure=True,
            samesite="None",
            max_age=15 * 60
        )
        return response
    

@api_view(["GET"])
@authentication_classes([AccessTokenAuthentication]) 
def get_folders(request):
    user = request.user
    folders = user.folders.all()
    folder_names = [folder.name for folder in folders]

    response = Response(folder_names)
    response.set_cookie(
        key="access_token",
        value=request.COOKIES.get("access_token"),
        httponly=True,
        secure=True,
        samesite="None",
        max_age=15 * 60
    )

    return response