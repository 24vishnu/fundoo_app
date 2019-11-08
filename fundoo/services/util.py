import logging
import os
import re

import jwt
import redis
import requests
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import status

from fundoo.settings import file_handler

from fundoo.url_settings import r_db, redis_port
from fundoonote.models import FundooNote, Label
from fundoonote.serializers import NotesSerializer
from rest_framework.response import Response

redis_db = redis.StrictRedis(host="localhost", db=r_db, port=redis_port)
SECRET_KEY = os.getenv("SECRET_KEY")
activate_secret_key = os.getenv("REGISTRATION_SECRET_KEY")
reset_secret_key = os.getenv("FORGOT_PASSWORD_SECRET_KEY")

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


def token_encode(original_data):
    token = requests.post(url=os.getenv("TOKEN_URL"), data=original_data)
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


def write_through(request):
    logger.info("No data found in redis cache" + ' for %s', request.user)
    get_note = FundooNote.objects.filter(user_id=request.user.id)
    note_data = NotesSerializer(get_note, many=True)
    try:
        for i in range(len(note_data.data)):
            note_data.data[i]['label'] = [Label.objects.get(id=x).name
                                          for x in note_data.data[i]['label']]
            note_data.data[i]['collaborate'] = [User.objects.get(id=x).email
                                                for x in note_data.data[i]['collaborate']]
    except Exception:
        raise ValueError("some data not present in database")
    i = 0
    logger.info("insert notes into redis cache" + ' for %s', request.user)
    for data in note_data.data:
        redis_db.hmset(str(request.user.id) + 'note',
                       {get_note.values()[i]['id']: {k: v for k, v in data.items()}})
        i += 1


if __name__ == '__main__':
    pass
