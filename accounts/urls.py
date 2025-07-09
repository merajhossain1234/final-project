from django.urls import path
from .views import *
from .Views.forgot_password_otp import ForgotPasswordOTP,VerifyOTP,ResetPassword
from .Views.user_verification import VerifyUserOTP,SendVerificationOTP

urlpatterns = [
    path('signup',SignupView.as_view(),name='signup'),
    path('login',LoginView.as_view(),name='login'),
    path('forgot-password',ForgotPasswordOTP.as_view(),name='forgot-password'),
    path('verify-otp-password-recovery',VerifyOTP.as_view(),name='verify-otp'),
    path('send-verification-otp',SendVerificationOTP.as_view(),name='send-verification-otp'),
    path('verify-user',VerifyUserOTP.as_view(),name='verify-user-with-otp'),
    path('reset-password',ResetPassword.as_view(),name='reset-password'),
    path('google/login', GoogleLogin.as_view(), name='google_login'),
    path("get/user", GetUserDetailView.as_view(), name="get-user"),
]