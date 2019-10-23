"""
views.py: In views.py file we implement the all required view api,s

author : vishnu kumar
date : 28/09/2019
"""

import fundoo
import jwt
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render
from django_short_url.models import ShortURL
from django_short_url.views import get_surl
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .myservices import redis
from .myservices.decorators import login_decorator
from .myservices.event_emitter import ee
from .myservices.util import smd_response, valid_email
from .serializer import (
    RegistrationSerializer,
    LoginSerializer,
    PasswordResetSerialize,
    ForgotPasswordSerializer,
    FileSerializer,
    NoteShareSerializer,
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

        global response
        username = request.data['username']
        email = request.data['email']
        password = request.data['password']

        # check user enter any empty field or not if any field is empty then give error
        try:
            if username == "" or email == "" or password == "":
                raise Exception("Error :field should not be empty.")
            elif len(password) < 5:
                raise Exception("Error :password should be at least 5 character's")
            elif not valid_email(email):
                raise Exception("Email is not valid")
            elif User.objects.filter(email=email).exists():
                raise Exception("Email already exist. ")

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
            mail_url = 'http://' + str(current_site.domain) + '/api/login/activate/' + short_token[2] + '/'
            ee.emit('messageEvent', mail_subject, email, mail_url)
            response = smd_response(True, 'You are successfully registered', [{'username': username, 'email': email}])
        except Exception as exception_detail:
            response = smd_response(False, str(exception_detail), [])
        return Response(response)


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
        # pdb.set_trace()
        username = request.data['username']
        password = request.data['password']

        try:
            if username == "" or password == "":
                raise KeyError('Username/password should not be empty')

            # authenticate username and password valid or not
            if authenticate(username=username, password=password) is not None:
                jwt_token = jwt.encode({"username": username, "password": password},
                                       fundoo.settings.SECRET_KEY,
                                       algorithm='HS256').decode("utf-8")
                # set token in redis cache
                redis.redis_db.set(username, jwt_token)
                response = smd_response(True, "You are successfully login", {'Authorization key ': jwt_token})
            else:
                response = smd_response(False, "Incorrect credential", [])
        except Exception as exception_detail:
            response = smd_response(False, str(exception_detail), [])
        return Response(response)


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
        try:
            if not valid_email(email):
                raise Exception('Email address is not valid')

            if not User.objects.filter(email=email).exists():
                raise Exception('Email does not exist!')

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

            mail_url = 'http://' + str(current_site.domain) + '/api/reset_password/' + short_token[2] + '/'
            ee.emit('messageEvent', mail_subject, user.email, mail_url)
            response = smd_response(True, 'Check your mail and reset your password', [])
        except Exception as exception_detail:
            response = smd_response(False, str(exception_detail), [])
        return Response(response)


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

        try:
            if password1 == "" or password2 == "":
                raise KeyError('password should not be empty!')
            elif password1 != password2:
                raise Exception('Your password does not match!')
            elif len(password1) < 5:
                raise ValueError('password size should be grater than 5 characters')

            user.set_password(password1)
            user.save()
            response = smd_response(True, 'Your password is successfully update', [])
        except Exception as exception_detail:
            response = smd_response(False, str(exception_detail), [])
        return HttpResponse(response)


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
        response = smd_response(True, "You are authenticated user", [])
        return Response(response)


class Upload(GenericAPIView):
    """
    upload file use to upload our file like image for profile pic upload
    """

    serializer_class = FileSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        :param request: request file details which user need to post
        :return: response in smd format
        """
        # pdb.set_trace()
        file_serialize = FileSerializer(data=request.FILES)
        if file_serialize.is_valid():
            file_serialize.save()
            response = smd_response(True, 'You file is successfully uploaded',
                                    {'link': file_serialize.data['file_details'], 'status': status.HTTP_201_CREATED})
        else:
            response = smd_response(False, 'file not uploaded', [])
        return Response(response)


def activate(request, token):
    """
    :param request: request use for which user is requesting for activate there account
    :param token: token is in jwt encoded it is in short length by using django shortUrl
    :return: response of user request
    """
    global response
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
            response = smd_response(True, 'Thank you for your email confirmation. Now you can login your account.', [])
        elif user.is_active:
            response = smd_response(False, 'Link already used', [])
    else:
        response = smd_response(False, 'link is not correct', [])
    return Response(response)


class ShareNote(GenericAPIView):
    """
    Share Note API is used for share our note with note title and note content on social network
    """
    serializer_class = NoteShareSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        :param request: request parameter use for get data of Note like note title and note content
        :return: if note is not empty then render on share page
        """
        global response
        user_pk = request.data['author_id']
        title = request.data['note_title']
        content = request.data['note_body']

        if title != '' and content != '':
            context = {
                'Author': user_pk,
                'title': title,
                'content': content,
                'domain': request.build_absolute_uri
            }
            response = smd_response(True, "your Note data is going to share", context)
            return render(request, 'home.html', context)
        else:
            response = smd_response(False, 'Please enter something', [])
        return Response(response)


def social_login(request):
    """
    :param request: social login request with user social profile
    :return: render on social login page
    """
    # pdb.set_trace()

    url = get_current_site(request).domain
    return render(request, 'login.html', {'link': url})


@login_required
def home(request):
    """
    :param request: request for share data on social links
    :return:
    """
    url = get_current_site(request).domain
    return render(request, 'home.html', {'link': url})
