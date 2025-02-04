import tempfile
import os
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.routers import DefaultRouter
from langchain_community.document_loaders import PyPDFLoader

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        name = request.data.get('name')
        if not uploaded_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        file_type = uploaded_file.content_type
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        loader = PyPDFLoader(temp_file_path)
        docs = loader.load() 

        return Response({'file_name': uploaded_file.name,'file_type':file_type,'name':name}, status=status.HTTP_201_CREATED)

router = DefaultRouter()
router.register('upload',FileUploadView, basename='file-upload')