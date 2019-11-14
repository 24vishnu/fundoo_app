import json

import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from docutils.nodes import status
from rest_framework import status

from .redis import redis_db
from .util import smd_response


def login_decorator(function):
    def wrapper(request):

        response = smd_response(message="You are not logged in", http_status=status.HTTP_401_UNAUTHORIZED)

        try:
            if request.COOKIES.get(settings.SESSION_COOKIE_NAME):
                user = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
                if user:
                    return function(request)
                else:
                    return response
            else:
                header = request.META["HTTP_AUTHORIZATION"]
                print(header)
                decode = jwt.decode(header, settings.SECRET_KEY)
                if redis_db.get(decode['username']) is not None:
                    return function(request)
                else:
                    user = User.objects.get(username=decode['username'])
                    if user is not None:
                        return function(request)
        except (TypeError, Exception):
            return response

    return wrapper
