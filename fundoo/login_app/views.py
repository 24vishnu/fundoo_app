"""In views.py file we implement the all required view api,s """
import json

import jwt
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializer import RegistrationSerializer, LoginSerializer, PasswordResetSerialize, ForgotPasswordSerializer


# pylint: disable=line-too-long
# pylint: disable= no-self-use
class UserRegistration(GenericAPIView):
    """
    Following class is implement for register a new user and send a verification link
    for activate there profile
    """

    # we need to include serialize class
    serializer_class = RegistrationSerializer

    def get(self, request):
        """
        :param request:
        :return:
        """
        return render(request, 'login_pages/registration.html')

    def post(self, request):
        """
        :param request: user request for send information for register the user
                        request parameters are username, email and password
        :return: we send a activation link on user given mail if user input is valid
        """

        username = request.data['username']
        email = request.data['email']
        password = request.data['password']

        try:
            # check given email is valid or not
            validate_email(email)
        except Exception:
            return HttpResponse(json.dumps("not a vaild email"))

        # check user enter any empty field or not if any field is empty then give error
        if username == "" or email == "" or password == "":
            return HttpResponse(json.dumps("Error :field should not be empty."))

        try:
            # if all user input data is correct then create user profile with given name, email and password and
            # then save in database

            user = User.objects.create_user(username=username, email=email, password=password)  # , is_active=False)
            user.save()

            # Get current site
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'

            # create jwt token this token is in byte form therefor we decode and convert into string format
            jwt_token = jwt.encode({user.username: user.email}, 'private_key', algorithm='HS256').decode("utf-8")

            email = EmailMessage(
                mail_subject,
                'http://' + str(current_site.domain) + '/login/activate/' + jwt_token + '/',
                to=[email]
            )
            # send message(activation link) on user given mail address
            email.send()

            return HttpResponse("Your profile successfully created now please activate your account")

        except (TypeError, ValueError, OverflowError, Exception):
            return HttpResponse(json.dumps("Database Error."))

    # def activate(self, request, token):
    #     decoded_token = jwt.decode(token, 'private_key', algorithms='HS256')
    #
    #     # check given token information is store in database or not
    #     try:
    #         user = User.objects.get(username=list(decoded_token.keys())[0])
    #     except(TypeError, ValueError, OverflowError, User.DoesNotExist):
    #         # if this is not store in our database then user should have first signup because user in invalid
    #         return HttpResponse('you are not registered yet, please sign up first')
    #         # user = None
    #     if user is not None and not user.is_active:
    #         # if user valid then activate user account and save
    #         user.is_active = True
    #         user.save()
    #         # login(request, user)
    #         return render(request, 'login_pages/confirm_mail.html')
    #     else:
    #         # this link already activated or (this link was one time use )
    #         return render(request, template_name='login_pages/home.html')


# pylint: disable=line-too-long
# pylint: disable= no-self-use
class UserLogin(GenericAPIView):
    """
    login method use for login any user,
    if it is valid user otherwise print error
    """

    # we need to include serialize class
    serializer_class = LoginSerializer

    def get(self, request):
        """
        :param request:
        :return:
        """
        return render(request, 'login_pages/login_page.html')

    def post(self, request):
        """
        :param request: username and password for login
        :return: if username and password is correct then response login success other wise give error
        """
        username = request.data['username']
        password = request.data['password']

        if username == "" or password == "":
            messages.info(request, "Username/password should not be empty")
            return HttpResponse(json.dumps("Username/password should not be empty"))
        try:
            user = User.objects.get(username=username)

            # authenticate username and password valid or not
            if authenticate(username=username, password=password) is not None:
                jwt_token = jwt.encode({user.username: user.email}, 'private_key', algorithm='HS256').decode("utf-8")
                messages.info(request, jwt_token)
                return HttpResponse(content='you are successfully login' + '\n Token :' + jwt_token)

        except (TypeError, ValueError, OverflowError, Exception):
            messages.info(request, "Incorrect Username/password")
        return HttpResponse(json.dumps('Incorrect Username/password'))


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

    def get(self):
        """
        :return: this project get request not allowed
        """
        return HttpResponse(json.dumps("Get request not allowed"))

    def post(self, request):
        """
        :param request: take user email address for sending reset password link
        :return:
        """
        email = request.data['email']
        try:
            validate_email(email)
            if email == "":
                messages.info(request, "field should not be empty.")
                raise Exception
            user = User.objects.get(email=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset your Password account.'
            jwt_token = jwt.encode({user.username: user.email}, 'private_key', algorithm='HS256').decode("utf-8")
            to_email = user.email

            email = EmailMessage(
                mail_subject,
                'http://' + str(current_site.domain) + '/ResetPassword/' + jwt_token + '/',
                to=[to_email]
            )
            email.send()
            return HttpResponse(content='http://' + str(current_site.domain) + '/ResetPassword/' + str(jwt_token))
        except Exception:
            # return render(request, 'login_pages/forgot_password.html')
            return HttpResponse(json.dumps("Email does not exist in database"))


# pylint: disable=line-too-long
# pylint: disable= no-self-use
class ResetPassword(GenericAPIView):
    """
    Reset password class is used for user password change password
    """
    # include the serializer class of reset password serializer
    serializer_class = PasswordResetSerialize

    def get(self):
        """
        :return:
        """
        return HttpResponse("Get request not allowed")

    def post(self, request):
        """
        :param request: take the user input as username, password and confirm password
        :return: if user name is exist then send response password set successfully
                 other wise print error message
        """

        username = request.data['username']
        password1 = request.data['password1']
        password2 = request.data['password2']

        try:
            if password1 == "" or password2 == "":
                return HttpResponse(json.dumps('password should not be empty!'))

            if password1 != password2:
                return HttpResponse(json.dumps('Your password does not match!'))

            user = User.objects.get(username=username)

            if user is not None or user is not "AnonymousUser":
                user.set_password(password1)
                user.save()
                messages.info(request, "password reset done")
                return HttpResponse('password Reset Done')

        except (ValueError, Exception):
            return HttpResponse(json.dumps("Incorrect Username"))


# pylint: disable=line-too-long
# pylint: disable= no-self-use
class UserProfile(GenericAPIView):
    """
    user profile class is used this will display if user is authenticated
    """

    # include the serialize class and permission class (IsAuthenticated)
    serializer_class = LoginSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        :param request:
        :return:
        """
        return HttpResponse("Get request not allowed")

    def post(self, request):
        """
        :param request:
        :return:
        """
        return HttpResponse("You/I are/am authenticated user")
