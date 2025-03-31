import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class AccessTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        if not access_token:
            raise AuthenticationFailed("no token found")
        try:
            decoded_access = jwt.decode(access_token, api_settings.SIGNING_KEY, algorithms=[api_settings.ALGORITHM])
            user_id = decoded_access.get('user_id')
            user = User.objects.get(id=user_id)
            return (user,None)
        except jwt.ExpiredSignatureError:
            if not refresh_token:
                raise AuthenticationFailed("Access token expired and no refresh token provided.")
            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
                decoded_refresh = jwt.decode(refresh_token, api_settings.SIGNING_KEY, algorithms=[api_settings.ALGORITHM])
                user_id = decoded_refresh.get('user_id')
                user = User.objects.get(id=user_id)

                request.COOKIES['access_token'] = new_access_token
                return (user, None)

            except jwt.InvalidTokenError:
                raise AuthenticationFailed("Invalid refresh token.")
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Refresh token expired')
            except Exception as e:
                print(f"Error during refresh: {e}")
                raise AuthenticationFailed("Error refreshing token.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid Token")