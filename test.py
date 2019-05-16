str = 'https://weibo.com/5282105031?refer_flag=1001030103_'

pattern = re.compile('.*weibo.com/(\d+)?.*?')
res = re.match(pattern,str)
print(res[1])