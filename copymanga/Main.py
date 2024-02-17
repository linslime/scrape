import concurrent.futures

from selenium import webdriver
from parsel import Selector
import requests
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor

class Scraper(object):
    def __init__(self,url):
        browser_options = webdriver.ChromeOptions()
        browser_options.add_argument("headless")
        self.website = 'https://www.copymanga.site'
        self.browser = webdriver.Chrome(options=browser_options)
        self.url = url
        self.url_index = []
        self.address = './comics'
        self.proxy = {'https': 'http://127.0.0.1:33210', 'http': 'http://127.0.0.1:33210', 'all': 'socks5://127.0.0.1:33211'}
        self.name = ''
        self.images_url = []

    def start(self):
        self.get_url_index()
        self.images_url = [[]for i in range(len(self.url_index))]
        pool = ThreadPoolExecutor(max_workers=100)
        futures = []
        for i in range(len(self.url_index)):
            futures.append(pool.submit(lambda cxp: self.get_images_url(*cxp), (self.website + self.url_index[i], i)))

        concurrent.futures.wait(futures)

        for i in range(len(self.images_url)):
            for j in range(len(self.images_url[i])):
                pool.submit(lambda cxp: self.save(*cxp), (self.images_url[i][j], i, j))

    def save(self, image_url, index, num):
        path = self.address + '/' + self.name + '/' + self.get_name(index)
        if not os.path.exists(path):
            os.makedirs(path)
        response = requests.get(image_url, proxies=self.proxy)
        with open(path + '/' + self.get_name(index) + '_' + self.get_name(num) + '.jpg', 'wb') as file:  # 以二进制写入文件保存
            file.write(response.content)
        file.close()
        response.close()

    def get_name(self,num):
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
        print(self.name)

    def get_images_url(self, url, index):
        browser_options = webdriver.ChromeOptions()
        browser_options.add_argument("headless")
        browser = webdriver.Chrome(options=browser_options)
        browser.get(url)
        for y in range(50):
            browser.execute_script('window.scrollBy(0,300)')
            time.sleep(0.001)
        selector = Selector(browser.page_source)
        count = int(selector.xpath('//span[contains(@class, "comicCount")]//text()').get())
        while True:
            for y in range(50):
                browser.execute_script('window.scrollBy(0,300)')
                time.sleep(0.001)
            selector = Selector(browser.page_source)
            images = selector.css('.comicContent-list img::attr(data-src)').getall()
            if count == len(images):
                self.images_url[index] = images
                browser.close()
                return

if __name__ == '__main__':
    scraper = Scraper('https://www.copymanga.site/comic/mswgtqlysjsjhgbjbsds')
    scraper.start()
