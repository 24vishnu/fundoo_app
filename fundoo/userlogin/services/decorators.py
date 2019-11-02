import jwt
from django.conf import settings
from django.contrib.auth.models import User
from docutils.nodes import status
from rest_framework import status

from .redis import redis_db
from .util import smd_response


def login_decorator(function):
    def wrapper(request):

        response = smd_response(False, "You are not logged in", [], status.HTTP_401_UNAUTHORIZED)

        try:
            header = request.META["HTTP_AUTHORIZATION"]
            print(header)
            decode = jwt.decode(header, settings.SECRET_KEY)
            if redis_db.get(decode['username']) is not None:
                return function(request)
            else:
                user = User.objects.get(username=decode['username'])
                if user is not None:
                    return function(request)
        except (Exception, TypeError):
            return response

    return wrapper
