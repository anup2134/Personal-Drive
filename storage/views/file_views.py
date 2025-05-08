from rest_framework.views import APIView 
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed,NotFound
from rest_framework.decorators import api_view,authentication_classes

from django.conf import settings
from django.db.utils import IntegrityError

from users.auth_class import AccessTokenAuthentication
from ..models import File,Folder
from ..tasks.doc_parsing import process_text
from utils.s3_utils import upload_to_s3,generate_presigned_url
from utils.temp_file import save_uploaded_file_temporarily
from users.models import User,Group,EmailVerificationToken
from ..serializers import FileSerializer, FolderSerializer, SharedFileSerializer

#NW426uLB2zxi9F3

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [AccessTokenAuthentication]
    def post(self, request:Request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({"error": "no file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        if not user:
            raise AuthenticationFailed("user not found")
        file_size = uploaded_file.size / (1024 * 1024)
        user.limit = user.limit + file_size

        try:
            user.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        try:
            folder_id = int(request.data.get("folder_id"))
            folder = user.folders.get(pk=folder_id)
        except:
            raise NotFound("invalid folder id")

        try:
            file = File.objects.create(
                name=uploaded_file.name,obj_type=uploaded_file.content_type,owner=user,folder=folder,size=file_size
            )
        except IntegrityError as e:
            return Response({'message':"duplicate file name"},status = status.HTTP_409_CONFLICT)

        TEXT_TYPES = {
            "application/pdf",  # PDF files
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
            "text/plain",  # Plain text files
        }
        
        # if uploaded_file.content_type in TEXT_TYPES:
        #     path = save_uploaded_file_temporarily(uploaded_file,file.id)
        #     process_text.delay(path,file.id,uploaded_file.content_type)
        #     upload_to_s3(file.id,path,uploaded_file.content_type)
        # else:
        #     upload_to_s3(file.id,uploaded_file,uploaded_file.content_type)

        # path = save_uploaded_file_temporarily(uploaded_file,file.id)
        # process_text.delay(path,file.id,uploaded_file.content_type)

        file_data = FileSerializer(file).data
        response = Response(file_data, status=status.HTTP_201_CREATED)
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
        try:
            file_id = int(request.query_params.get("file_id"))
            file = request.user.files.get(pk=file_id)
        except:
            return Response({"error": "file not found"}, status=status.HTTP_404_NOT_FOUND)
        
        file_size = file.size
        file.delete()
        request.user.limit -= file_size
        request.user.save()
        response = Response("File deleted successfully.",status=status.HTTP_204_NO_CONTENT)
        response.set_cookie(
            key="access_token",
            value=request.COOKIES.get("access_token"),
            httponly=True,
            secure=True,
            samesite="None",
            max_age=15 * 60
        )
        return response

@api_view(["POST"])
@authentication_classes([AccessTokenAuthentication]) 
def create_folder(request):
    user = request.user
    try:
        parent_folder_id = request.data.get("parent_folder_id")
    except (ValueError, TypeError):
        return Response({"error": "Invalid parent folder ID"}, status=status.HTTP_400_BAD_REQUEST)
    
    folder_name = request.data.get("folder_name")
    if not folder_name or folder_name == "root":
        return Response({"error": "folder name is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    
    parent_folder = user.folders.get(pk=parent_folder_id)

    folder = Folder.objects.create(name=folder_name,owner=user,parent=parent_folder)
    serialize = FolderSerializer(folder)

    response = Response({
        "folder": serialize.data
    }, status=status.HTTP_201_CREATED)
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
def get_folder_content(request):
    user = request.user
    try:
        folder_id = int(request.query_params.get("folder_id"))
        folder = user.folders.get(pk=folder_id)
    except (ValueError, TypeError):
        return Response({"error": "Invalid folder ID"}, status=status.HTTP_400_BAD_REQUEST) 
    
    files = folder.files.all()
    files = FileSerializer(files, many=True).data
    sub_folders = folder.subfolders.all()
    sub_folders = FolderSerializer(sub_folders, many=True).data

    response = Response({"files":files,"sub_folders":sub_folders})
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
def get_shared_files(request):
    user = request.user
    shared_files = user.shared_files.all()
    file_serializer_data = SharedFileSerializer(shared_files,many=True).data
    
    response = Response(file_serializer_data,status=status.HTTP_200_OK)
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
def get_photos(request):
    user = request.user
    photos = user.files.filter(obj_type__startswith="image/")
    photos = FileSerializer(photos,many=True).data
    
    response = Response(photos,status=status.HTTP_200_OK)
    response.set_cookie(
        key="access_token",
        value=request.COOKIES.get("access_token"),
        httponly=True,
        secure=True,
        samesite="None",
        max_age=15 * 60
    )
    return response

@api_view(["PUT"])
@authentication_classes([AccessTokenAuthentication])
def file_share(request):
    user = request.user
    try:
        file_id = request.data.get("file_id")
        file = user.files.get(pk=file_id)
    except File.DoesNotExist:
        return Response({"error":"File not found."},status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({"error":"Invalid file ID."},status=status.HTTP_400_BAD_REQUEST)
    anyone = request.data.get("anyone")
    email = request.data.get("email")
    response = Response(status=status.HTTP_204_NO_CONTENT)
    response.set_cookie(
        key="access_token",
        value=request.COOKIES.get("access_token"),
        httponly=True,
        secure=True,
        samesite="None",
        max_age=15 * 60
    )
    if anyone:
        file.access = 'ANYONE'
        file.save()
        return response
    elif email != "":
        try:
            user2 = User.objects.get(email=email)
            file.shared.add(user2)
            file.save()
            return response
        except:
            return Response({"error":"Invalid Email ID."},status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error":"Invalid request"},status=status.HTTP_400_BAD_REQUEST)
    

@api_view(["GET"])
@authentication_classes([AccessTokenAuthentication])
def search_files_folders(request):
    user = request.user
    name = request.query_params.get("name")

    try:
        files = user.files.filter(name__icontains=name)
        # files = user.files.all()
        folders = user.folders.filter(name__icontains=name)
        print(files)
        print(folders)
        files = FileSerializer(files,many=True).data
        folders = FolderSerializer(folders,many=True).data

        response = Response({"files":files,"folders":folders},status=status.HTTP_200_OK)
        response.set_cookie(
            key="access_token",
            value=request.COOKIES.get("access_token"),
            httponly=True,
            secure=True,
            samesite="None",
            max_age=15 * 60
        )
        return response
    except:
        return Response({"error":"Invalid request"},status=status.HTTP_400_BAD_REQUEST)
    

@api_view(["GET"])
def get_all(request):
    if not settings.DEBUG:
        return Response({"message": "This endpoint is disabled in production"}, status=status.HTTP_403_FORBIDDEN)
    
    files = File.objects.all()
    files = [{
        "name":file.name,
        'id':file.id,
        "user_id":file.owner.id,
        "group_id": "no group" if not file.group else file.group.id,
        "folder_id":file.folder.id,
        "access":file.access
    } for file in files]

    users = User.objects.all()
    users = [{
        "id":user.id,
        "email":user.email,
        "f_name":user.f_name,
        "l_name":user.l_name,
        "limit":user.limit
    } for user in users]
    groups = Group.objects.all()
    groups = [{
        "id":group.id,
        "name":group.name,
        "owner":group.owner.id,
        "admins":[admin.id for admin in group.admins.all()],
        "users":[user.id for user in group.users.all()]
    } for group in groups]
    tokens = EmailVerificationToken.objects.all()
    tokens = [{
        "id":token.id,
        "user_id":token.user.id,
        "token":token.token,
        "expires_at":token.expires_at
    } for token in tokens]
    folders = Folder.objects.all()
    folders = [{
        "id":folder.id,
        "name":folder.name,
        "owner":folder.owner.id,
        "group":folder.group.id if folder.group else None,
        "parent":folder.parent.id if folder.parent else None
    } for folder in folders]
    
    response = Response({'users':users,"tokens":tokens,"groups":groups,"files":files,"folders":folders},status=status.HTTP_200_OK)
    response.set_cookie(
        key="access_token",
        value=request.COOKIES.get("access_token"),
        httponly=True,
        secure=True,
        samesite="None",
        max_age=15 * 60
    )
    return response
