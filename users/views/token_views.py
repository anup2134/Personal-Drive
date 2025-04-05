from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from ..models import User

class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        access = response.data.pop("access")
        refresh = response.data.pop("refresh")
        
        user = User.objects.get(email=request.data['email'])
        user = {
            "f_name":user.f_name,
            "l_name":user.l_name,
            "id":user.id,
            "email":user.email,
            "picture":user.picture,
            "limit":user.limit
        }

        response.data['user'] = user
        response.set_cookie(
            key="access_token", 
            value=access,
            httponly=True,  
            secure=True, 
            samesite="None",
            max_age=15 * 60
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=7 * 24 * 60 * 60
        )

        return response

class CookieTokenRefreshView(TokenRefreshView):
    def post(self,request,*args,**kwargs):
        request.COOKIES['refresh'] = request.COOKIES.get("refresh_token")
        response = super().post(request,*args,**kwargs)
        access = response.data.pop('access')
        response.set_cookie(
            key="access_token", 
            value=access,
            httponly=True,  
            secure=False,   # set true in production 
            samesite="None",
            max_age=15 * 60
        )
        response.data["message"] = "success"
        return response
    
class TokensClass(TokenObtainPairView):
    def get_tokens(self, request, *args, **kwargs):
        self.request = request
        response = super().post(request, *args, **kwargs)
        access = response.data.pop("access")
        refresh = response.data.pop("refresh")

        return [access,refresh]