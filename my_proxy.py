import pymongo
import requests
from lxml import etree
from multiprocessing import Process
import threading
import random

class Proxy:

    def __init__(self, init=True):
        self.lock = threading.Lock()
        self.ok_ip_list = []            # 用于多线程检查 IP 可用性
        self.all_ip = []                # 数据库中所有可用 IP
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0",
        }
        if init:
            self.get_all_proxy()

    def get_89ip(self, page_count):
        url = 'https://www.89ip.cn/'
        url_list = [url + f'index_{p}.html' for p in range(1, page_count + 1)]
        ip_list = []
        for url_item in url_list:
            try:
                res = requests.get(url_item)
                html = etree.HTML(res.text)
                ip_port = [i.strip() for i in html.xpath('//tr/td[position()<=2]/text()')]
                for i in range(0, len(ip_port), 2):
                    item = {}
                    ip = ip_port[i] + ':' + ip_port[i + 1]
                    if ip_port[i + 1] == '443':
                        item['https'] = 'https://' + ip
                    else:
                        item['http'] = 'http://' + ip
                    ip_list.append(item)
            except Exception:
                pass
        return ip_list

    def check_ip(self, ip):
        try:
            res = requests.get('http://www.baidu.com/', proxies=ip.copy(), timeout=2)
            if res.status_code == 200:
                with self.lock:
                    self.ok_ip_list.append(ip)
                return True
        except Exception:
            pass

        return False

    def check_all_ip(self, ip_list):
        all_thread = []
        for ip in ip_list:
            t = threading.Thread(target=self.check_ip, args=(ip,))
            all_thread.append(t)
            t.start()
        
        for t in all_thread:
            t.join()

    def save_ip(self, ip_list):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        proxy_db = client['proxy_db']
        proxy_col = proxy_db['proxy']
        for ip in ip_list:
            if proxy_col.count_documents({'ip': ip}) == 0:
                proxy_col.insert_one({'ip': ip})
                # print(ip, '写入完成')
        client.close()

    def delete_ip(self, data):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        proxy_db = client['proxy_db']
        proxy_col = proxy_db['proxy']
        proxy_col.delete_many(data)
        client.close()

    def query_all_ip(self):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        proxy_db = client['proxy_db']
        proxy_col = proxy_db['proxy']
        ip_list = []
        for ip in proxy_col.find():
            ip_list.append(ip['ip'])
        client.close()
        return ip_list

    def check_proxy(self, ip):
        url = 'http://ip.tool.chinaz.com/'
        try:
            res = requests.get(url, headers=self.headers, proxies=ip, timeout=2)
            html = etree.HTML(res.text)
            print(html.xpath('//*[@id="leftinfo"]/div[3]/div[2]/div[2]/span[1]/text()')[0])
        except Exception:
            pass

    def get_all_proxy(self):
        self.all_ip = []
        self.ok_ip_list = []
        ip_list = self.get_89ip(16)
        ip_list.extend(self.query_all_ip())
        self.check_all_ip(ip_list)    # 将获取到的新 IP 与数据库中旧 IP 全部 check
        self.delete_ip({})
        self.save_ip(self.ok_ip_list)
        self.all_ip = self.query_all_ip()
        # print(self.all_ip)
        # print(len(self.all_ip))

    # 每次需要 check 一次，若在爬虫中更新代理则需要处理 time out 时的异常
    def get_random_proxy(self):
        while len(self.all_ip) > 1:
            ip = random.choice(self.all_ip)
            if self.check_ip(ip):
                return ip
            else:
                self.all_ip.remove(ip)
        self.get_all_proxy()            # 可用 IP 过少时更新代理池
        return {}                       # 返回本地 IP


if __name__ == '__main__':
    proxy = Proxy()
    x = 0
    while x <= 500:
        x += 1
        print(proxy.get_random_proxy())