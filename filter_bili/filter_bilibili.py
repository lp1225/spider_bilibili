import requests
import time
from requests.exceptions import ConnectionError

from filter_bili.filter_redis import FilterRedis
from filter_bili.mongo_db import Mongodb

MID = 0
MIN = 0


def get_space(user_id, mongo):
    """
    进入用户个人空间
    """
    try:
        headers = {
            'Host': 'space.bilibili.com',
            'Referer': 'https://www.bilibili.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Cookie': ''
        }
        url = 'https://space.bilibili.com/' + str(user_id)
        response = requests.get(url, headers=headers, timeout=60)
        if response.status_code == 200:
            print('bilibili用户主页url：{}'.format(url))
            print('成功进入用户主页')
            # 获取用户个人信息
            get_userinfo(user_id, mongo)
        else:
            print('进入bilibili用户主页失败---code {}'.format(response.status_code))
    except ConnectionError as e:
        print('网络连接异常', e.args)


def get_userinfo(user_id, mongo):
    """
    获取用户个人信息
    """
    try:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'space.bilibili.com',
            'Origin': 'https://space.bilibili.com',
            'Referer': 'https://space.bilibili.com/' + str(user_id),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        url = 'http://space.bilibili.com/ajax/member/GetInfo'
        data = {
            'mid': str(user_id)
        }
        response = requests.post(url, headers=headers, data=data, timeout=60)
        if response.status_code == 200:
            print('获取用户个人信息成功')
            status = response.json()
            if status.get('data'):
                data = status.get('data')
                regtimez = time.localtime(data.get('regtime'))
                regtime = time.strftime("%Y-%m-%d %H:%M:%S", regtimez)
                result = {
                    'mid': data.get('mid'),
                    'name': data.get('name'),
                    'sex': data.get('sex'),
                    'regtime': regtime,
                    'birthday': data.get('birthday'),
                    'sign': data.get('sign')
                }
                print('用户个人信息:{}'.format(result))
                # 得到用户个人信息保存到数据库
                mongo.save_getinfo_mongodb(result)

            else:
                print('获取用户个人信息失败,code {}'.format(response.status_code))

    except ConnectionError as e:
        print('网络连接异常', e.args)


def get_myinfo(user_id):
    """
    获取用户关注数量的和粉丝数量
    """
    try:
        headers = {
            'Connection': 'keep-alive',
            'Cookie': '',
            'Host': 'api.bilibili.com',
            'Referer': 'https://space.bilibili.com/' + str(user_id),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        url = 'http://api.bilibili.com/x/relation/stat?vmid={}&jsonp=jsonp'.format(user_id)
        print('获取用户关注数量和粉丝的数量。。。')
        response = requests.get(url, headers=headers, timeout=60)
        if response.status_code == 200:
            status = response.json()
            if status.get('data'):
                data = status.get('data')
                # 粉丝
                follower = data.get('follower')
                # 关注
                following = data.get('following')
                print('关注数量:{}, 粉丝数量:{}'.format(following, follower))
                return following, follower
            else:
                print('get_myinfo url失败 code:{}'.format(response.status_code))
    except ConnectionError as e:
        print('ConnectionError网络异常', e.args)


def get_following(user_id, page, filter, mongo):
    """
    获取关注用户信息
    """
    try:
        headers = {
            'Connection': 'keep-alive',
            'Cookie': '',
            'Host': 'api.bilibili.com',
            'Referer': 'https://space.bilibili.com/' + str(user_id),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        url = 'http://api.bilibili.com/x/relation/followings?vmid={}&pn={}&ps=20&order=desc&jsonp=jsonp'.format(user_id, page)
        print('正在获取用户关注信息。。。')
        response = requests.get(url, headers=headers, timeout=60)
        if response.status_code == 200:
            status = response.json()
            if status.get('data'):
                content = status.get('data').get('list')
                if len(content) == 0:
                    return
                for item in content:
                    result = {
                        'user_name': item.get('uname'),
                        'user_id': item.get('mid')
                    }
                    print(result)
                    # 得到mid进入用户主页面
                    get_space(result.get('user_id'), mongo)
                    # 保存关注用户的信息
                    filter.save_flowers_redis(result)
        else:
            print('获取关注用户信息失败:{}'.format(response.status_code))

    except ConnectionError as e:
        print('ConnectionError网络异常', e.args)


def get_followers(user_id, page, filter, mongo):
    """
    获取粉丝信息
    """
    try:
        headers = {
            'Connection': 'keep-alive',
            'Cookie': '',
            'Host': 'api.bilibili.com',
            'Referer': 'https://space.bilibili.com/' + str(user_id),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        url = 'http://api.bilibili.com/x/relation/followers?vmid={}&pn={}&ps=20&order=desc&jsonp=jsonp'.format(user_id, page)
        print('正在获取粉丝信息。。。')
        response = requests.get(url, headers=headers, timeout=60)
        if response.status_code == 200:
            status = response.json()
            if status.get('data'):
                content = status.get('data').get('list')
                print(len(content))
                if len(content) == 0:
                    return
                for item in content:
                    result = {
                        'user_name': item.get('uname'),
                        'user_id': item.get('mid')
                    }
                    print(result)
                    # 得到mid进入用户主页面
                    get_space(result.get('user_id'), mongo)
                    # 保存粉丝用户user_id到数据库
                    filter.save_flowers_redis(result)
        else:
            print('获取所有粉丝用户信息失败{}'.format(response.status_code))
    except ConnectionError as e:
        print('ConnectionError网络异常', e.args)


def run(user_id, mongo, filter):
    # 进入用户主页
    get_space(user_id, mongo)
    time.sleep(0.5)

    # 获取关注的数量和粉丝的数量
    flowing, flower = get_myinfo(user_id)

    # 获取关注用户信息
    page = int(flower/20)+1
    if page <= 1:
        get_following(user_id, 1, filter, mongo)
    else:
        # b站限制最多查看5页
        if page > 5:
            page = 5
        for g_item in range(1, page):
            get_following(user_id, g_item, filter, mongo)

    # 获取粉丝信息
    f_page = int(flower/20)+1
    if f_page <= 1:
        get_followers(user_id, 1, filter, mongo)
    else:
        if f_page > 5:
            f_page = 5
        for g_item in range(1, f_page):
            get_followers(user_id, g_item, filter, mongo)

    # 循环
    rep_run(mongo)


def rep_run(mongo):
    """
    当上一个user_id所有事情完成后进入此函数进行循环爬取下一个user_id
    """
    global MIN
    MIN += 1
    print(MIN)
    db = mongo.create_db()
    collection = db.list
    # collection = db.list
    # 查询数据库所有的数据保存到result
    if collection.find_one({'id': MIN}):
        ran = collection.find_one({'id': MIN})
        # 查询数据有多少条
        count = collection.find({}).count()
        print(count)

        if MIN > count:
            print('程序即将停止运行')
            time.sleep(10)
            exit()
        else:
            data = ran.get('user_id')
            print(data)
            run(ran.get('user_id'))
    else:
        print('数据库没有该数据 id: {}'.format(MIN))


if __name__ == '__main__':
    mongo = Mongodb()
    filter = FilterRedis()
    id = '22520707'
    run(id, mongo, filter)