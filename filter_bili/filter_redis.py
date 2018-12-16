import redis


class FilterRedis:

    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port

    def create_filter(self):
        pool = redis.ConnectionPool(host=self.host, port=6379, decode_responses=True)
        r = redis.Redis(connection_pool=pool)

        return r

    def save_flowers_mongodb(self, result):
        """
        将关注的用户信息和粉丝信息保存
        """
        r = self.create_filter()
        user_id = result["user_id"]

        if r.hkeys(user_id):
            print('{} 在数据库已经存在'.format(r.hgetall(user_id).get("user_name")))
        else:
            r.hmset(user_id, result)
            print('保存用户{} 的关注信息和粉丝信息到数据库'.format(result.get('user_name')))
            print('============================================')
