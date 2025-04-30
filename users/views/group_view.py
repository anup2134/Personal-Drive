from rest_framework.decorators import api_view,authentication_classes
from ..auth_class import AccessTokenAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from ..models import Group
# from storage.models import Folder
# from storage.models import Folder
from rest_framework import status

@api_view(["POST","GET","DELETE"])
@authentication_classes([AccessTokenAuthentication])
def create_group(request:Request):
    if request.method == "DELETE":
        request.user.group_owner.all().delete()

        return Response("DELETED",status=status.HTTP_205_RESET_CONTENT)
    

    if request.method == "GET":
        user = request.user
        owned_groups = user.group_owner.all()
        admin_groups = user.group_admin.all()
        groups = user.group_users.all()

        res1 = [{"name":group.name,"id":group.id} for group in owned_groups]
        res2 = [{"name":group.name,"id":group.id} for group in groups]
        res3 = [{"name":group.name,"id":group.id} for group in admin_groups]

        response = Response({"owned_groups":res1,"groups":res3,"admin_groups":res2},status=status.HTTP_200_OK)
        response.set_cookie(
            key="access_token",
            value=request.COOKIES.get("access_token"),
            httponly=True,
            secure=True,
            samesite="None",
            max_age=15 * 60
        )
        return response

    group_name = request.data.get('name')
    user = request.user
    
    if not group_name:
        return Response({"message":"group name is required"},status=status.HTTP_400_BAD_REQUEST)
    Group.objects.create(
        owner=user,
        name=group_name
    )

    response = Response({"message":"group created"},status=status.HTTP_201_CREATED)
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
def get_groups(request:Request):
    user = request.user
    owned_groups = user.group_owner.all()
    admin_groups = user.group_admin.all()
    groups = user.group_users.all()

    res1 = [{"name":group.name,"id":group.id} for group in owned_groups]
    res2 = [{"name":group.name,"id":group.id} for group in groups]
    res3 = [{"name":group.name,"id":group.id} for group in admin_groups]

    response = Response({"owned_groups":res1,"groups":res3,"admin_groups":res2},status=status.HTTP_200_OK)
    response.set_cookie(
        key="access_token",
        value=request.COOKIES.get("access_token"),
        httponly=True,
        secure=True,
        samesite="None",
        max_age=15 * 60
    )
    return response