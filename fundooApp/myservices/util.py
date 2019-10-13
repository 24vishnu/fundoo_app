import re


def smd_response(success, message, data):
    response = {
        'success': success,
        'message': message,
        'deta': data
    }
    return response


def valid_email(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if re.search(regex, email):
        return True
    else:
        return False
