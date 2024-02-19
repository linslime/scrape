import concurrent.futures
import csv
from selenium import webdriver
from parsel import Selector
import requests
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor
import img2pdf
import threading

class MangaScraper(object):
    def __init__(self,url):
        self.proxy = {'https': 'http://127.0.0.1:33210', 'http': 'http://127.0.0.1:33210',
                      'all': 'socks5://127.0.0.1:33211'}
        browser_options = webdriver.ChromeOptions()
        browser_options.add_argument("headless")
        # browser_options.add_argument(self.proxy)
        self.website = 'https://www.copymanga.site'
        self.browser = webdriver.Chrome(options=browser_options)
        self.url = url
        self.url_index = []
        self.address = './comics'
        self.name = ''
        self.images_url = []
        self.images_dir = []
        self.images_exist = []
        self.lock = threading.Lock()

    def start(self):
        print('开始下载漫画目录')
        self.get_url_index()
        print(self.name + ',漫画目录下载完成')

        print('创建线程池')
        pool = ThreadPoolExecutor(max_workers=60)
        print('线程池创建完成')

        print('开始初始化图片url')
        self.init_images_url()
        print('完成图片url初始化')

        print('开始下载图片url')
        num = 0
        while not self.check_url_index():
            if num > 0:
                print('有章节未成功下载图片url，开始第' + str(num) + '轮重试')
            num += 1
            futures = []
            for i in range(len(self.url_index)):
                if len(self.images_url[i]) == 0:
                    futures.append(pool.submit(lambda cxp: self.get_images_url(*cxp), (self.website + self.url_index[i], i)))
            concurrent.futures.wait(futures)
            print('开始第' + str(num) + '轮检查')
        print('通过第' + str(num) + '轮检查，图片url下载完成')

        print('开始创建目录')
        self.create_comics_dir()
        print('目录创建成功')

        print('开始检测图片是否存在')
        self.init_images_exist()
        print('完成图片是否存在检测')

        print('开始下载图片')
        num = 0
        while not self.check_save_images():
            if num > 0:
                print('有图片未下载成功，开始第' + str(num) + '轮重试')
            num += 1
            futures = []
            for i in range(len(self.images_url)):
                for j in range(len(self.images_url[i])):
                    if not self.images_exist[i][j]:
                        futures.append(pool.submit(lambda cxp: self.save_image(*cxp), (self.images_url[i][j], i, j)))
            concurrent.futures.wait(futures)
            print('开始第' + str(num) + '轮检查')
        print('通过第' + str(num) + '轮检查，图片下载完成')

        print('开始创建pdf')
        self.create_pdf()
        print('pdf创建成功')

    def init_images_url(self):
        path = self.address + '/' + self.name + '/' + self.name + '.csv'
        if not os.path.exists(path):
            self.images_url = [[] for i in self.url_index]
            os.makedirs(self.address + '/' + self.name)
            return
        with open(path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                self.images_url.append(row)
        if len(self.images_url) < len(self.url_index):
            self.images_url += [[] for i in range(len(self.url_index) - len(self.images_url))]

    def init_images_exist(self):
        self.images_exist = [[0 for i in urls] for urls in self.images_url]
        for row in range(len(self.images_exist)):
            for col in range(len(self.images_exist[row])):
                path = self.address + '/' + self.name + '/images/' + self.get_name(row) + '/' + self.get_name(row) + '_' + self.get_name(col) + '.jpg'
                if os.path.exists(path):
                    self.images_exist[row][col] = 1

    def create_comics_dir(self):
        for i in range(len(self.url_index)):
            path = self.address + '/' + self.name + '/images/' + self.get_name(i)
            if not os.path.exists(path):
                os.makedirs(path)

    def save_image(self, image_url, index, num):
        path = self.address + '/' + self.name + '/images/' + self.get_name(index) + '/' + self.get_name(index) + '_' + self.get_name(num) + '.jpg'
        response = requests.get(image_url, proxies=self.proxy, timeout=10)
        with open(path, 'wb') as file:  # 以二进制写入文件保存
            file.write(response.content)
        file.close()
        response.close()
        self.images_exist[index][num] = 1

    def save_images_url(self):
        file = open(self.address + '/' + self.name + '/' + self.name + '.csv', 'w', newline='')
        csv.writer(file).writerows(self.images_url)
        file.close()

    def create_pdf(self):
        # 当前目录
        base_dir = './comics/' + self.name + '/images/'
        # 获取当前目录下的所有文件
        files = os.listdir(base_dir)
        images_dir = []
        for filename in files:
            images_dir += [base_dir + filename + '/' + image_name for image_name in os.listdir(base_dir + filename)]
        self.images_dir = images_dir

        output = './comics/' + self.name + '/' + self.name + '.pdf'
        # 创建一个PDF文件 并以二进制方式写入
        with open(output, "wb") as f:
            # convert函数 用来转PDF
            write_content = img2pdf.convert(self.images_dir)
            f.write(write_content)  # 写入文件

    def get_name(self, num):
        if num < 10:
            return '00' + str(num)
        elif num < 100:
            return '0' + str(num)
        else:
            return str(num)

    def get_url_index(self):
        self.browser.get(self.url)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, 'default全部')))
        selector = Selector(self.browser.page_source)
        self.url_index = selector.css('#default全部 ul:not(.page-all) a::attr(href)').getall()
        self.name = selector.css('.comicParticulars-title-right h6::attr(title)').get()

    def check_url_index(self):
        for urls in self.images_url:
            if len(urls) == 0:
                return False
        return True

    def get_images_url(self, url, index):
        browser_options = webdriver.ChromeOptions()
        browser_options.add_argument("headless")
        # browser_options.add_argument(self.proxy)
        browser = webdriver.Chrome(options=browser_options)
        browser.get(url)
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'lazyloaded')))
        for y in range(50):
            browser.execute_script('window.scrollBy(0,300)')
            time.sleep(0.001)
        selector = Selector(browser.page_source)
        count = int(selector.xpath('//span[contains(@class, "comicCount")]//text()').get())
        while True:
            images = selector.css('.comicContent-list img::attr(data-src)').getall()
            if count == len(images):
                browser.close()
                self.lock.acquire()
                self.images_url[index] = images
                self.save_images_url()
                self.lock.release()
                return
            for y in range(50):
                browser.execute_script('window.scrollBy(0,300)')
                time.sleep(0.001)
            selector = Selector(browser.page_source)

    def check_save_images(self):
        for i in range(len(self.images_exist)):
            for j in range(len(self.images_exist[i])):
                if self.images_exist[i][j] == 0:
                    return False
        return True

if __name__ == '__main__':
    scraper = MangaScraper('https://www.copymanga.site/comic/eyizhiyousiwangjieju')
    scraper.start()
