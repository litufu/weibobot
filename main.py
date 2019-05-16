from search import WeiboSpider

if __name__ == '__main__':
    # 搜索高考
    weibo1 = WeiboSpider('sc01@gewu.org.cn', 'asdfew8803s', '高考')  # 你的微博账号，密码
    weibo1.get_all_user()

    # 搜索高

