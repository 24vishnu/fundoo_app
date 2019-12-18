"""
serializer.py
    This is serializer.py class for user authentication model classes

author : vishnu kumar
date : 30/09/2019
"""
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


def email_validation(email):
    if User.objects.filter(email=email).exists():
        raise serializers.ValidationError("Email already exist")
    return email


def empty_validation(input_data):
    if input_data == "":
        raise serializers.ValidationError("Field should not be empty")
    return input_data


def username_validation(username):
    if User.objects.filter(username=username).exists():
        raise serializers.ValidationError("Username already exist")
    return username


class RegistrationSerializer(serializers.ModelSerializer):
    """ Registration serializer class"""
    username = serializers.CharField(max_length=200, validators=[username_validation])
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=150, validators=[email_validation])
    password = serializers.CharField(max_length=50)

    class Meta:
        """ Meta class of Registration serializer class"""
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']


class LoginSerializer(serializers.ModelSerializer):
    """ This is Login serializer class """
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=50)

    class Meta:
        """ Meta class of Login serializer class """
        model = User
        fields = (['username', 'password'])


class PasswordResetSerialize(serializers.ModelSerializer):
    """ This is Password Reset class"""
    password = serializers.CharField(max_length=50)
    confirm_password = serializers.CharField(max_length=50)

    class Meta:
        """ meta class of Password Reset class"""
        model = User
        fields = (['password', 'confirm_password'])


class ForgotPasswordSerializer(serializers.ModelSerializer):
    """ This is Forgot password serializer class"""
    email = serializers.EmailField(max_length=150)

    class Meta:
        """ Meta class of Forgot password serializer class"""
        model = User
        fields = ['email']


class FileSerializer(serializers.ModelSerializer):
    file_details = serializers.FileField(default=False)

    class Meta:
        model = User
        fields = ['file_details']


class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['image']
