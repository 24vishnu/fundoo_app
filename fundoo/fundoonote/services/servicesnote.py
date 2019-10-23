import logging
import os
import re

import jwt
from django.contrib.auth import get_user_model
SECRET_KEY = os.getenv("SECRET_KEY")
User = get_user_model()


def smd_response(success, message, data):
    response = {
        'success': success,
        'message': message,
        'data': data
    }
    return response


def valid_email(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if re.search(regex, email):
        return True
    else:
        return False


def create_token(payload):
    jwt_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode("utf-8")
    return jwt_token


def decode_token(token):
    original_value = jwt.decode(token, SECRET_KEY, algorithms='HS256')
    return original_value
