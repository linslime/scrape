def get_homepage_website(code):
    """
    通过番剧的代码得到番剧主页的网址
    :param code:番剧的代码
    :return: 番剧主页的网址
    """
    return "https://www.gugufan.org/index.php/vod/detail/id/" + str(code) + ".html"

if __name__ == "__main__":
    code = 2738
    homepage_website = get_homepage_website(code)
    print(homepage_website)