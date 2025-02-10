import tempfile
from django.conf import settings

from rest_framework.views import APIView 
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings
from pinecone import Pinecone


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
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True
        )
        all_splits = text_splitter.split_documents(docs)

        for split in all_splits:
            split.metadata['source'] = name

        if not settings.PINECONE_API_KEY:
            raise ValueError("Pinecone api key not found")
        
        pc = Pinecone(settings.PINECONE_API_KEY)
        index = pc.Index('personal-drive')

        embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        vector_store = PineconeVectorStore(embedding=embeddings, index=index)
        vector_store.add_documents(documents=all_splits)

        return Response({'file_name': uploaded_file.name,'file_type':file_type,'name':name}, status=status.HTTP_201_CREATED)
