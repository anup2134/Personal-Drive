from rest_framework.decorators import api_view,authentication_classes
from ..auth_class import AccessTokenAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from ..models import Group,User
# from storage.models import Folder
# from storage.models import Folder
from rest_framework import status

@api_view(["POST","GET"])
@authentication_classes([AccessTokenAuthentication])
def groups(request:Request):
    response = Response({})
    response.set_cookie(
        key="access_token",
        value=request.COOKIES.get("access_token"),
        httponly=True,
        secure=True,
        samesite="None",
        max_age=15 * 60
    )
    if request.method == "GET":
        user = request.user
        owned_groups = user.group_owner.all()
        admin_groups = user.group_admin.all()
        groups = user.group_users.all()

        res1 = [{"name":group.name,"id":group.id} for group in owned_groups]
        res2 = [{"name":group.name,"id":group.id} for group in groups]
        res3 = [{"name":group.name,"id":group.id} for group in admin_groups]

        response.data["owned_groups"] = res1
        response.data["groups"] = res3
        response.data["admin_groups"] = res2
        response.status_code=200

        return response

    group_name = request.data.get('name')
    members = request.data.get('members')
    user = request.user
    
    if not group_name:
        response.data['message'] = "Group name is required."
        response.status_code = 400
        return response
    
    group = Group.objects.create(
        owner=user,
        name=group_name
    )

    for member_email in members:
        try:
            user = User.objects.get(email=member_email)
            group.users.add(user)
        except:
            group.delete()
            response.data['message'] = "Invalid user email."
            response.status_code = 400
            return response

    response.data["message"] = "Group created."
    response.status_code = 201
    return response
