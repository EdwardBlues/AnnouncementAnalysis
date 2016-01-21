# -*- coding: utf-8 -*-
import urllib.request as ur
import re    # 正则表达式


# 获取整个页面的源代码
def getHtml(url):
    request = ur.Request(url)
    response = ur.urlopen(request)
    html = response.read()
    return html


# 获取网页源代码中的某项资源列表
def getTitle(html):
    html = html.decode('utf-8')
    # pattern = re.compile(r'title="(.*?)"')    # 非贪婪粗糙匹配title
    #pattern = re.compile(r'target="_blank">(.+?)</a>')
    pattern = re.compile(r'<li>(.+?)</li>')
    titles = re.findall(pattern, html)
    return list(set(titles))


# 获取上交所公告
#sseHtml = getHtml("http://2016.sse.com.cn/disclosure/listedinfo/announcement/")
#print(html)
jcHtml = getHtml("http://www.cninfo.com.cn/cninfo-new/index/")
# 获取公告标题列表
jcTitle = getTitle(jcHtml)


print(jcTitle)