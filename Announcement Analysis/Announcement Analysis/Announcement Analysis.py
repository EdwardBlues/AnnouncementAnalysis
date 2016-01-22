# -*- coding: utf-8 -*-
import requests, sys, json
# import re    # 正则表达式
from bs4 import BeautifulSoup    # 解析网页HTML
import pandas as pd    # 使用DataFrame保存、输出结果
from urlparse import *    # 解析网址


# 保存公告内容的DataFrame
anncmt = pd.DataFrame(columns=('code', 'name', 'title', 'href'))

# 获取整个页面的源代码
def getHtml(url, headers={}):
    print url
    print headers
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception('HTTP request error: %d' % resp.status_code)
    return resp.text


# 0. js获取数据的上交所、深交所公告（有待处理js）
#    刷新可能比巨潮及时
#    上交所盘中无公告，但深交所全天随时出公告，盘中对股票有影响
#sseHtml = getHtml("http://2016.sse.com.cn/disclosure/listedinfo/announcement/")    # 上交所
#szseHtml = getHtml("http://disclosure.szse.cn/m/drgg.htm")    # 深交所
"""
无需处理JS，直接看发的http请求，比如上交所
query.sse.com.cn/infodisplay/queryLatestBulletinNew.do?
isPagination=true&productId&keyWord&reportType2&reportType=ALL&beginDate=2016-01-22&endDate=2016-01-22
其中productId,keyWord,reportType,reportType2,beginDate,endDate对应上交所页面上的查询条件
"""
def getSSEAnnouncement(productId='', keyWord='', reportType='ALL', reportType2='', beginDate='', endDate=''):
    rowData = []
    headers = {'Referer':'http://2016.sse.com.cn/disclosure/listedinfo/announcement/'}
    reqURL = 'http://query.sse.com.cn/infodisplay/queryLatestBulletinNew.do?isPagination=false&productId={0}&keyWord={1}&reportType={2}&reportType2={3}&beginDate={4}&endDate={5}'.format(productId,keyWord,reportType,reportType2,beginDate,endDate)
    respJson = json.loads(getHtml(url=reqURL, headers=headers))
    rowData.extend(respJson['pageHelp']['data'])
    total = int(respJson['pageHelp']['total'])
    pageSize = int(respJson['pageHelp']['pageSize'])
    pageCount = int(respJson['pageHelp']['pageCount'])
    cachedCount = int(respJson['pageHelp']['cacheSize'])
    nextPageBegin = cachedCount + 1
    nextCacheSize = pageCount - cachedCount
    reqURL = 'http://query.sse.com.cn/infodisplay/queryLatestBulletinNew.do?isPagination=false&productId={0}&keyWord={1}&reportType={2}&reportType2={3}&beginDate={4}&endDate={5}&pageHelp.pageSize={6}&pageHelp.pageCount={7}&pageHelp.beginPage={8}&pageHelp.cacheSize={9}'.format(productId, keyWord, reportType, reportType2, beginDate, endDate, pageSize, pageCount, nextPageBegin, nextCacheSize)
    respJson = json.loads(getHtml(url=reqURL, headers=headers))
    rowData.extend(respJson['pageHelp']['data'])
    data = map(lambda item: [item['security_Code'], item['title'], item['SSEDate'],item['URL']], rowData)
    for item in data:
        # print item[0], item[1], item[2], item[3]
        print item[2], item[0], item[1]
        print item[3]
        print ''
    return data

getSSEAnnouncement(beginDate='2016-01-22', endDate='2016-01-22')

# 1. 巨潮资讯最新公告，可能比较及时，但不全
#def getCnInfoNews():
#    jcHttp = "http://www.cninfo.com.cn/cninfo-new/index/"
#    jcRoot = urlparse(jcHttp).netloc    # 自动获取根域名
#    jcHtml = getHtml(jcHttp)

#    parsedHtml = BeautifulSoup(jcHtml, 'html.parser')
#    announcements = parsedHtml.find(id = 'con-a-1').find_all('li')
#    for item in announcements:
#        # class=t1对应代码, class=t2对应名称
#        code = item.find(class_ = 't1').text
#        name = item.find(class_ = 't2').text
#        print code, name
#        # class是python的关键字，所以后面要加个_

#        ## class=t3 or t4对应公告标题
#        #print ', '.join(map(lambda item: item['title'] if item.get('title') != None else item.text.strip(), item.find_all('a')))
#        ## item.get('title') 是不是等价于 item.title ？ item.find_all('a') 是不是等价于 item.select('a') ？

#        for cont in item.find_all('a'):
#            title = cont['title'] if cont.get('title') != None else cont.text.strip()
#            print title
#            href = jcRoot + cont.get('href')
#            print href
#            row = pd.DataFrame([dict(code = code, name = name, title = title, href = href)])
#            anncmt = anncmt.append(row, ignore_index=True)

#        print ''

    # 将结果保存到excel
    #anncmt.to_excel('anncmt.xlsx')

# 2. 巨潮资讯sse沪市公告。。似乎同样是js取得的数据
#    http://www.cninfo.com.cn/cninfo-new/disclosure/sse

# 3. 巨潮资讯szse深市公告
#    http://www.cninfo.com.cn/cninfo-new/disclosure/szse