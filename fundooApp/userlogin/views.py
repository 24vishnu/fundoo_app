"""
views.py
    In views.py file we implement the all required view api,s

author : vishnu kumar
date : 28/09/2019
"""

import json

import jwt
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import render
from django_short_url.models import ShortURL
from django_short_url.views import get_surl
from myservices import redis
from myservices.decorators import login_decorator
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

import fundoo
from rest_framework.response import Response

from .event_emitter import *
from .serializer import (
    RegistrationSerializer,
    LoginSerializer,
    PasswordResetSerialize,
    ForgotPasswordSerializer,
    FileSerializer,
)


class UserRegistration(GenericAPIView):
    """
    Following class is implement for register a new user and send a verification link
    for activate there profile
    """

    # we need to include serialize class
    serializer_class = RegistrationSerializer

    def post(self, request):
        """
        :param request: user request for send information for register the user
                        request parameters are username, email and password
        :return: we send a activation link on user given mail if user input is valid
        """

        # response is a dictionary SMD format default success is False
        response = {
            "success": False,
            "message": "something went wrong",
            "data": []
        }

        username = request.data['username']
        email = request.data['email']
        password = request.data['password']

        # check user enter any empty field or not if any field is empty then give error
        if username == "" or email == "" or password == "":
            response['message'] = "Error :field should not be empty."
            return HttpResponse(json.dumps(response, indent=1))
        elif len(password) < 5:
            response['message'] = "Error :password should be at least 5 character's"
            return HttpResponse(json.dumps(response, indent=1))
        elif User.objects.filter(email=email).exists():
            response['message'] = "Email already exist. "
            return HttpResponse(json.dumps(response))

        try:
            # check given email is valid or not
            try:
                validate_email(email)
            except:
                response['message'] = 'email is not valid'
                return HttpResponse(json.dumps(response))

            # if all user input data is correct then create user profile with given name, email and password and
            # then save in database
            user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
            user.save()

            # Get current site
            current_site = get_current_site(request)

            # create jwt token this token is in byte form therefor we decode and convert into string format
            jwt_token = jwt.encode(
                {user.username: user.email},
                fundoo.settings.SECRET_KEY,
                algorithm='HS256'
            ).decode("utf-8")
            mail_url = get_surl(jwt_token)
            short_token = mail_url.split("/")
            mail_subject = 'Activate your account'
            mail_url = 'http://' + str(current_site.domain) + '/login/activate/' + short_token[2] + '/'
            # message_short_url = short_url.sort_url_method(mail_url)
            ee.emit('messageEvent', mail_subject, email, mail_url)
            response['success'] = True
            response['message'] = "You are successfully registered " \
                                  ",Only you need to verify your Email"
            return HttpResponse(json.dumps(response, indent=1), status=201)
        except Exception as exception_detail:
            return HttpResponse(str(exception_detail))  # response, indent=1))


class UserLogin(GenericAPIView):
    """
    login method use for login any user,
    if it is valid user otherwise print error
    """

    # we need to include serialize class
    serializer_class = LoginSerializer

    def post(self, request):
        """
        :param request: username and password for login
        :return: if username and password is correct then response login success other wise give error
        """
        username = request.data['username']
        password = request.data['password']

        response = {
            "status": False,
            "message": "something went wrong",
            "data": []
        }

        if username == "" or password == "":
            response['message'] = 'Username/password should not be empty'
            return HttpResponse(json.dumps(response, indent=1))
        try:
            # authenticate username and password valid or not
            if authenticate(username=username, password=password) is not None:
                jwt_token = jwt.encode({"username": username, "password": password},
                                       fundoo.settings.SECRET_KEY,
                                       algorithm='HS256').decode("utf-8")
                # set token in redis cache
                redis.redis_db.set(username, jwt_token)
                response['status'] = True
                response['message'] = "You are successfully login"
                response['data'] = {'Authorization key ': jwt_token}
                print(redis.redis_db.get(username))
                return HttpResponse(json.dumps(response, indent=1))
            else:
                response['message'] = "Incorrect Username or Password"
                raise Exception("Incorrect Username or Password")
        except Exception as exception_detail:
            return HttpResponse(json.dumps(str(exception_detail)))


# pylint: disable= line-too-long
# pylint: disable= no-self-use
class ForgotPassword(GenericAPIView):
    """
    Forgot password class user to send a activation link on user email
    if user forgot there password
    """

    # need to include serializer class
    serializer_class = ForgotPasswordSerializer
    # give the permission allow any type
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        :param request: take user email address for sending reset password link
        :return:
        """
        email = request.data['email']
        response = {
            'status': False,
            'message': 'Something is wrong',
            'data': []
        }
        try:
            validate_email(email)
            if email == "":
                messages.info(request, "field should not be empty.")
                raise Exception("field should not be empty.")

            user = User.objects.get(email=email)
            current_site = get_current_site(request)
            mail_subject = 'Reset your Password account.'

            jwt_token = jwt.encode(
                {user.username: user.email},
                fundoo.settings.SECRET_KEY,
                algorithm='HS256'
            ).decode("utf-8")
            mail_url = get_surl(jwt_token)
            short_token = mail_url.split("/")

            mail_url = 'http://' + str(current_site.domain) + '/reset_password/' + short_token[2] + '/'
            ee.emit('messageEvent', mail_subject, user.email, mail_url)
            response['status'] = True
            response['message'] = 'Check your mail and reset your password'
            return HttpResponse(json.dumps(response))
        except Exception as exception_detail:
            return HttpResponse(json.dumps(response))


# pylint: disable=line-too-long
# pylint: disable= no-self-use
class ResetPassword(GenericAPIView):
    """
    Reset password class is used for user password change password
    """

    # include the serializer class of reset password serializer
    serializer_class = PasswordResetSerialize

    def post(self, request, token):
        """
        :param token:
        :param request: take the user input as username, password and confirm password
        :return: if user name is exist then send response password set successfully
                 other wise print error message
        """
        token1 = ShortURL.objects.get(surl=token)
        decoded_token = jwt.decode(token1.lurl, fundoo.settings.SECRET_KEY, algorithms='HS256')
        user = User.objects.get(username=list(decoded_token.keys())[0])

        password1 = request.data['password1']
        password2 = request.data['password2']
        response = {
            'status': False,
            'message': 'Something is wrong',
            'data': []
        }

        try:
            if password1 == "" or password2 == "":
                response['message'] = 'password should not be empty!'
                return HttpResponse(json.dumps(response))
            elif password1 != password2:
                response['message'] = 'Your password does not match!'
                return HttpResponse(json.dumps(response))
            elif len(password1) < 5:
                response['message'] = 'password size should be grater than 5 characters'
                return HttpResponse(json.dumps(response))

            user.set_password(password1)
            user.save()
            response['status'] = True
            response['message'] = 'Your password is successfully update'
            return HttpResponse(json.dumps(response))

        except Exception as exception_detail:
            return HttpResponse(json.dumps(response))


class UserProfile(GenericAPIView):
    """
    user profile class is used this will display if user is authenticated
    """

    # include the serialize class and permission class (IsAuthenticated)
    serializer_class = LoginSerializer

    @staticmethod
    @login_decorator
    def get(request):
        """
        :return:
        """
        response = {"status": True, "message": "You are authenticated user", "data": []}
        return HttpResponse(json.dumps(response, indent=1))


class Upload(GenericAPIView):
    serializer_class = FileSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        response = {
            "success": False,
            "message": "something went wrong",
            "data": []
        }
        file_serialize = FileSerializer(data=request.FILES)
        if file_serialize.is_valid():
            file_serialize.save()
            response['success'] = True
            response['message'] = 'You file is successfully uploaded'
            response['data'] = [file_serialize.data['file_details'], status.HTTP_201_CREATED]
            return Response(json.dumps(response))
        else:
            response['message'] = [status.HTTP_400_BAD_REQUEST]
            return Response(json.dumps(response))


def activate(request, token):
    response = {
        'status': False,
        'message': 'something is wrong',
        'data': []
    }
    try:
        token = ShortURL.objects.get(surl=token)
        decoded_token = jwt.decode(token.lurl, fundoo.settings.SECRET_KEY, algorithms='HS256')
        user = User.objects.get(username=list(decoded_token.keys())[0])
    except Exception:
        user = None
    if user is not None:
        if not user.is_active:
            user.is_active = True
            user.save()
            response['status'] = True
            response['message'] = 'Thank you for your email confirmation. Now you can login your account.'
        elif user.is_active:
            response['message'] = 'This like already used'
    else:
        response['message'] = 'This is not valid link'

    return HttpResponse(json.dumps(response, indent=2))


def profile_view(request):
    return render(request, 'index.html')


def login(request):
    return render(request, 'login.html')


@login_required
def home(request):
    return render(request, 'home.html')