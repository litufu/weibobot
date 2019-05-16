import time
import  re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import User, Base
import pickle


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
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(
            executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
            options=chrome_options)
        self.driver.get(url='http://s.weibo.com/')

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
        self.save_cookie()

    def save_cookie(self):
        '''保存cookie'''
        # 将cookie序列化保存下来
        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))

    def set_cookie(self):
        '''往浏览器添加cookie'''
        '''利用pickle序列化后的cookie'''
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
            time.sleep(8)
        except Exception as e:
            print(e)

    def search(self):
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

    def send(self,content):
        users = session.query(User).filter(User.send == False).all()
        for user in users:
            print(user.uid)
            url = 'https://api.weibo.com/chat/#/chat?to_uid={}'.format(user.uid)
            self.driver.get(url)
            self.driver.refresh()
            WebDriverWait(self.driver, 10
                          ).until(EC.presence_of_element_located((By.ID, "webchat-textarea")))
            webchat = self.driver.find_element_by_id('webchat-textarea')
            webchat.clear()
            webchat.send_keys(content)
            webchat.send_keys(Keys.ENTER)
            user.send = True
            session.commit()
            time.sleep(10)

    def get_all_user(self):

        self.get_user()
        for i in range(49):
            self.next()
            time.sleep(10)
            self.get_user()

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












    # def post(self, bar_name, title, content):
    #     self.driver.get('http://tieba.baidu.com/f?kw={}'.format(bar_name))
    #     time.sleep(5)
    #     # 将页面滚动条拖到底部
    #     js = "var q=document.documentElement.scrollTop=10000"
    #     self.driver.execute_script(js)
    #     time.sleep(3)
    #     # 输入标题
    #     title_input = self.driver.find_element_by_name('title')
    #     title_input.send_keys(title)
    #     time.sleep(3)
    #     # 输入内容
    #     ueditor_replace = self.driver.find_element_by_id('ueditor_replace')
    #     self.driver.execute_script("arguments[0].innerHTML='<p>{}</p>'".format(content), ueditor_replace)
    #     time.sleep(3)
    #     # 点击提交
    #     button = self.driver.find_element_by_class_name('poster_submit')
    #     # button.click()
    #     sleep_time = random.randint(5, 15)
    #     time.sleep(sleep_time)
    #
    # def get_ties(self):
    #     self.driver.get('http://tieba.baidu.com/i/i/my_tie')
    #     tables = self.driver.find_elements_by_tag_name('table')
    #     for table in tables:
    #         bar_tag = table.find_element_by_class_name('nowrap').find_element_by_tag_name('a')
    #         bar_name = bar_tag.text[:-1]
    #         bars = session.query(Bar).filter(Bar.name == bar_name).all()
    #         if len(bars) == 0:
    #             bar = Bar(name=bar_name)
    #         else:
    #             bar = bars[0]
    #         tie_tag = table.find_element_by_class_name('wrap').find_element_by_tag_name('a')
    #         tie_url = tie_tag.get_attribute('href')
    #         tie = Tie(url=tie_url, bar_id=bar.id, bar=bar)
    #         session.add(tie)
    #         session.commit()
    #
    # def reply(self):
    #     ties = session.query(Tie).all()
    #     for tie in ties:
    #         if '高' in tie.bar.name or '中' in tie.bar.name:
    #             self.driver.get(tie.url)
    #             # 将页面滚动条拖到底部
    #             js = "var q=document.documentElement.scrollTop=10000"
    #             self.driver.execute_script(js)
    #             time.sleep(3)
    #             reply_content = get_reply()
    #             # 输入内容
    #             ueditor_replace = self.driver.find_element_by_id('ueditor_replace')
    #             self.driver.execute_script("arguments[0].innerHTML='<p>{}</p>'".format(reply_content), ueditor_replace)
    #             time.sleep(3)
    #             # 点击提交
    #             button = self.driver.find_element_by_class_name('poster_submit')
    #             button.click()
    #             sleep_time = random.randint(5, 15)
    #             time.sleep(sleep_time)


if __name__ == '__main__':
    # 登陆
    weibo = WeiboSpider('sc01@gewu.org.cn', 'asdfew8803s')  # 你的微博账号，密码
    # 搜搜
    weibo.login()
    # weibo.search('高考')
    # weibo.get_user()
    # 发帖
    weibo.send('你好')
    # for bar_obj in session.query(Bar).all():
    #     barName = bar_obj.name
    #     post_title = '{}{}'.format(barName, get_title())
    #     post_content = '{}的同学们，{}'.format(barName, get_content())
    #     baidu.post(barName, post_title, post_content)
    # # 查看已发的帖子
    # baidu.get_ties()
    # #  回复已经发布的帖子
    # baidu.reply()


