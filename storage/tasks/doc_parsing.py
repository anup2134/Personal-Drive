from celery import shared_task
import os

from dotenv import load_dotenv
load_dotenv()

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

from utils.file_parser import parse_file

@shared_task
def process_text(path, file_id,content_type):
    try:
        docs = parse_file(path,content_type)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1600, chunk_overlap=200, add_start_index=True
        )
        all_splits = text_splitter.split_documents(docs)

        if not os.getenv("PINECONE_API_KEY"):
            raise ValueError("Pinecone API key not found")
        if not os.getenv("HF_TOKEN"):
            raise ValueError("HF_TOKEN key not asdfasdfasdf found")
        
        index_name = "personal-drive-hf"
        embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=os.getenv("HF_TOKEN"),
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
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
