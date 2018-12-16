import redis


# r = redis.Redis(host='localhost', port=6379, decode_responses=True)
#
# r.set('name', 'xiaoming')
# print(r['name'])
# print(r.get('name'))
# print(type(r['name']))

# 使用连接池
pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
r.set('name', 'xiaohua')
print(r.get('name'))

data = {
    'name': 'aaa',
    'id': 1
}
#
# data2 = {
#     'name': 'bbb',
#     'id': 2
# }
#
# data3 = {
#     'name': 'ccc',
#     'id': 3
# }
#
r.hmset("aaa", data)
# r.hmset('a', data2)
# r.hmset('a', data3)
#
res = r.hgetall("aaa").get("name")
print(res)
