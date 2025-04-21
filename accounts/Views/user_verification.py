from django.core.mail import send_mail
from django.core.cache import cache
import random
from django.contrib.auth import get_user_model
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

User = get_user_model()
def send_verification_otp(user,email):
    otp = random.randint(10000,99999)
    otp = str(otp)
    cache.set(f"user_verification_{user.id}",otp,900)
    send_mail(
        subject="Verify Your Account",
        message="",
        from_email="......................",   # Enter Email
        recipient_list=[email]
    )
  
# View for sending the OTP (send otp to User email)
class SendVerificationOTP(GenericAPIView):
    def post(self,request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user:
          if user.is_verified:
              return Response({"message":"User already verified"},status=400)
          send_verification_otp(user,email)
          return Response({"message":"OTP sent successfully"})
        return Response({"message":"User not found"},status=400)
  
# View for verifying the OTP (send otp to User email)
class VerifyUserOTP(GenericAPIView):
    def post(self,request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message":"User not found"},status=400)
        cached_otp = cache.get(f"user_verification_{user.id}")
        if cached_otp and otp == cached_otp:
            user.is_verified = True
            user.save()
            cache.delete(f"user_verification_{user.id}")
            return Response({"message":"User verified successfully"})
        return Response({"message":"Invalid OTP"},status=400)