"""
serializer.py
    This is serializer.py class for user authentication model classes

author : vishnu kumar
date : 30/09/2019
"""
from rest_framework import serializers
from .models import Registration, UserLogin, PasswordReset, ForgotPassword


class RegistrationSerializer(serializers.ModelSerializer):
    """ Registration serializer class"""
    class Meta:
        """ Meta class of Registration serializer class"""
        model = Registration
        fields = '__all__'


class LoginSerializer(serializers.ModelSerializer):
    """ This is Login serializer class """
    class Meta:
        """ Meta class of Login serializer class """
        model = UserLogin
        fields = (['username', 'password'])


class PasswordResetSerialize(serializers.ModelSerializer):
    """ This is Password Reset class"""
    class Meta:
        """ meta class of Password Reset class"""
        model = PasswordReset
        fields = (['username', 'password1', 'password2'])


class ForgotPasswordSerializer(serializers.ModelSerializer):
    """ This is Forgot password serializer class"""
    class Meta:
        """ Meta class of Forgot password serializer class"""
        model = ForgotPassword
        fields = (['email'])
