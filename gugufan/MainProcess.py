from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from parsel import Selector
import re
import requests
import multiprocessing
from Config import Config
import os


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
    browser = get_browser(Config.browser_type)
    browser.get(url)
    selector = Selector(browser.page_source)
    cartoon_name = selector.css('.slide-info-title *::text').get()
    episode = int(re.findall(r"\d+\.?\d*", selector.css('.slide-info-remarks *::text').get())[0])
    browser.close()
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
    browser = get_browser(Config.browser_type)
    browser.get(url)
    m3u8_url = "https://" + re.search(pattern="1\",\"url\":\"(.*?)\",\"url_next", string=browser.page_source).group(1)[10:].replace('\\', '/')
    ts_part_url = re.findall(pattern="videos/(.*?)/index", string=browser.page_source)[0]
    browser.close()
    return m3u8_url, ts_part_url


def multi_process_download(task):
    # 创建队列
    queue = multiprocessing.Manager().Queue()
    for i in task:
        queue.put(i)
    # 用与互斥访问队列
    lock = multiprocessing.Manager().Lock()

    # 多进程下载.ts文件
    processes = list()
    for i in range(5):
        process = multiprocessing.Process(target=run_download, args=(queue, lock))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()


def run_download(queue, lock):
    while True:
        lock.acquire()
        if not queue.empty():
            url, path = queue.get()
            lock.release()
            ts = request(url).content
            with open(path, 'wb') as f:
                f.write(ts)
        else:
            lock.release()
            break


def request(url):
    """
    通过url下载文件，如果下载失败则重试
    :param url: 文件网址
    :return: 文件
    """
    response = None
    while True:
        try:
            response = requests.get(url=url, timeout=10)
            break
        except:
            continue
    return response


def get_task(code):
    """
    通过动漫代码得到任务列表
    :param code:动漫代码
    :return: 任务列表
    """

    # 得到动漫主页网址
    homepage_website = get_homepage_website(code)
    # 得到动漫名字和集数
    cartoon_name, episode = get_name_and_episodes(homepage_website)
    # 通过动漫代码和集数，得到每一集动漫的网址
    websites = get_episode_website(code, episode)
    # 创建任务队列
    task_list = list()
    for i in range(len(websites)):
        # 创建目录
        if not os.path.exists('./cartoon/' + cartoon_name + '/' + str(i + 1) + '/temp/'):
            os.makedirs('./cartoon/' + cartoon_name + '/' + str(i + 1) + '/temp/')
        m3u8_url, ts_part_url = get_m3u8_and_ts_part_url(websites[i])
        m3u8 = request(m3u8_url).text
        index_list = re.findall(pattern="index.*.ts", string=m3u8)
        ts_url = list()
        for index in index_list:
            url = 'https://b19.yizhoushi.com/acgworld/videos/' + ts_part_url + '/' + index
            path = './cartoon/' + cartoon_name + '/' + str(i + 1) + '/temp/' + index
            ts_url.append((url, path))
        task_list.append(ts_url)
    return task_list


def complete_all_tasks(task_queue, lock):
    """
    多进程下载多集动漫
    :param task_queue:任务队列
    :param lock: 锁
    :return:
    """
    while True:
        lock.acquire()
        if not task_queue.empty():
            task = task_queue.get()
            lock.release()
            multi_process_download(task)
        else:
            lock.release()
            break


def main(code):
    # 获得任务队列
    task_list = get_task(code)
    # 创建任务共享队列，该队列由多个队列组成，每个队列都是某一集的.ts文件集合
    task_queue = multiprocessing.Manager().Queue()
    for task in task_list:
        task_queue.put(task)

    # 锁，用于互斥访问task_queue
    lock = multiprocessing.Manager().Lock()

    # 多进程处理任务
    processes = list()
    for i in range(5):
        process = multiprocessing.Process(target=complete_all_tasks, args=(task_queue, lock))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()


if __name__ == "__main__":
    main(Config.code)
