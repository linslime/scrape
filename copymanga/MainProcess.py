from CopyMangaScraper import *
from PDFManagement import *
from FileDirectoryManagement import *
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
import threading

if __name__ == '__main__':

    print('开始下载漫画目录')
    chapter_urls, comics_name = download_chapter_urls('https://www.copymanga.site/comic/woduzishenji')
    print(comics_name + ',完成下载漫画目录')

    print('开始初始化目录')
    init_comics_directory(comics_name, len(chapter_urls))
    print('完成初始化目录')

    print('开始读取本地图片url')
    image_urls = init_image_urls(comics_name, len(chapter_urls))
    print('完成读取本地图片url')

    print('开始创建进程池、线程池和监测线程')
    process_pool = Pool(6)
    thread_pool = ThreadPoolExecutor(max_workers=30)
    print('完成创建进程池、线程池和监测线程')

    print('开始下载图片url')
    num = 0
    lock = threading.Lock()
    while not check_image_urls(image_urls):
        if num > 0:
            print('有章节未成功下载图片url，开始第' + str(num) + '轮重试')
        num += 1
        futures = []
        for chapter_index in range(len(chapter_urls)):
            if len(image_urls[chapter_index]) == 0:
                futures.append(thread_pool.submit(lambda cxp: download_image_urls(*cxp), (comics_name, chapter_urls[chapter_index], chapter_index, image_urls, lock)))
        concurrent.futures.wait(futures)
        print('开始第' + str(num) + '轮检查')
    thread_pool.shutdown()
    print('通过第' + str(num) + '轮检查，图片url下载完成')

    print('开始读取本地图片和pdf')
    images_exist, pdfs_exist, aggregate_pdf_exist = init_images_and_pdf(comics_name, image_urls)
    print('完成读取本地图片和pdf')

    print('开始创建线程池')
    thread_pool = ThreadPoolExecutor(max_workers=10)
    print('完成创建线程池')

    print('开始下载图片并开始生成章节pdf')
    num = 0
    while not check_images_exist(images_exist):
        if num > 0:
            print('有图片未下载成功，开始第' + str(num) + '轮重试')
        num += 1
        futures = []
        lock = threading.Lock()
        chapter_index_list = [0,]
        for i in range(10):
            futures.append(thread_pool.submit(lambda cxp: download_chapters(*cxp), (comics_name, image_urls, lock, chapter_index_list, images_exist, pdfs_exist, process_pool)))
        concurrent.futures.wait(futures)
        print('开始第' + str(num) + '轮检查')
    thread_pool.shutdown()
    print('通过第' + str(num) + '轮检查，图片下载完成')
    if len(process_pool._cache) > 0:
        print('还有章节pdf未处理完成')
    process_pool.close()
    process_pool.join()
    print('完成生成章节pdf')

    if not aggregate_pdf_exist:
        print('开始生成总pdf')
        create_aggregate_pdf(comics_name)
    print('完成生成总pdf')
