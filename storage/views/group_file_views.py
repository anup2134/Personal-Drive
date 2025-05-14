from rest_framework.decorators import api_view,authentication_classes,parser_classes
from users.auth_class import AccessTokenAuthentication
from users.models import Group
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from ..models import File
from django.db.utils import IntegrityError
from ..tasks.doc_parsing import process_text
from utils.s3_utils import upload_to_s3
from utils.temp_file import save_uploaded_file_temporarily


@api_view(['POST','GET'])
@parser_classes([MultiPartParser,FormParser])
@authentication_classes([AccessTokenAuthentication])
def upload_file_to_group(request):
    if request.method == "GET":
        try:
            group_id = int(request.data.get("group_id"))
            group = Group.objects.get(pk=group_id)
            if group.owner.id != request.user.id and not(request.user in [g.id for g in group.admins.all()]):
                raise Exception()
        except:
            return Response({"message":"invalid group id"},status=status.HTTP_400_BAD_REQUEST)
        
        res = [file.name for file in group.files.all()]
        return Response(res)


    try:
        group_id = int(request.data.get("group_id"))
        group = Group.objects.get(pk=group_id)
        if group.owner.id != request.user.id and not(request.user in [g.id for g in group.admins.all()]):
            raise Exception()
    except:
        return Response({"message":"invalid group id"},status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_file = request.FILES.get('file')
    folder_name = request.data.get("folder_name","root")
    user = request.user

    if not uploaded_file:
        return Response({"error": "no file provided"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        folder = group.folders.get(name=folder_name)
    except group.folders.DoesNotExist:
        return Response({"message":"folder not found"},status=status.HTTP_400_BAD_REQUEST)
    
    file_size = uploaded_file.size / (1024 * 1024)
    try:
        file = File.objects.create(
            name=uploaded_file.name,obj_type=uploaded_file.content_type,group=group,folder=folder
        )
    except IntegrityError as e:
        return Response({'message':"duplicate file name"},status = status.HTTP_409_CONFLICT)

    file_id = file.id
    user.limit = user.limit + file_size
    user.save()

    TEXT_TYPES = {
        "application/pdf",  # PDF files
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
        "text/plain",  # Plain text files
    }
        
    # if uploaded_file.content_type in TEXT_TYPES:
    #     path = save_uploaded_file_temporarily(uploaded_file,file_id)
    #     process_text.delay(path,file_id,uploaded_file.content_type)
    # else:
    #     upload_to_s3(file_id,uploaded_file,uploaded_file.content_type)

    response = Response({'file_size': file_size,'file type':uploaded_file.content_type}, status=status.HTTP_201_CREATED)
    response.set_cookie(
        key="access_token",
        value=request.COOKIES.get("access_token"),
        httponly=True,
        secure=True,
        samesite="None",
        max_age=15 * 60
    )
    return response
    
    
