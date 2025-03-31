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
from storage.views.file_views import FileUploadView
from storage.views.query_views import QueryDocView
from users.views.users import router,google_user_signup
from users.views.verify_email import verify_email
from users.views.users import (destroy,get_verified_users,get_users_id)
from users.views.token_views import CookieTokenObtainPairView,CookieTokenRefreshView


urlpatterns = [
    path('api/v1/file/pdf/upload/', FileUploadView.as_view(), name='file-upload'),
    path('api/v1/file/pdf/query/', QueryDocView.as_view(), name='file-query'),
    path('',include(router.urls)),
    path('api/v1/user/verify_email/<str:token>/',verify_email,name="verify-email"),
    path('api/v1/user/delete/',destroy,name="delete-user"),
    path('api/v1/user/tokens/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/user/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/user/list/verified/',get_verified_users,name="verified-list"),
    path('api/v1/user/list/users/',get_users_id,name="id-list"),
    path('api/v1/user/google/auth/',google_user_signup,name="google-auth")
]
