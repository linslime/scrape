from selenium import webdriver
from parsel import Selector
import requests
import time
browser_options = webdriver.ChromeOptions()
browser_options.add_argument("headless")
browser = webdriver.Chrome(options=browser_options)
url = 'https://www.copymanga.site/comic/lhqcdeyqjzqdgxssxsydxhsh/chapter/26b8d1ca-37c9-11eb-b5f2-00163e0ca5bd'
browser.get(url)

for y in range(50):
    js = 'window.scrollBy(0,300)'
    browser.execute_script(js)
    time.sleep(0.001)
# print(browser.page_source)
Selector = Selector(browser.page_source)
items = Selector.css('.comicContent-list img::attr(data-src)')
images = []
for item in items:
    images.append(item.get())
proxy = {'https': 'http://127.0.0.1:33210',  'http': 'http://127.0.0.1:33210', 'all': 'socks5://127.0.0.1:33211'}
for i in range(len(images)):
    response = requests.get(images[i], proxies=proxy)
    with open('.\image' + str(i) + '.jpg', 'wb') as f:  # 以二进制写入文件保存
        f.write(response.content)
    f.close()
    response.close()
browser.close()

