from PDFManagement import *
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from selenium import webdriver
from parsel import Selector
import requests
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor

def download_chapter_urls(url):
    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("headless")
    browser = webdriver.Chrome(options=browser_options)
    browser.get(url)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'default全部')))
    selector = Selector(browser.page_source)
    chapter_urls = selector.css('#default全部 ul:not(.page-all) a::attr(href)').getall()
    comics_name = selector.css('.comicParticulars-title-right h6::attr(title)').get()
    chapter_urls = ['https://www.copymanga.site' + chapter_url for chapter_url in chapter_urls]
    return chapter_urls, comics_name

def check_image_urls(image_urls):
    for urls in image_urls:
        if len(urls) == 0:
            return False
    return True

def check_images_exist(images_exist):
    for chapter_index in range(len(images_exist)):
        if sum(images_exist[chapter_index]) != len(images_exist[chapter_index]):
            return False
    return True

def check_chapter_exist(images_exist, chapter_index):
    if sum(images_exist[chapter_index]) != len(images_exist[chapter_index]):
        return False
    return True

def check_pdfs_exist(pdfs_exist):
    if sum(pdfs_exist) != len(pdfs_exist):
        return False
    return True

def download_image_urls(comics_name, chapter_url, chapter_index, image_urls, lock):
    start_time = time.time()
    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("headless")
    browser = webdriver.Chrome(options=browser_options)
    browser.get(chapter_url)
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
            lock.acquire()
            image_urls[chapter_index] = images
            save_image_urls_csv(comics_name, image_urls)
            lock.release()
            return
        if time.time() - start_time > 60:
            browser.close()
            return
        for y in range(50):
            browser.execute_script('window.scrollBy(0,300)')
            time.sleep(0.001)
        selector = Selector(browser.page_source)

def download_image(image_url, comics_name, chapter_index, image_index, images_exist):
    proxy = {'https': 'http://127.0.0.1:33210', 'http': 'http://127.0.0.1:33210', 'all': 'socks5://127.0.0.1:33211'}
    response = requests.get(image_url, proxies=proxy, timeout=10)
    save_image(comics_name, chapter_index, image_index, response.content)
    response.close()
    images_exist[chapter_index][image_index] = 1

def monitor_download_image_urls(comics_name, image_urls):
    while True:
        time.sleep(1)
        if check_image_urls(image_urls):
            save_image_urls_csv(comics_name, image_urls)
            return
        else:
            save_image_urls_csv(comics_name, image_urls)

def monitor_download_images(comics_name, images_exist, pdfs_exist, process_pool):
    while True:
        time.sleep(5)
        for chapter_index in range(len(images_exist)):
            if not pdfs_exist[chapter_index] and len(images_exist[chapter_index]) == sum(images_exist[chapter_index]):
                process_pool.apply_async(func=create_pdf, args=(comics_name, chapter_index))
                pdfs_exist[chapter_index] = 1
        if check_pdfs_exist(pdfs_exist):
            return

def download_chapters(comics_name, image_urls, lock, chapter_index_list, images_exist, pdfs_exist, process_pool):
    thread_pool = ThreadPoolExecutor(max_workers=10)
    while True:
        lock.acquire()
        if chapter_index_list[0] == len(image_urls):
            lock.release()
            thread_pool.shutdown()
            return
        chapter_index = chapter_index_list[0]
        chapter_index_list[0] = chapter_index + 1
        lock.release()

        while not check_chapter_exist(images_exist, chapter_index):
            futures = []
            for image_index in range(len(image_urls[chapter_index])):
                if not images_exist[chapter_index][image_index]:
                    futures.append(thread_pool.submit(lambda cxp: download_image(*cxp), (image_urls[chapter_index][image_index], comics_name, chapter_index, image_index, images_exist)))
            concurrent.futures.wait(futures)
        if not pdfs_exist[chapter_index]:
            process_pool.apply_async(func=create_pdf, args=(comics_name, chapter_index))
            pdfs_exist[chapter_index] = 1