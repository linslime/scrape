import requests

# proxy = {'https_proxy': 'http://127.0.0.1:33210',  'http_proxy': 'http://127.0.0.1:33210', 'all_proxy': 'socks5://127.0.0.1:33211'}
proxy = {'https': 'http://127.0.0.1:33210',  'http': 'http://127.0.0.1:33210', 'all': 'socks5://127.0.0.1:33211'}
response = requests.get("https://hi77-overseas.mangafuna.xyz/lhqcdeyqjzqdgxssxsydxhsh/48563/16402197829960/c800x.jpg",proxies=proxy)
with open('D:\Desktop\image.jpg', 'wb') as f:  # 以二进制写入文件保存
    f.write(response.content)
