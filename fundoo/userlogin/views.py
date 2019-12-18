"""
views.py: In views.py file we implement the all required view api,s

author : vishnu kumar
date : 28/09/2019
"""
import json
import logging
import pdb
# decouple package work on .env, .ini
# from decouple import config
from decouple import config
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_short_url.models import ShortURL
from django_short_url.views import get_surl
# from fundoo.settings import file_handler
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.reverse import reverse

from fundoo.settings import file_handler
from services import util, redis
from services.aws import aws_file_upload
from services.decorators import login_decorator, check_login
from services.event_emitter import ee
from .models import UserProfile
from .serializer import (
    RegistrationSerializer,
    LoginSerializer,
    PasswordResetSerialize,
    ForgotPasswordSerializer,
    UploadSerializer,
)

# from services import (
#     redis,
#     util,
# )
# from services.decorators import login_decorator
# from services.event_emitter import ee

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


# we con use like following config method
# DEBUG = config('REDIS_PORT', default=8000, cast=int)
# print(DEBUG)


class UserRegistration(GenericAPIView):
    """
    Following class is implement for register a new user and send a verification link
    for activate there profile
    """

    # we need to include serialize class
    serializer_class = RegistrationSerializer

    # @csrf_exempt
    def post(self, request):
        """
        :param request: user request for send information for register the user
                        request parameters are username, email and password
        :return: we send a activation link on user given mail if user input is valid
        """
        # check user enter any empty field or not if any field is empty then give error
        try:
            serialized_data = RegistrationSerializer(data=request.data)
            if not 'username' in serialized_data.initial_data or not 'first_name' in serialized_data.initial_data \
                    or not 'last_name' in serialized_data.initial_data:
                logger.error("first name field is not present")
                raise KeyError('first name field is not present')

            if not 'password' in serialized_data.initial_data or \
                    not 'email' in serialized_data.initial_data:
                logger.error("username/password/email field is not present")
                raise KeyError('username and password field is not present')
            serialized_data.is_valid(raise_exception=True)
            user = serialized_data.save()
            user.is_active = False
            user.save()
            payload = {
                user.username: user.email
            }

            jwt_token = util.create_token(payload)
            mail_url = get_surl(jwt_token)
            short_token = mail_url.split("/")
            mail_subject = 'Activate your account'
            # Todo request schema for reverse url : DONE
            # print(request.build_absolute_uri(reverse('userlogin:activate', kwargs={'token': short_token[2]})))
            mail_url = request.build_absolute_uri(reverse('userlogin:activate', kwargs={'token': short_token[2]}))
            ee.emit('messageEvent', mail_subject, user.email, mail_url)
            response = util.smd_response(success=True, message='You are successfully registered',
                                         http_status=status.HTTP_201_CREATED)
            logger.info('User successfully registered')
        except (KeyError, ValueError) as error:
            response = util.smd_response(message=str(error), http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception_detail:
            logger.error(exception_detail)
            response = util.smd_response(message=str(exception_detail), http_status=status.HTTP_404_NOT_FOUND)
        return response


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
        
        # Todo create required validation : DONE
        try:
            serialized_data = LoginSerializer(data=request.data)
            if not 'username' in serialized_data.initial_data or not 'password' in serialized_data.initial_data:
                logger.error('username or password field not present')
                raise EnvironmentError('username or password field not present')
            if not serialized_data.is_valid():
                logger.error('LoginSerializer serialized data not valid')
                raise ValueError('please enter valid', [k for k in serialized_data.errors.keys()])

            username = serialized_data.data['username']
            password = serialized_data.data['password']

            if username == "" or password == "":
                logger.error("Username/password Field should not be empty.")
                raise KeyError('Username/password should not be empty')

            # authenticate username and password valid or not
            user = authenticate(username=username, password=password)
            
            if user is not None:
                payload = {"username": username, 'password': password}
                jwt_token = util.token_encode(payload)
                # # print(util.token_encode(payload))
                # # set token in redis cache
                redis.redis_db.set(username, jwt_token)

                # todo all small latter : DONE
                response = util.smd_response(success=True, message="You are successfully login",
                                             data={'access': jwt_token},
                                             http_status=status.HTTP_201_CREATED)
                logger.info('user successful login.')
            else:
                logger.error('Incorrect credential')
                response = util.smd_response(message="Incorrect credential",
                                             http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception_detail:
            response = util.smd_response(message=str(exception_detail), http_status=status.HTTP_400_BAD_REQUEST)
        return response


# pylint: disable= no-self-use, line-too-long
class ForgotPassword(GenericAPIView):
    """
    Forgot password class user to send a activation link on user email
    if user forgot there password
    """

    serializer_class = ForgotPasswordSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        :param request: take user email address for sending reset password link
        :return:
        """
        # todo use body in place of request.data : DONE (but now i am using serializer)
        
        try:

            serialized_data = ForgotPasswordSerializer(data=request.data)
            if not 'email' in serialized_data.initial_data:
                logger.error('email field not present')
                raise KeyError('email field not present')
            if serialized_data.is_valid():
                email = serialized_data.data['email']
                if not util.valid_email(email):
                    logger.error('Invalid Email')
                    raise ValueError('Email address is not valid')

                if not User.objects.filter(email=email).exists():
                    logger.error('Email does not exist.')
                    raise ValueError('You are not register user!')

                mail_subject = 'Reset your Password account.'
                payload = {'email': email}
                jwt_token = util.create_token(payload)
                
                mail_url = get_surl(jwt_token)
                short_token = mail_url.split("/")
                # todo not use underscore in url : DONE

                # mail_url = request.build_absolute_uri(
                #     reverse('userlogin:resetpassword', kwargs={'token': short_token[2]}))

                mail_url = config('FRONT_END_RESET_PASSWORD') + short_token[2]
                # ee.emit('emptEvent', mail_subject, email, mail_url)
                ee.emit('messageEvent', mail_subject, email, mail_url)
                response = util.smd_response(success=True, message='Check your mail and reset your password',
                                             http_status=status.HTTP_200_OK)
                logger.info('password link send on email')
            else:
                logger.error('ForgotPasswordSerializer serializer data not valid')
                response = util.smd_response(message='serializer data not valid',
                                             http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception_detail:
            response = util.smd_response(message=str(exception_detail),
                                         http_status=status.HTTP_404_NOT_FOUND)
        return response


# todo check slug field in detail

# pylint: disable= no-self-use, line-too-long
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
        # return request.get("http://localhost:4200/login")
        # todo try re lib. most of time (TRY : DONE)
        try:
            # todo not(avoid) use number in variable : DONE
            try:
                surl_token = ShortURL.objects.get(surl=token)
                decoded_token = util.decode_token(surl_token.lurl)
                user = User.objects.get(email=list(decoded_token.values())[0])
            except:
                raise ValueError('Invalid token')
            password = request.data['password']
            confirm_password = request.data['confirm_password']

            if password != confirm_password:
                logger.error('password not match')
                raise Exception('Your password does not match!')
            elif not util.password_validator(password):
                logger.error('short password length')
                raise ValueError('Minimum required 5 characters')

            user.set_password(password)
            user.save()
            response = util.smd_response(success=True, message='Your password is successfully update',
                                         http_status=status.HTTP_201_CREATED)
            logger.info('password update successfully')
        except Exception as exception_detail:
            logger.error('Invalid token')
            response = util.smd_response(message=str(exception_detail), http_status=status.HTTP_400_BAD_REQUEST)
        return response


class Upload(GenericAPIView):
    """
    upload file use to upload our file like image for profile pic upload
    """

    serializer_class = UploadSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        :param request: request file details which user need to post
        :return: response in smd format
        """
        
        # todo use key for user : DONE (key is user_id)
        try:
            # file_serialize = UploadSerializer(data=request.data)
            file_serialize = UploadSerializer(data=request.data)

            if file_serialize.is_valid():
                file_serialize.save(user_id=request.user.id)
                response = util.smd_response(success=True, message='You file is successfully uploaded',
                                             data={'image_url': file_serialize.data['image']},
                                             http_status=status.HTTP_201_CREATED)
                logger.info('file uploaded')
            else:
                logger.error('UploadSerializer serializer data not valid')
                response = util.smd_response(message='file not uploaded', http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            response = util.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        return response


class ImageUpdate(GenericAPIView):
    """
    upload file use to update our file like image for profile pic update
    """

    serializer_class = UploadSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        """
        :param image_id:
        :param request: request file details which user need to post
        :return: response in smd format
        """
        try:
            instance = UserProfile.objects.get(user_id=request.user.id)

            file_serialize = UploadSerializer(instance, data=request.FILES, partial=True)
            if not 'image' in file_serialize.initial_data:
                logger.error('image field not present')
                raise KeyError('image field not present')

            if file_serialize.is_valid():
                file_serialize.save()
                
                response = util.smd_response(success=True, message='You file is successfully update',
                                             data={'image_url': file_serialize.data['image']},
                                             http_status=status.HTTP_200_OK)
                logger.info('update successfully')
                # return HttpResponse(response)
            else:
                logger.error('Image serializer data not valid.')
                response = util.smd_response(message='file not update', http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            response = util.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(response)


def activate(request, token):
    """
    :param request: request use for which user is requesting for activate there account
    :param token: token is in jwt encoded it is in short length by using django shortUrl
    :return: response of user request
    """
    try:
        try:
            token = ShortURL.objects.get(surl=token)
            decoded_token = util.decode_token(token.lurl)
            user = User.objects.get(username=list(decoded_token.keys())[0])
        except Exception as e:
            logger.error('Invalid token')
            user = None
        if user is not None:
            if not user.is_active:
                user.is_active = True
                user.save()
                response = util.smd_response(success=True,
                                             message='Thank you for confirmation.',
                                             http_status=status.HTTP_202_ACCEPTED)
                logger.info('user email confirmation done')
                # return request.get("http://localhost:4200/login")
            else:
                logger.error('linked already used')
                response = util.smd_response(message='Link already used',
                                             http_status=status.HTTP_208_ALREADY_REPORTED)
        else:
            response = util.smd_response(message='link is not correct',
                                         http_status=status.HTTP_400_BAD_REQUEST)
    except:
        response = util.smd_response(message='something is wrong',
                                     http_status=status.HTTP_404_NOT_FOUND)
    return response


def social_login(request):
    """
    :param request: social login request with user social profile
    :return: render on social login page
    """
    
    try:
        logger.info('social login')
        url = request.build_absolute_uri(reverse('userlogin:login'))
        return render(request, 'login.html', {'link': url})
    except:
        return util.smd_response(message='something is wrong', http_status=status.HTTP_404_NOT_FOUND)


# @login_required
@check_login
def home(request):
    """
    :param request: request for share data on social links
    :return:
    """
    try:
        url = request.build_absolute_uri()
        return render(request, 'home.html', {'link': url})
    except:
        return util.smd_response(message='something is wrong', http_status=status.HTTP_404_NOT_FOUND)


class SessionLogin(GenericAPIView):
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
        
        # Todo create required validation : DONE
        try:
            serialized_data = LoginSerializer(data=request.data)
            if not 'username' in serialized_data.initial_data or not 'password' in serialized_data.initial_data:
                logger.error('username or password field not present')
                raise EnvironmentError('username or password field not present')
            if not serialized_data.is_valid():
                logger.error('LoginSerializer serialized data not valid')
                raise ValueError('please enter valid', [k for k in serialized_data.errors.keys()])
            username = serialized_data.data['username']
            password = serialized_data.data['password']

            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)

                from django.contrib.sessions.backends.db import SessionStore
                ss = SessionStore()
                ss[user.username] = user.pk
                ss.create()
                response = util.smd_response(success=True, message="You are successfully login", data=user.id,
                                             http_status=status.HTTP_201_CREATED)
                logger.info('user successful login.')
            else:
                logger.error('Incorrect credential')
                response = util.smd_response(message="Incorrect credential",
                                             http_status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception_detail:
            response = util.smd_response(message=str(exception_detail), http_status=status.HTTP_400_BAD_REQUEST)
        return response


class GetProfilePic(GenericAPIView):
    serializer_class = UploadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        :param request: request file details which user need to get
        :return: response in smd format
        """
        try:
            user = User.objects.get(id=request.user.id)
            user_detail = UserProfile.objects.filter(user_id=user.id)
            image = UploadSerializer(user_detail, many=True)
            
            user_info = {
                'username': user.username,
                'email': user.email,
                'image_url': None
            }
            if len(image.data) > 0:
                user_info['image_url'] = image.data[0]['image']
                response = util.smd_response(success=True, message='You file is successfully uploaded',
                                             data=user_info,
                                             http_status=status.HTTP_200_OK)
            else:
                logger.error('Image not found')
                response = util.smd_response(message='image not found', data=user_info, http_status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(e)
            response = util.smd_response(message=str(e), http_status=status.HTTP_400_BAD_REQUEST)
        return response
