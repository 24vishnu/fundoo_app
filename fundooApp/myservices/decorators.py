import json
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse
from .redis import redis_db


def login_decorator(function):
    def wrapper(request):

        response = {
            "status": False,
            "message": "you are not a valid user",
            'data': []
        }

        try:
            header = request.META["HTTP_AUTHORIZATION"]
            print(header)
            decode = jwt.decode(header, settings.SECRET_KEY)
            user = User.objects.get(username=decode['username'])
            if redis_db.get(user.username) is not None:
                return function(request)
        except (Exception, TypeError):
            return HttpResponse(json.dumps(response))

    return wrapper
