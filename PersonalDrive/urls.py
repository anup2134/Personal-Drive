"""
URL configuration for PersonalDrive project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,include
from storage.views.file_views import FileUploadView,get_folder_content,create_folder,get_all,get_shared_files,get_photos,file_share
from storage.views.query_views import QueryDocView
from users.views.users_view import router,google_user_signup,get_user
from users.views.verify_email import verify_email
from users.views.users_view import (destroy,get_verified_users,get_users_id,logout)
from users.views.token_views import CookieTokenObtainPairView,CookieTokenRefreshView
from users.views.group_view import create_group,get_groups
from storage.views.group_file_views import upload_file_to_group

urlpatterns = [
    path('api/v1/storage/file/upload/', FileUploadView.as_view(), name='file-upload'),
    path('api/v1/storage/file/upload/group/', upload_file_to_group, name='group-file-upload'),
    path('api/v1/storage/folder_content/', get_folder_content, name='root-folders'),
    path('api/v1/storage/file/query/', QueryDocView.as_view(), name='file-query'),
    path('',include(router.urls)),
    path('api/v1/user/verify_email/<str:token>/',verify_email,name="verify-email"),
    path('api/v1/user/delete/',destroy,name="delete-user"),
    path('api/v1/user/tokens/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/user/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/user/list/verified/',get_verified_users,name="verified-list"),
    path('api/v1/user/list/users/',get_users_id,name="id-list"),
    path('api/v1/user/google/auth/',google_user_signup,name="google-auth"),
    path('api/v1/user/get_user/',get_user,name="get-user"),
    path('api/v1/user/logout/',logout,name="logout"),
    path('api/v1/user/create/group/',create_group,name="create-group"),
    path('api/v1/storage/folder/create/',create_folder,name="create-folder"),
    path('api/v1/get_all/',get_all,name="get-all"),
    path('api/v1/storage/shared_files/',get_shared_files,name="shared-files"),
    path('api/v1/storage/images/',get_photos, name='images'),
    path('api/v1/user/groups/all/',get_groups, name='all-groups'),
    path('api/v1/storage/file/update/share/',file_share, name='file-share'),
]
