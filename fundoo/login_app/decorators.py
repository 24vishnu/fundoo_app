import json
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse
from .redis import redis_db


def login_decorator(function):

    def wrapper(request):

        smd = {
            "success": False,
            "message": "not a vaild user",
            'data': []
        }

        try:
            header = request.META["HTTP_AUTHORIZATION"]
            token_decode = header.split(" ")
            decode = jwt.decode(token_decode[1], settings.SECRET_KEY)
            print('ccccccccccccccccc', decode)
            user = User.objects.get(id=decode['user_id'])
            print('ddddddddddddddddddd', user)
            # red_obj = RedisConnection()  # red object is created
            print('eeeeeeeeeeeeeeeee')
            redis_db.get(user.username)
            print('ffffffffffffffffffff')
            return function(request)
        except (Exception, TypeError):
            HttpResponse(json.dumps(smd))

    return wrapper
