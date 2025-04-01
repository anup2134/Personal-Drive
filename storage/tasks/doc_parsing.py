from celery import shared_task
import os

from django.conf import settings

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings

from utils.upload_to_s3 import upload_to_s3
from ..models import File

@shared_task
def process_text(path, file_id,content_type):
    try:
        file = File.objects.get(pk=file_id)
        # file.url = upload_to_s3(file_id,path,content_type)
        # file.save()
        loader = PyPDFLoader(path)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True
        )
        all_splits = text_splitter.split_documents(docs)
        if not settings.PINECONE_API_KEY:
            raise ValueError("Pinecone API key not found")

        index_name = "personal-drive"
        embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        PineconeVectorStore.from_documents(
            documents=all_splits,
            embedding=embeddings,
            index_name=index_name,
            namespace=str(file_id),
        )

        os.remove(path)
    except Exception as e:
        os.remove(path)
        print(f"Error in Celery task: {str(e)}")
