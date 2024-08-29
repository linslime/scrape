from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from parsel import Selector
import re


def get_homepage_website(code):
    """
    通过番剧的代码得到番剧主页的网址
    :param code:番剧的代码
    :return: 番剧主页的网址
    """
    return "https://www.gugufan.org/index.php/vod/detail/id/" + str(code) + ".html"


def get_name_and_episodes(url):
    """
    通过番剧主页地址，获得番剧的名字和最新集数
    :param url:番剧主页的网址
    :return:
    cartoon_name:番剧的名字
    episode:番剧的最新集数
    """
    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("headless")
    browser = webdriver.Chrome(options=browser_options)
    browser.get(url)
    selector = Selector(browser.page_source)
    cartoon_name = selector.css('.slide-info-title *::text').get()
    episode = int(re.findall(r"\d+\.?\d*", selector.css('.slide-info-remarks *::text').get())[0])
    return cartoon_name, episode


if __name__ == "__main__":
    code = 2738
    homepage_website = get_homepage_website(code)
    get_name_and_episodes(homepage_website)
    print(homepage_website)