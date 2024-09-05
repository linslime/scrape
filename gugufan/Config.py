from miniredis.miniredis import create_shared_memory


class Config:
    browser_type = 'chrome'
    save_path = 'D:/Desktop'
    code = 437
    main_page = 'https://www.gugu3.com'
    max_episodes = 8
    max_downloads = 10


class Path:
    cartoon_name = None

    @staticmethod
    def get_ts_folder_path(name):
        path = Config.save_path + '/cartoon/' + Path.get_cartoon_name() + '/temp/' + name
        return path

    @staticmethod
    def get_ts_file_path(name, index):
        return Config.save_path + '/cartoon/' + Path.get_cartoon_name() + '/temp/' + name + '/' + index

    @staticmethod
    def get_homepage_website(code):
        """
        通过番剧的代码得到番剧主页的网址
        :param code:番剧的代码
        :return: 番剧主页的网址
        """
        return Config.main_page + "/index.php/vod/detail/id/" + str(code) + ".html"

    @staticmethod
    def get_ts_url(ts_part_url, index):
        return 'https://b19.yizhoushi.com/acgworld/videos/' + ts_part_url + '/' + index

    @staticmethod
    def get_temp_folder_path():
        return Config.save_path + '/cartoon/' + Path.get_cartoon_name() + '/temp'

    @staticmethod
    def get_mp4_path(episode):
        return Config.save_path + '/cartoon/' + Path.get_cartoon_name() + '/' + episode + '.mp4'

    @staticmethod
    def get_cartoon_name():
        if Path.cartoon_name is None:
            shared_memory = create_shared_memory()
            Path.cartoon_name = shared_memory.get_data('cartoon_name')
        return Path.cartoon_name
