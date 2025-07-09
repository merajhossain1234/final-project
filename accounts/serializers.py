from .models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
# Signup serializer for email based registration
class SignupSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email','first_name','password','password1','whatsapp_number']
        extra_kwargs = {
            'password':{'write_only':True}
        }
    def save(self):
        user = User(
            email = self.validated_data['email']
        )
        password = self.validated_data['password']
        password1 = self.validated_data['password1']
        if password != password1:
            raise serializers.ValidationError({'password':'Passwords must match'})
        # Validate password
        # raise serializers.ValidationError with validate_password(password) as argument
        try:
            validate_password(password)
        except Exception as e:
            raise serializers.ValidationError({'password':e})
        user.username = user.email
        user.set_password(password)
        user.save()
        return user
    
# Login serializer for email based login
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = User
        fields = ['email','password']
        extra_kwargs = {
            'password':{'write_only':True}
        }
    def validate(self,data):
        email = data.get('email')
        password = data.get('password')
        if email and password:
            user = User.objects.filter(email=email).first()
            if user:
                if not user.check_password(password):
                    raise serializers.ValidationError({'password':'Incorrect password'})
                else:
                    return user
            else:
                raise serializers.ValidationError({'email':'User not found'})
        else:
            raise serializers.ValidationError({'email':'Email and password are required'})



class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login',
            'attributes',
        ]
        read_only_fields = [
            'id',
            'email'
        ]
