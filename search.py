import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import pickle
import json
import os
from PIL import Image
from database import User, Base
from lzdm import code


pattern = re.compile('.*weibo.com/(\d+)?.*?')
engine = create_engine('sqlite:///weibo.sqlite')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class WeiboSpider(object):
    def __init__(self, username, password,content):
        self.username = username
        self.password = password
        self.content = content
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(
            executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
            options=chrome_options)
        self.driver.set_window_size(1200, 900)
        self.driver.get(url='http://s.weibo.com/')
        self.driver.save_screenshot('test{}.png'.format(self.username[0:4]))
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
        f1 = open('cookie.txt', 'w')
        f1.write(json.dumps(self.driver.get_cookies()))
        f1.close

    def set_cookie(self):
        '''往浏览器添加cookie'''
        '''利用pickle序列化后的cookie'''
        try:
            f1 = open('cookie.txt')
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
        time.sleep(3)
        # 人工输入手机验证码
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
        time.sleep(30)
        self.save_cookie()

    def search(self):
        self.driver.get(url='http://s.weibo.com/')
        self.driver.refresh()
        WebDriverWait(self.driver, 10
                      ).until(EC.presence_of_element_located((By.CLASS_NAME, "gn_name")))
        search_input = self.driver.find_element_by_class_name("search-input").find_element_by_tag_name('input')
        search_input.clear()
        search_input.send_keys(self.content)
        self.driver.find_element_by_class_name('s-btn-b').click()
        time.sleep(10)

    def next(self):
        next_page = self.driver.find_element_by_class_name('m-page').find_element_by_class_name('next')
        next_page.click()

    def get_all_user(self):
        try:
            self.search()
            self.get_user()
            for i in range(30):
                self.next()
                sleep_time = random.randint(3, 8)
                time.sleep(sleep_time)
                self.get_user()
        except Exception as e:
            print(e)
        finally:
            self.driver.close()

    def get_user(self):
        try:
            WebDriverWait(self.driver, 10
                          ).until(EC.presence_of_element_located((By.CLASS_NAME, "info")))
            print('电脑')
            infos = self.driver.find_elements_by_class_name('info')
            for info in infos:
                divs = info.find_elements_by_tag_name('div')
                if len(divs) == 2:
                    title = divs[1]
                    links = title.find_elements_by_tag_name('a')
                    nick_name = links[0].text
                    href = links[0].get_attribute("href")
                    res = re.match(pattern, href)
                    uid = res[1]
                    if len(links) == 1 or (len(links) == 2 and links[1].get_attribute('title') == "微博会员"):
                        users = session.query(User).filter(User.uid == uid).all()
                        if len(users) == 0:
                            user = User(name=nick_name, url=href, uid=uid, send=False)
                            session.add(user)
                            session.commit()
        except TimeoutException as e:
            WebDriverWait(self.driver, 10
                          ).until(EC.presence_of_element_located((By.CLASS_NAME, "ctype-2")))
            print('手机')
            cards = self.driver.find_elements_by_class_name('ctype-2')
            for card in cards:
                panels = card.find_elements_by_class_name('m-panel')
                for panel in panels:
                    header = panel.find_element_by_tag_name('header')
                    image = header.find_element_by_class_name('m-img-box')
                    gold = image.find_elements_by_class_name('m-icon-goldv-static')
                    blue = image.find_elements_by_class_name('m-icon-bluev')
                    if (len(gold) > 0) or (len(blue) > 0):
                        print('gold')
                    else:
                        nick_name = header.find_element_by_class_name('m-text-box').find_element_by_tag_name('a')
                        print(nick_name.get_text())


def send():
    keywords = ['高考', '高三', '高中']
    try:
        while True:
            for keyword in keywords:
                weibo = WeiboSpider('ae56@gewu.org.cn', 'LtERFTWQUYzEnu6', keyword)
                # weibo = WeiboSpider('litufu001', '123456abc', keyword)
                weibo.get_all_user()
    except Exception as e:
        print(e)
        time.sleep(300)
        send()


if __name__ == '__main__':
    send()



