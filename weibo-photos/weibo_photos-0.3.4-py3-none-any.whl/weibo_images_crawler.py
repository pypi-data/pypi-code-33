import requests
import pickle
import getpass
import json
import re
import os
import time
import sqlite3
from . import auth, db

class WeiboImageCrawler(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Referer': 'https://webo.com/'
    }
    pic_url = 'http://photo.weibo.com/photos/get_all?uid=%s&album_id=%s&count=30&page=%d&type=%s&__rnd=%d'
    album_url = 'http://photo.weibo.com/albums/get_all?uid=%s&page=%d&count=20&__rnd=%d'

    def __init__(self, user_id=None):
        self.user_id = user_id
        requests.packages.urllib3.disable_warnings()
        self.s = requests.Session()
        self.sql = db.SQLiteHelper('wp.db')
        self.albums = []
        self.images = []
        
    def init_requests(self):
        self.s.headers = self.headers
        self.s.verify = False
        file_name = 'cookies'
        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                self.s.cookies.update(pickle.load(f))
                print('从保存的cookies文件中成功读取到cookies！')
                test_res = self.test_cookies()
                if test_res:
                    return
                else:
                    print('该cookies文件错误或者失效！请重新登录！')
        else:
            print('没有可用的cookies，请登录！')
        username = input('请输入您的微博用户名:')
        password = getpass.getpass('请输入您的微博密码：')
        auth.login(self.s, username, password)

    def test_cookies(self):
        '''测试下cookies是否错误或者失效'''
        r = self.s.get('https://weibo.com/')
        url = r.url
        index = url.find('passport')
        if index == -1:
            return True
        return False
    
    # 根据用户名搜索信息
    def search_user(self, search_key):
        search_url = 'https://s.weibo.com/ajax/topsuggest.php'
        timestamp = int(time.time() * 1e5)
        payloads = {
            'key': search_key,
            '_k': str(timestamp),
            'uid': '',
            '_t': '1',
            '_v': 'STK_%d' % (timestamp + 1)
        }
        r = self.s.get(search_url, params=payloads)
        r.raise_for_status()
        text = r.text
        left_index = text.find('(')
        right_index = text.find(')')
        text = text[(left_index + 1) : right_index]
        res_dict = json.loads(text)
        users = res_dict['data']['user']
        print('共查找到{}个用户！'.format(len(users)))
        for user in users:
            print('名称:{}, id:{}, 性别:{}, 是否是大V:{}, 粉丝数:{}'.format(user['u_name'], user['u_id'], user['sex'], user['is_v'], user['fans_n']))

    # 相册列表每次都更新
    def get_album_info(self):
        if self.user_id is None:
            raise Exception('未设置用户ID')
        is_table_exist = self.sql.check_table_exists('ALBUMS')
        if not is_table_exist:
            self.sql.create_albums_table()
        i = 1
        while True:
            time_stamp = WeiboImageCrawler.get_timestamp()
            url = self.album_url % (self.user_id, i, time_stamp)
            r = self.s.get(url)
            r.raise_for_status()
            res_dict = r.json()
            if res_dict['code'] != 0:
                raise Exception('Wrong response!')
            album_list = res_dict['data']['album_list']
            if len(album_list) == 0:
                self.sql.clear_table('ALBUMS')
                for album in self.albums:
                    self.sql.insert_albums_table(album)
                return
            self.albums.extend(album_list)
            i += 1

    def get_images_address(self, album_id, album_type):
        if self.user_id is None:
            raise Exception('未设置用户ID')
        is_table_exist = self.sql.check_table_exists('PHOTOS')
        if not is_table_exist:
            self.sql.create_photos_table()
        else:
            images = self.sql.get_images(album_id)
            if len(images) > 0:
                self.images = images
        i = 1
        print('正在获取图片地址...')
        while True:
            time_stamp = WeiboImageCrawler.get_timestamp()
            url = self.pic_url % (self.user_id, album_id, i, album_type, time_stamp)
            r = self.s.get(url)
            r.raise_for_status()
            res_dict = r.json()
            if res_dict['code'] != 0:
                raise Exception('Wrong response!')
            print('获得第%d页的数据！' % i)
            photo_list = res_dict['data']['photo_list']
            if len(photo_list) == 0:
                print('获取图片地址完成！总共获取%d张图片！' % len(self.images))
                return
            for photo in photo_list:
                is_exist = self.is_images_in_memory(photo)
                if not is_exist:
                    self.sql.insert_photos_table(photo)
                    self.images.append(photo)
                else:
                    print('获取图片地址完成！总共获取%d张图片！' % len(self.images))
                    return
            i += 1
            time.sleep(0.1) # 暂停一下，防止被识出是爬虫

    def get_image_url(self, image):
        host = image['pic_host']
        name = image['pic_name']
        url = '{}/large/{}'.format(host, name)
        return url

    def write_images_address(self, album_id):
        if self.user_id is None:
            raise Exception('未设置用户ID')
        image_file = '{}-{}.txt'.format(self.user_id, album_id)
        with open(image_file, 'w') as f:
            for image in self.images:
                image_url = self.get_image_url(image)
                f.write(image_url)
                f.write('\n')
    
    def save_all_images(self, user_id, album_id, save_dir):
        if self.user_id is None:
            raise Exception('未设置用户ID')
        if save_dir is not None:
            if not os.path.exists(save_dir):
                print('错误的路径！')
                return
            output_dir = '{}/{}-{}'.format(save_dir, user_id, album_id)
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            os.chdir(output_dir)
        for image in self.images:
            image_name = image['pic_name']
            caption = image['caption_render']
            path = '{}/{}'.format(output_dir, image_name)
            if os.path.exists(path):
                print('{}已存在，跳过！'.format(image_name))
                continue
            image_url = self.get_image_url(image)
            cmd = 'curl -O {} -#'.format(image_url)
            print('->{}({})'.format(image_name, caption))
            os.system(cmd)
    
    def is_images_in_memory(self, photo):
        name = photo['pic_name']
        for image in self.images:
            if image['pic_name'] == name:
                return True
        return False  
    
    def print_albums_info(self):
        for album in self.albums:
            album_id = album['album_id']
            album_caption = album['caption']
            album_type = album['type']
            photos_count = album['count']['photos']
            info = '相册专辑ID：%s, 相册名称: %s, 相册类型: %s, 包含相片数量: %s' % (album_id, album_caption, album_type, photos_count)
            print(info)

    @staticmethod
    def get_timestamp():
        return int(round(time.time() * 1000))

    @staticmethod
    def parse_cookies_from_browser(web_cookies):
        cookies_list = web_cookies.split(';')
        cookies = {}
        for cookie in cookies_list:
            cookie = cookie.strip()
            pair = cookie.split('=')
            try:
                key = pair[0]
                value = pair[1]
                cookies[key] = value
            except:
                raise Exception('cookies is error!')
        return cookies 
    