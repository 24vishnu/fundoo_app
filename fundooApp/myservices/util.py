def smd_response(success, message, data):
    response = {
        'success': success,
        'message': message,
        'deta': data
    }
    return response
