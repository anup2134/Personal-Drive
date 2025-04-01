import os
from django.conf import settings

from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain.chat_models import init_chat_model
from langchain_ollama import OllamaEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

from users.auth_class import AccessTokenAuthentication
from storage.models import File

class QueryDocView(APIView):
    authentication_classes = [AccessTokenAuthentication]
    def post(self,request):
        if 'file_id' not in request.data or 'query' not in request.data:
            return Response({'message':"bad query"},status=status.HTTP_400_BAD_REQUEST)
        
        file_id = request.data['file_id']
        query = request.data['query']

        user = request.user
        try:
            user.files.get(pk=int(file_id))
        except File.DoesNotExist:
            return Response({"message":"file not found"},status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"message":"invalid file id"},status=status.HTTP_400_BAD_REQUEST)

        if not settings.PINECONE_API_KEY:
            raise ValueError("Pinecone api key not found")
        
        pc = Pinecone(settings.PINECONE_API_KEY)
        index = pc.Index('personal-drive')
        embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        vector_store = PineconeVectorStore(embedding=embeddings, index=index,namespace=file_id)

        results = vector_store.similarity_search(
            query=query,
            k=5,
        )
        context=""
        for doc in results:
            context += doc.page_content

        if not os.environ.get("GOOGLE_API_KEY"):
            raise ValueError("gemini api key not found")

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        response = llm.invoke(f"""You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
                              If you don't know the answer, just say "Unable to answer the question due to lack of relevant information.". Keep the answer concise\n
                   <context>{context}</context>
                   <question>{query}</question>""")

        return Response({"success":"true","response":response.content},status.HTTP_200_OK)
    