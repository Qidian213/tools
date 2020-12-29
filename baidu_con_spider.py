#coding:utf8

from queue import Queue
import json
from itertools import count
from datetime import datetime as dt
import time
import requests
import os
import threading

"""
发送请求
获取到content 转化为json
取出image_url 丢进队列
开多线程从队列取出image进行下载
"""

class BaiduSpider(object):
    base_url = r"http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&fp=result&queryWord={word}&cl=2&lm=-1&ie=utf-8&oe=utf-8&st=-1&ic=0&word={word}&face=0&istype=2nc=1&pn={pn}&rn=30"

    def __init__(self, word, sid, start, limit=50000, path='./image_spider'):
        self.picture_queue = Queue()
        self.message_queue = Queue()
        self.headers = {"user-agent":'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        self.word = word
        self.limit = limit
        self.lock = threading.Lock()
        self.lock2 = threading.Lock()
        self.index = start
        self.delay = 1.1
        self.count = (step for step in count(0, 30))  # 生成器用于生成列表页地址的step
        #if '车牌' in word:
        #    self.pic_head = '1'
        self.pic_head = sid
        self.pic_save_path = path + '/' + word + '/'
        if not os.path.exists(self.pic_save_path):
            os.makedirs(self.pic_save_path)
        self.log = self.word + '_log.txt'
        self.error_prefix = 'ERROR!!!:'
        self.err_log = self.word + '_err.txt'

    def send_url(self):
        message = '列表页线程执行，线程号: %s' % threading.current_thread()
        self.message_queue.put(message)
        print(message)
        while self.index < self.limit:
            if self.picture_queue.qsize() < 600:  # 如果队列消息小于600
                num = next(self.count)
                url = self.base_url.format(word=self.word, pn=num)
                try:
                    time.sleep(self.delay)
                    resp = requests.get(url, headers=self.headers, timeout=10)
                    content = resp.content.decode(errors='ignore')
                    json_data = json.loads(content)
                    data = json_data['data']
                    for item in data:
                        if item:
                            self.picture_queue.put(item['thumbURL'])
                except Exception as e:
                    message = self.error_prefix + str(dt.now()) + '一个列表页请求失败:' + url + '\n 错误信息：' + str(e)
                    self.message_queue.put(message)
                    print(message)
        message = '列表页请求完毕,线程号:%s' % threading.current_thread()
        print(message)

    def save_log(self):
        with open(self.log, 'w', encoding='utf-8') as f:
            while self.index < self.limit:
                message = self.message_queue.get()
                if self.error_prefix in message:
                    self.save_error(message)
                f.write(message + '\n')
                f.flush()

    def save_error(self, message):
        with open(self.err_log, 'a+') as f:
            f.write(message + '\n')

    def __getIndex(self):
        """获取文件编号"""
        self.lock.acquire()
        try:
            return self.index
        finally:
            self.index += 1
            self.lock.release()

    def save_picture(self):
        message = '下载图片线程执行，线程号: %s' % threading.current_thread()
        self.message_queue.put(message)
        print(message)
        while self.index < self.limit:
            url = self.picture_queue.get()

            # 加锁
            lock_flag = self.lock.acquire()
            if lock_flag:
                index = self.index
                self.index += 1
                self.lock.release()

            try:
                time.sleep(self.delay)
                resp = requests.get(url, headers=self.headers, timeout=10)
                with open(self.pic_save_path + self.pic_head + str(index) + '.jpg', 'wb') as f:
                    f.write(resp.content)
            except Exception as e:
                message = self.error_prefix + str(dt.now()) + '一张图片下载失败:' + url + '\n失败原因:' + str(e)
                self.message_queue.put(message)
                print(message)
                continue
            if index % 10 == 0:
                message = str(dt.now()) + '已下载%s张图片' % index
                self.message_queue.put(message)
                print(message)
        message = '图片下载完毕，当前线程退出：%s' % threading.current_thread()
        self.message_queue.put(message)
        print(message)

    def start(self):
        """run..."""
        print('=========程序运行========')
        print('图片保存在%s' % self.pic_save_path)
        thread_list = []
        # 创建3个线程来请求列表页并将url 放入队列
        for i in range(3):
            t = threading.Thread(target=self.send_url)
            thread_list.append(t)

        # 创建30个线程来取url并进行下载
        for i in range(10):
            t = threading.Thread(target=self.save_picture)
            thread_list.append(t)

        # 日志记录线程
        t = threading.Thread(target=self.save_log)
        thread_list.append(t)

        # 启动线程
        for t in thread_list:
            # t.setDaemon(True)
            t.start()

if __name__ == '__main__':
    names = ['宠物狗', '眼睛狗', '宠物猫', '宠物兔', '宠物猪', '猩猩', '母猴子']
    for id, name in enumerate(names):
        word  = name
        limit = 1500
        start = 0
        sp = BaiduSpider(word=word, sid = str(id) ,limit=int(limit), start=int(start))
        sp.start()
