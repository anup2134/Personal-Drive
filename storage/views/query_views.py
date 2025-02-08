from django.conf import settings
import os
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings
from pinecone import Pinecone
from langchain.chat_models import init_chat_model

class QueryDocView(APIView):
    def post(self,request):
        if ('name' not in request.data) or (not request.data['name']):
            return Response({"error":"doc_name not provided"}, status=status.HTTP_400_BAD_REQUEST)
        if ('query' not in request.data) or (not request.data['query']):
            return Response({"error":"query not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        doc_name = request.data['name']
        query = request.data['query']

        if not settings.PINECONE_API_KEY:
            raise ValueError("Pinecone api key not found")
        
        pc = Pinecone(settings.PINECONE_API_KEY)
        index = pc.Index('personal-drive')
        embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        vector_store = PineconeVectorStore(embedding=embeddings, index=index)

        results = vector_store.similarity_search(
            query=query,
            k=5,
            filter={"source":doc_name}
        )
        context = ""
        for doc in results:
            context += doc.page_content

        if not os.environ.get("MISTRAL_API_KEY"):
            raise ValueError("Mistral api key not found")

        llm = init_chat_model("mistral-large-latest", model_provider="mistralai")
        response = llm.invoke(f"""You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
                              If you don't know the answer, just say that you don't know. Use five sentences maximum and keep the answer concise\n
                   <context>{context}</context>
                   <question>{query}</question>""")

        return Response({"Success":"True","Response":response.content},status.HTTP_200_OK)
    