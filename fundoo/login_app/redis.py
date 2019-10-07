import redis
red = redis.StrictRedis(host="localhost", db=0, port=6379)


class RedisConnection:
    def set(self, key, value):
        red.set(key, value)

    def get(self, key):
        red.get(key)

    def delete(self, key):
        red.delete(key)