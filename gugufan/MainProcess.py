from selenium import webdriver
from parsel import Selector
import re
import requests
import multiprocessing
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from gugufan.Config import Config
from gugufan.Config import Path
import os
import shutil
from miniredis.miniredis import create_shared_memory


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


def get_message(url):
    """
    通过番剧主页地址，获得番剧的名字和最新集数
    :param url:番剧主页的网址
    :return:
    cartoon_name:番剧的名字
    episode_name:番剧每一集的名字
    episode_website:番剧每一集的网址
    """
    browser = get_browser(Config.browser_type)
    browser.get(url)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'rel')))
    selector = Selector(browser.page_source)
    cartoon_name = selector.css('.slide-info-title *::text').get()
    # 将动画名放入共享内存
    shared_memory = create_shared_memory()
    shared_memory.set_data('cartoon_name', cartoon_name)
    shared_memory.close()
    episode_website = selector.css('.anthology-list-play')[0].css('a::attr(href)').getall()
    episode_website = [Config.main_page + i for i in episode_website]
    episode_name = selector.css('.anthology-list-play')[0].css('*::text').getall()
    browser.close()
    return episode_name, episode_website


def get_m3u8_and_ts_part_url(url):
    """
    通过一集番剧的网址，得到.m3u8文件的网址
    :param url:该集番剧的网址
    :return:m3u8_url文件的网址，.ts文件url的一部分
    """
    browser = get_browser(Config.browser_type)
    browser.get(url)
    m3u8_url = "https://" + re.search(pattern="1\",\"url\":\"(.*?)\",\"url_next", string=browser.page_source).group(1)[10:].replace('\\', '/')
    ts_part_url = re.findall(pattern="videos/(.*?)/index", string=browser.page_source)[0]
    browser.close()
    return m3u8_url, ts_part_url


def multi_process_download(task):
    """
    下载一集番剧的全部.ts文件
    :param task: 该集番剧的任务队列
    :return:
    """
    # 创建队列
    queue = multiprocessing.Manager().Queue()
    for i in task:
        queue.put(i)
    # 用与互斥访问队列
    lock = multiprocessing.Manager().Lock()

    # 多进程下载.ts文件
    processes = list()
    for i in range(Config.max_downloads):
        process = multiprocessing.Process(target=run_download, args=(queue, lock))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()


def run_download(queue, lock):
    """
    下载.ts文件，并保存
    :param queue: 任务队列
    :param lock: 锁，用于互斥访问queue
    :return: None
    """
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


def download_m3u8(name, website, results):
    """
    为某一集创建任务
    :param name:某一集的名字
    :param website:某一集的url
    :param results:结果队列，是共享队列
    :return:
    """
    # 创建目录
    dirs = Path.get_ts_folder_path(name=name)
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    m3u8_url, ts_part_url = get_m3u8_and_ts_part_url(website)
    m3u8 = request(m3u8_url).text
    index_list = re.findall(pattern="index.*.ts", string=m3u8)
    ts_url = list()
    for index in index_list:
        url = Path.get_ts_url(ts_part_url=ts_part_url, index=index)
        path = Path.get_ts_file_path(name=name, index=index)
        # 判断该.ts文件是否已经下载完成
        if not os.path.exists(path):
            ts_url.append((url, path))
    results.put(ts_url)


def get_task(code):
    """
    通过动漫代码得到任务列表
    :param code:动漫代码
    :return: 任务列表
    """

    # 得到动漫主页网址
    homepage_website = Path.get_homepage_website(code)
    # 得到动漫名字和集数
    episode_name, episode_website = get_message(homepage_website)
    # 创建结果队列
    task_queue = multiprocessing.Manager().Queue()
    # 创建多进程处理任务
    processes = []
    for i in range(len(episode_website)):
        process = multiprocessing.Process(target=download_m3u8, args=(episode_name[i], episode_website[i], task_queue))
        process.start()
        processes.append(process)
    # 等待多进程完成任务
    for process in processes:
        process.join()
    return task_queue


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


def merge_ts_files(code):
    """
    合并文件，并删除文件
    :param code: 番剧代码
    :return:
    """
    dirs = Path.get_temp_folder_path()
    if not os.path.exists(dirs):
        return
    episodes = os.listdir(dirs)
    for episode in episodes:
        # 若该mp4文件已经生成完成，则跳过
        if os.path.exists(Path.get_mp4_path(episode=episode)):
            continue
        episode_path = Path.get_ts_folder_path(episode)
        ts_list = sorted(os.listdir(episode_path), key=lambda s: int(re.findall('\d+', s)[0]))
        mp4 = open(Path.get_mp4_path(episode=episode), 'ab')
        for ts in ts_list:
            ts_path = Path.get_ts_file_path(episode, ts)
            ts_file = open(ts_path, 'rb')
            mp4.write(ts_file.read())
            ts_file.close()
        mp4.close()
    shutil.rmtree(dirs)


def main(code):
    """
    主函数
    :param code:番剧代码
    :return:
    """
    # 获得任务队列
    task_queue = get_task(code)

    # 锁，用于互斥访问task_queue
    lock = multiprocessing.Manager().Lock()

    # 多进程处理任务
    processes = list()
    for i in range(Config.max_episodes):
        process = multiprocessing.Process(target=complete_all_tasks, args=(task_queue, lock))
        process.start()
        processes.append(process)
    # 等待任务完成
    for process in processes:
        process.join()
    # 合并文件，生成mp4文件，并删除.ts文件
    merge_ts_files(code)


if __name__ == "__main__":
    main(Config.code)
