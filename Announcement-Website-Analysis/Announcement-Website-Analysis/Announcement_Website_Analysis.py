# -*- coding: utf-8 -*-
import requests, sys
import re    # 正则表达式
from bs4 import BeautifulSoup    #解析网页HTML

# 获取整个页面的源代码
def getHtml(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception('HTTP request error: %d' % resp.status_code)
    return resp.text

# 获取上交所公告
#sseHtml = getHtml("http://2016.sse.com.cn/disclosure/listedinfo/announcement/")
#print(html)
jcHtml = getHtml("http://www.cninfo.com.cn/cninfo-new/index/")

parsedHtml = BeautifulSoup(jcHtml, 'html.parser')
announcements = parsedHtml.find(id = 'con-a-1').find_all('li')
for item in announcements:
    # class=t1对应代码, class=t2对应名称
    print item.find(class_ = 't1').text, item.find(class_ = 't2').text
    # class=t3 or t4对应公告标题
    print ','.join(map(lambda item: item['title'] if item.get('title') != None else item.text.strip(), item.find_all('a')))
