import pymongo


class Mongodb:

    def __init__(self, host='localhost', port=27017):
        self.host = host
        self.port = port

    def create_db(self):
        client = pymongo.MongoClient(host=self.host, port=self.port)
        db = client.bilibili

        return db

    def save_getinfo_mongodb(self, result):
        """
        将用户个人信息保存到mongodb
        """
        db = self.create_db()
        collection = db.myinfo
        user = collection.find_one({'mid': result.get('mid')})
        if user:
            print('{} 在数据库已存在'.format(user['name']))
        else:
            collection.insert(result)
            print('{} 保存到数据库成功'.format(result.get('name')))