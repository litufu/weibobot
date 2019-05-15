import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from database import User
import pickle


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
        self.driver.get(url='https://passport.weibo.cn/signin/login')
        time.sleep(8)
        self.set_cookie()
        self.is_login()

    def is_login(self):
        # 判断是否登录
        html = self.driver.page_source
        # 判断是否登陆
        if html.find("W_ficon ficon_user S_ficon") == -1 and html.find('m-bubble m-bubble-red-s') == -1:
            # 没登录 ,则手动登录
            print('你没有登录')
            self.login()

    def login(self):
        # 登陆
        print('start login manual')
        try:
            # 电脑端
            username = self.driver.find_element_by_id('loginName')
        except Exception as e:
            # 手机端
            print(e)
            username = self.driver.find_element_by_id('loginname')
        username.send_keys(self.username)
        time.sleep(1)
        try:
            password = self.driver.find_element_by_id('loginPassword')
        except Exception as e:
            print(e)
            password = self.driver.find_element_by_name('password')
        password.send_keys(self.password)
        time.sleep(1)
        try:
            submit = self.driver.find_element_by_id('loginAction')
        except Exception as e:
            submit = self.driver.find_element_by_link_text('登录')
        submit.click()
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

    def search(self, userId, content):
        self.driver.get('https://www.weibo.com/u/' + userId)
        time.sleep(8)
        search_input = self.driver.find_element_by_class_name('W_input')
        search_input.send_keys(content)
        search_input.send_keys(Keys.RETURN)
        time.sleep(8)
        content = self.driver.page_source.encode('utf-8')
        print(content)
        soup = BeautifulSoup(content, 'html.parser')
        infos = soup.find_all("div", class_="info")

        for info in infos:
            print(info)
            children = info.contents
            if len(children) == 2 :
                name_div = children[1]
                nick_names = name_div.contents
                if len(nick_names) == 1:
                    url = nick_names[0]['href']
                    name = nick_names[0].get_text()
                    print(url)
                    print(name)
                elif len(nick_names) == 2:
                    if nick_names[1]['title'] == '微博会员':
                        url = nick_names[0]['href']
                        name = nick_names[0].get_text()
                        print(url)
                        print(name)





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
    weibo.search('7137663283', '高考')
    # 发帖
    # for bar_obj in session.query(Bar).all():
    #     barName = bar_obj.name
    #     post_title = '{}{}'.format(barName, get_title())
    #     post_content = '{}的同学们，{}'.format(barName, get_content())
    #     baidu.post(barName, post_title, post_content)
    # # 查看已发的帖子
    # baidu.get_ties()
    # #  回复已经发布的帖子
    # baidu.reply()


