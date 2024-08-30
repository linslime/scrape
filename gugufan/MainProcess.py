from selenium import webdriver
from parsel import Selector
import re
import requests


def get_homepage_website(code):
    """
    通过番剧的代码得到番剧主页的网址
    :param code:番剧的代码
    :return: 番剧主页的网址
    """
    return "https://www.gugufan.org/index.php/vod/detail/id/" + str(code) + ".html"


def get_browser(type):
    """
    返回指定浏览器类型的工具
    :param type: 浏览器类型
    :return: 浏览器工具
    """
    if type == "chrome":
        browser_options = webdriver.ChromeOptions()
        browser_options.add_argument("headless")
        browser = webdriver.Chrome(options=browser_options)
        return browser
    elif type == "edge":
        browser_options = webdriver.EdgeOptions()
        browser_options.add_argument("headless")
        browser = webdriver.Edge(options=browser_options)
        return browser


def get_name_and_episodes(url):
    """
    通过番剧主页地址，获得番剧的名字和最新集数
    :param url:番剧主页的网址
    :return:
    cartoon_name:番剧的名字
    episode:番剧的最新集数
    """
    browser = get_browser('edge')
    browser.get(url)
    selector = Selector(browser.page_source)
    cartoon_name = selector.css('.slide-info-title *::text').get()
    episode = int(re.findall(r"\d+\.?\d*", selector.css('.slide-info-remarks *::text').get())[0])
    return cartoon_name, episode


def get_episode_website(code, episode):
    """
    通过番剧的最新集数和番剧的代码获得番剧每一集的网址
    :param episode: 番剧的最新集数
    :param code: 番剧代码
    :return: 每一集番剧的网址
    """
    websites = list()
    for i in range(1, episode + 1):
        website = "https://www.gugufan.org/index.php/vod/play/id/" + str(code) + "/sid/1/nid/" + str(i) + ".html"
        websites.append(website)
    return websites


def get_m3u8_and_ts_part_url(url):
    """
    通过一集番剧的网址，得到.m3u8文件的网址
    :param url:
    :return:
    """
    browser = get_browser('edge')
    browser.get(url)
    m3u8_url = "https://" + re.search(pattern="url_next\":\"(.*?)\"", string=browser.page_source).group(1)[10:].replace('\\', '/')
    ts_part_url = re.findall(pattern="videos/(.*?)/index", string=browser.page_source)[0]
    return m3u8_url, ts_part_url


def get_ts_url(url):
    """
    通过某一集url，得到所有.ts文件网址
    :param url: 某一集url的网址
    :return: 这一集所有.ts文件的网址
    """
    m3u8_url, ts_part_url = get_m3u8_and_ts_part_url(url)
    m3u8 = requests.get(url=m3u8_url, timeout=10).text
    index = re.findall(pattern="index.*.ts", string=m3u8)
    ts_url = list()
    for i in index:
        ts_url.append('https://b19.yizhoushi.com/acgworld/videos/' + ts_part_url + '/' + i)
    return ts_url


def get_and_save_ts(url):
    """
    通过.ts网址，下载并保存.ts文件
    :param url: .ts文件网址
    :return: 是否成功
    """
    try:
        ts = requests.get(url=url, timeout=10).content
        with open('./data/' + url + '.ts', 'wb') as f:
            f.write(ts)
        return True
    except:
        print("haha")
        return False


if __name__ == "__main__":
    code = 2738
    homepage_website = get_homepage_website(code)
    cartoon_name, episode = get_name_and_episodes(homepage_website)
    websites = get_episode_website(code, episode)
    m3u8_url, ts_part_url = get_m3u8_and_ts_part_url(websites[3])
