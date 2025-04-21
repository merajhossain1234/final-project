from django.core.mail import send_mail
from django.core.cache import cache
import random
from django.contrib.auth import get_user_model
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

User = get_user_model()

def send_otp_email(user, email):
    # generate random 5 digit OTP
    otp = str(random.randint(10000, 99999))
    # store the OTP in cache
    cache.set(f"reset_user_{user.id}", otp, timeout=900)

    # create a simple plain text email message
    message = f"""
    Hi {user.username},

    Here's your One-Time Password (OTP) to reset your password: {otp}

    This code is valid for 10 minutes. Please enter it on the password reset page.

    If you didn't request a password reset, please ignore this email.

    Best regards,
    OneNightPrep Team
    """

    # send the plain text email
    send_mail(
        subject="Reset Password OTP",
        message=message,
        from_email=".........................",   #Enter email here
        recipient_list=[email]
    )
# send otp email to the user when they request to reset their password
class ForgotPasswordOTP(GenericAPIView):
    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            send_otp_email(user,email)
            return Response({"message": "An OTP has been sent to your email address."}, status=200)
        return Response({"error": "User not found."}, status=404)
    
# verify the OTP entered by the user
class VerifyOTP(GenericAPIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        user = User.objects.filter(email=email).first()
        if user:
            if cache.get(f"reset_user_{user.id}") == otp:
                return Response({"message": "OTP is valid."}, status=200)
            return Response({"error": "Invalid OTP."}, status=400)
        return Response({"error": "User not found."}, status=404)
    
# reset the user's password (if OTP is valid)
class ResetPassword(GenericAPIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        otp = request.data.get("otp")
        user = User.objects.filter(email=email).first()
        if user:
            if cache.get(f"reset_user_{user.id}") == otp:
                user.set_password(password)
                user.save()
                cache.delete(f"reset_user_{user.id}")
                return Response({"message": "Password reset successfully."}, status=200)
            return Response({"error": "Invalid OTP."}, status=400)
        return Response({"error": "User not found."}, status=404)