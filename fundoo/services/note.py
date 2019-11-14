import ast
import logging

import redis
from django.contrib.auth import get_user_model

from fundoo.settings import file_handler, r_db, redis_port
from fundoonote.models import FundooNote, Label
from fundoonote.serializers import NotesSerializer

redis_db = redis.StrictRedis(host="localhost", db=r_db, port=redis_port)

User = get_user_model()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


def write_through(request):
    user_redis_note = redis_db.hgetall(str(request.user.id) + 'note')
    logger.info("fetch user notes from redis cache" + ' for %s', request.user)
    if len(user_redis_note) < 1:
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
                           {str(get_note.values()[i]['id']): str({k: v for k, v in data.items()})})
            i += 1

    user_redis_note = redis_db.hgetall(str(request.user.id) + 'note')

    user_redis_note = [{
        ast.literal_eval(user_note_id.decode('utf-8')): ast.literal_eval(user_note_value.decode('utf-8'))
    }
        for user_note_id, user_note_value in user_redis_note.items()]

    return user_redis_note
