import os
import re

import jwt
import requests
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import status

SECRET_KEY = os.getenv("SECRET_KEY")
User = get_user_model()


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
    return JsonResponse(response, status=http_status)


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


def token_encode(uer):
    print('-==========-=-=-=--==--------------===',os.getenv("TOKEN_URL"))
    token = requests.post(url=os.getenv("TOKEN_URL"), data=uer)
    token1 = token.json()['access']
    return token1


def password_validator(password):
    error = ''

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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



if __name__ == '__main__':
    payload = {
        "A": 'a',
        "B": 'b'
    }
    token_encode(payload)
