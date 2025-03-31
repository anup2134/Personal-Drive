import tempfile
from celery import shared_task
from django.conf import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_community.embeddings.ollama import OllamaEmbeddings
from pinecone import Pinecone

@shared_task
def process_text(file_path, name):
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True
        )
        all_splits = text_splitter.split_documents(docs)

        for split in all_splits:
            split.metadata['source'] = name

        if not settings.PINECONE_API_KEY:
            raise ValueError("Pinecone API key not found")


        pc = Pinecone(settings.PINECONE_API_KEY)
        index = pc.Index('personal-drive')

        embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        vector_store = PineconeVectorStore(embedding=embeddings, index=index)
        vector_store.add_documents(documents=all_splits)

        doc = File.objects.get(id=doc_id)
        doc.processed = True
        doc.save()

    except Exception as e:
        print(f"Error in Celery task: {str(e)}")
