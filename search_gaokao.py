from search import WeiboSpider


if __name__ == '__main__':
    weibo = WeiboSpider('ae56@gewu.org.cn', 'LtERFTWQUYzEnu6', '高考')
    weibo.get_all_user()
    