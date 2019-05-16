import time
import  re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import User, Base
import random
from content import content

pattern = re.compile('.*weibo.com/(\d+)?.*?')
engine = create_engine('sqlite:///weibo.sqlite')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class WeiboSpider(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        chrome_options = Options()
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(
            executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
            options=chrome_options)
        self.driver.get(url='http://s.weibo.com/')
        self.login()

    def login(self):
        # 登陆
        print('start login manual')
        WebDriverWait(self.driver, 10
                      ).until(EC.presence_of_element_located((By.XPATH, "//a[@node-type='loginBtn']")))
        self.driver.find_element_by_xpath("//a[@node-type='loginBtn']").click()
        WebDriverWait(self.driver, 10
                      ).until(EC.presence_of_element_located((By.XPATH, "//input[@name='username']")))
        user = self.driver.find_element_by_xpath("//input[@name='username']")
        user.clear()
        user.send_keys(self.username)
        psw = self.driver.find_element_by_xpath("//input[@name='password']")
        psw.clear()
        psw.send_keys(self.password)
        self.driver.find_element_by_xpath("//a[@node-type='submitBtn']").click()
        # 人工输入手机验证码
        time.sleep(30)

    def send(self, message):
        users = session.query(User).filter(User.send == False).all()
        for user in users:
            url = 'https://api.weibo.com/chat/#/chat?to_uid={}'.format(user.uid)
            self.driver.get(url)
            self.driver.refresh()
            WebDriverWait(self.driver, 10
                          ).until(EC.presence_of_element_located((By.ID, "webchat-textarea")))
            webchat = self.driver.find_element_by_id('webchat-textarea')
            webchat.clear()
            for part in message.split('\n'):
                webchat.send_keys(part)
                ActionChains(self.driver).key_down(Keys.CONTROL).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(
                    Keys.CONTROL).perform()
            webchat.send_keys(Keys.ENTER)
            user.send = True
            session.commit()
            sleep_time = random.randint(10, 20)
            time.sleep(sleep_time)


if __name__ == '__main__':
    # 登陆
    weibo1 = WeiboSpider('sc02@gewu.org.cn', 'LtERFTWQUYzEnu6')
    weibo1.send(content)
    # for part in content.replace(r'\r\n', r'\n').split('\n'):
    #     print(part)





