from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

browser = webdriver.Chrome()
try:
    browser.get('https://www.copymanga.site/comic/lhqcdeyqjzqdgxssxsydxhsh/chapter/26b8d1ca-37c9-11eb-b5f2-00163e0ca5bd')
    # input = browser.find_element(By.ID, 'kw')
    # input.send_keys('Python')
    # input.send_keys(Keys.ENTER)
    wait = WebDriverWait(browser, 10)
    # wait.until(EC.presence_of_element_located((By.ID, 'content_left')))
    # print(browser.current_url)
    # print(browser.get_cookies())
    print(browser.page_source)
finally:
    browser.close()