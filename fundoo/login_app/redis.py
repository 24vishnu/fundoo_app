import redis

redis_db = redis.StrictRedis(host="localhost", db=0, port=6379)
