import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from multiprocessing import Pool
import random
import json
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from database import User,Base
from content import content
from lzdm import code

pattern = re.compile('.*weibo.com/(\d+)?.*?')
engine = create_engine('sqlite:///weibo.sqlite?check_same_thread=False')
Base.metadata.bind = engine

class WeiboSpider(object):
    def __init__(self, username, password,length, no):
        self.username = username
        self.password = password
        self.length = length
        self.no = no
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        self.session = session
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(
            executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
            options=chrome_options)
        self.driver.get(url='http://s.weibo.com/')
        self.set_cookie()
        self.is_login()

    def is_login(self):
        # 判断是否登录
        html = self.driver.page_source
        if html.find('gn_name') == -1:  # 利用用户名判断是否登陆
            # 没登录 ,则手动登录
            print('你没有登录')
            self.login()
            self.is_login()

    def save_cookie(self):
        '''保存cookie'''
        # 将cookie序列化保存下来
        f1 = open('{}.txt'.format(self.username), 'w')
        f1.write(json.dumps(self.driver.get_cookies()))
        f1.close

    def set_cookie(self):
        '''往浏览器添加cookie'''
        '''利用pickle序列化后的cookie'''
        try:
            f1 = open('{}.txt'.format(self.username))
            cookies = f1.read()
            cookies = json.loads(cookies)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
            time.sleep(8)
        except Exception as e:
            print(e)

    def get_snap(self):  # 对目标网页进行截屏。这里截的是全屏
        self.driver.save_screenshot('full{}.png'.format(self.username[0:4]))
        time.sleep(3)
        page_snap_obj = Image.open('full{}.png'.format(self.username[0:4]))
        return page_snap_obj

    def get_image(self):  # 对验证码所在位置进行定位，然后截取验证码图片
        img = self.driver.find_element_by_xpath("//img[@node-type='verifycode_image']")
        time.sleep(2)
        location = img.location
        print(location)
        size = img.size

        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']

        page_snap_obj = self.get_snap()
        # image_obj = page_snap_obj.crop((left*1.25, top*1.25, right*1.25, bottom*1.25))
        image_obj = page_snap_obj.crop((left, top, right, bottom))
        image_obj.save('code{}.png'.format(self.username[0:4]))
        return image_obj  # 得到的就是验证码

    def login(self):
        # 登陆
        print('start login manual')
        WebDriverWait(self.driver, 10
                      ).until(EC.presence_of_element_located((By.XPATH, "//a[@node-type='loginBtn']")))
        login_btn = self.driver.find_element_by_xpath("//a[@node-type='loginBtn']")
        login_btn.click()
        try:
            WebDriverWait(self.driver, 10
                          ).until(EC.presence_of_element_located((By.XPATH, "//input[@name='username']")))
        except TimeoutException as e:
            login_btn.click()
        user = self.driver.find_element_by_xpath("//input[@name='username']")
        user.clear()
        user.send_keys(self.username)
        psw = self.driver.find_element_by_xpath("//input[@name='password']")
        psw.clear()
        psw.send_keys(self.password)
        self.driver.find_element_by_xpath("//a[@node-type='submitBtn']").click()
        time.sleep(3)
        try:
            verifycode = self.driver.find_element_by_xpath("//input[@name='verifycode']")
            print('请输入验证码')
            if verifycode:
                self.get_image()
                result = code('code{}.png'.format(self.username[0:4]))
                print(result['data'])
                v_code = result['data']['val']
                print(result)
                print(v_code)
                verifycode.clear()
                verifycode.send_keys(v_code)
                self.driver.find_element_by_xpath("//a[@node-type='submitBtn']").click()
        except Exception as e:
            print(e)
            print('无需输入人工验证码')
        # 人工输入手机验证码
        time.sleep(30)
        self.save_cookie()

    def send(self, message,user):
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
        self.session.commit()
        print(user.name)

    def send_all(self,message):
        users = self.session.query(User).filter(User.send == False).all()
        users_length = len(users)
        start = int(users_length * (self.no/self.length))
        end = int(users_length * ((self.no + 1)/self.length))
        for user in users[start:end]:
            self.send(message,user)
        self.driver.close()


def send(weibouser,length,i):
    print(weibouser['name'])
    try:
        weibo = WeiboSpider(password=weibouser['pwd'], username=weibouser['name'], length=length, no=i)
        weibo.send_all(content)
    except Exception as e:
        print(e)
        time.sleep(100)
        send()


if __name__ == '__main__':
    while True:
        weibousers = [
            {"name": 'sc02@gewu.org.cn', "pwd": "LtERFTWQUYzEnu6"},
            {"name": 'adifus@gewu.org.cn', "pwd": "mGCWWX2EkLKJfBw"},
            {"name": 'sdiu@gewu.org.cn', "pwd": "LtERFTWQUYzEnu6"},
            {"name": 'dasdi@hotmail.com', "pwd": "LtERFTWQUYzEnu6"},
            {"name": 'er4rfvcxe3@gmail.com', "pwd": "LtERFTWQUYzEnu6"},
        ]
        length = len(weibousers)
        p = Pool(length)
        for i,weibouser in enumerate(weibousers):
            p.apply_async(send, args=(weibouser,length,i))
        print('Waiting for all subprocesses done...')
        p.close()
        p.join()
        print('All subprocesses done.')
        time.sleep(300)







