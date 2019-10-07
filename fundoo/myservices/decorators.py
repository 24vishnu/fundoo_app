import json
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse
from .redis import RedisConnection


def login_decorator(function):
    """
    :param function: function is called
    :return: will check token expiration
    """

    def wrapper(request):
        """
        :return: will check token expiration
        """
        smd = {
            "success": False,
            "message": "not a vaild user",
            'data': []
        }

        try:

            header = request.META["HTTP_AUTHORIZATION"]
            token = header.split(" ")
            decode = jwt.decode(token[1], settings.SECRET_KEY)
            user = User.objects.get(username=decode['username'])
            red_obj = RedisConnection()  # red object is created
            red_obj.get(user.username)
            return function(request)
        except (Exception, TypeError):
            HttpResponse(json.dumps(smd))

    return wrapper
