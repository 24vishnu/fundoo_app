import ast
import json
import logging
import os
import pdb
import re

import jwt
import redis
import requests
from decouple import config
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from fundoo.settings import file_handler, r_db, redis_port


redis_db = redis.StrictRedis(host="localhost", db=r_db, port=redis_port)
SECRET_KEY = config("SECRET_KEY")
activate_secret_key = config("REGISTRATION_SECRET_KEY")
reset_secret_key = config("FORGOT_PASSWORD_SECRET_KEY")

User = get_user_model()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


def smd_response(success=False, message='', data=None, http_status=None):
    if data is None:
        data = []
    if http_status is None:
        http_status = status.HTTP_400_BAD_REQUEST
    response = {
        'success': success,
        'message': message,
        'data': data
    }
    # return Response(response, status=http_status)
    return JsonResponse(response, status=http_status)


def valid_email(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if re.search(regex, email):
        return True
    else:
        return False


def create_token(payload):
    # jwt_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    jwt_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode("utf-8")
    return jwt_token


def decode_token(token):
    original_value = jwt.decode(token, SECRET_KEY, algorithms='HS256')
    return original_value


def token_encode(original_data):
    # pdb.set_trace()
    token = requests.post(url=config("TOKEN_URL"), data=original_data)
    token1 = token.json()['access']
    return token1


def password_validator(password):
    error = ''

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{5,20}$"
    reg = '^(?=.{5,50}$).*'
    # compiling regex
    pat = re.compile(reg)
    # searching regex
    mat = re.search(pat, password)
    # validating conditions 
    if mat:
        return True
    else:
        return False
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # while True:
    #     if len(password) < 5:
    #         # flag = -1
    #         # error = 'Minimum 5 characters'
    #         # break
    #         return False
    #     # elif not re.search("[a-z]", password):
    #     #     flag = -1
    #     #     error = 'The alphabets must be between [a-z]'
    #     #     break
    #     # elif not re.search("[A-Z]", password):
    #     #     flag = -1
    #     #     error = 'At least one alphabet should be of Upper Case [A-Z]'
    #     #     break
    #     # elif not re.search("[0-9]", password):
    #     #     flag = -1
    #     #     error = 'At least 1 number or digit between [0-9].'
    #     #     break
    #     # elif not re.search("[_@$]", password):
    #     #     flag = -1
    #     #     error = 'At least 1 character from [ _ or @ or $ ].'
    #     #     break
    #     else:
    #         return True


def activate_jwt_token(payload):
    token = jwt.encode(payload, activate_secret_key, algorithm='HS256').decode('utf-8')
    return token


def decode_activate_token(token):
    original_value = jwt.decode(token, activate_secret_key, algorithms='HS256')
    return original_value


def password_jwt_encode(payload):
    token = jwt.encode(payload, reset_secret_key, algorithm='HS256').decode('utf-8')
    return token


def password_jwt_decode(token):
    original_value = jwt.decode(token, reset_secret_key, algorithms='HS256')
    return original_value


if __name__ == '__main__':
    pass
