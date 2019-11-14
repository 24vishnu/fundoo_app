import redis

# from fundoo.url_settings import redis_port, r_db
from fundoo.settings import r_db, redis_port

redis_db = redis.StrictRedis(host="localhost", db=r_db, port=redis_port)

def redis():
    return redis_db
