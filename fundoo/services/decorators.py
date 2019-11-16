import json
import pdb

import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from docutils.nodes import status
from rest_framework import status

from .redis import redis_db
from .util import smd_response


def login_decorator(function):
    def wrapper(request):

        response = smd_response(message="You are not logged in", http_status=status.HTTP_401_UNAUTHORIZED)
        # pdb.set_trace()
        try:
            header = request.META["HTTP_AUTHORIZATION"]
            print(header)
            header = header.split(' ')
            decode = jwt.decode(header[1], settings.SECRET_KEY)
            user = User.objects.get(id=decode['user_id'])
            if redis_db.get(user.username) is not None:
                return function(request)
            else:
                if user is not None:
                    return function(request)
        except (TypeError, Exception):
            return response

    return wrapper


def check_login(function):
    def wrapper(request):
        try:
            users = User.objects.values_list('username', flat=True)
            if request.user.username in users:
                return function(request)
            else:
                return redirect('/sessionlogin')
        except (TypeError, Exception):
            return redirect('/sessionlogin')

    return wrapper
