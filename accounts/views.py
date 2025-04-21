from django.contrib.auth import get_user_model
from .serializers import SignupSerializer,LoginSerializer
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

User = get_user_model()

# Google login view
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def process_login(self):
        super().process_login()

        # Check if the user is new
        if self.request.user.socialaccount_set.count() == 1:
            # If the user is newly signed up, mark them as verified
            if hasattr(self.request.user, 'is_verified'):
                self.request.user.is_verified = True
                self.request.user.save()


# Signup view for email-based registration
class SignupView(generics.GenericAPIView):
    serializer_class = SignupSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate token for the new user
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'email': user.email,
            'message': 'User successfully registered.'
        }, status=status.HTTP_201_CREATED)
    
# Login view for email-based login
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        # Check if the user is active
        if not user.is_active:
            return Response({'error': 'User account is deactivated.'}, status=status.HTTP_403_FORBIDDEN)

        # Generate token for the user
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'email': user.email,
            'message': 'Login successful.'
        }, status=status.HTTP_200_OK)
    