# -*- coding: utf-8 -*-
import requests, sys, json
# import re    # ????????ʽ
from bs4 import BeautifulSoup    # ??????ҳHTML
import pandas as pd    # ʹ??DataFrame???桢????????
from urlparse import *    # ??????ַ


# ???湫?????ݵ?DataFrame
anncmt = pd.DataFrame(columns=('code', 'name', 'title', 'href'))


# ??ȡ????ҳ????Դ????
def getHtml(url, headers={}):
    print url
    print headers
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception('HTTP request error: %d' % resp.status_code)
    return resp.text


# 0. js??ȡ???ݵ??Ͻ???????????棨?д?????js??
#    ˢ?¿??ܱȾ޳???ʱ
#    ?Ͻ????????޹??棬?????ȫ????ʱ?????棬???жԹ?Ʊ??Ӱ??
#sseHtml = getHtml("http://2016.sse.com.cn/disclosure/listedinfo/announcement/")    # ?Ͻ???
#szseHtml = getHtml("http://disclosure.szse.cn/m/drgg.htm")    # ???
"""
???账??JS??ֱ?ӿ?????http???󣬱????Ͻ???
query.sse.com.cn/infodisplay/queryLatestBulletinNew.do?
isPagination=true&productId&keyWord&reportType2&reportType=ALL&beginDate=2016-01-22&endDate=2016-01-22
????productId,keyWord,reportType,reportType2,beginDate,endDate??Ӧ?Ͻ???ҳ???ϵĲ?ѯ????
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

getSSEAnnouncement(beginDate='2016-01-01', endDate='2016-01-01')

# 1. ?޳???Ѷ???¹??棬???ܱȽϼ?ʱ??????ȫ
#def getCnInfoNews():
#    jcHttp = "http://www.cninfo.com.cn/cninfo-new/index/"
#    jcRoot = urlparse(jcHttp).netloc    # ?Զ???ȡ??????
#    jcHtml = getHtml(jcHttp)

#    parsedHtml = BeautifulSoup(jcHtml, 'html.parser')
#    announcements = parsedHtml.find(id = 'con-a-1').find_all('li')
#    for item in announcements:
#        # class=t1??Ӧ????, class=t2??Ӧ????
#        code = item.find(class_ = 't1').text
#        name = item.find(class_ = 't2').text
#        print code, name
#        # class??python?Ĺؼ??֣????Ժ???Ҫ?Ӹ?_

#        ## class=t3 or t4??Ӧ????????
#        #print ', '.join(map(lambda item: item['title'] if item.get('title') != None else item.text.strip(), item.find_all('a')))
#        ## item.get('title') ?ǲ??ǵȼ??? item.title ?? item.find_all('a') ?ǲ??ǵȼ??? item.select('a') ??

#        for cont in item.find_all('a'):
#            title = cont['title'] if cont.get('title') != None else cont.text.strip()
#            print title
#            href = jcRoot + cont.get('href')
#            print href
#            row = pd.DataFrame([dict(code = code, name = name, title = title, href = href)])
#            anncmt = anncmt.append(row, ignore_index=True)

#        print ''

    # ?????????浽excel
    #anncmt.to_excel('anncmt.xlsx')

# 2. ?޳???Ѷsse???й??档???ƺ?ͬ????jsȡ?õ?????
#    http://www.cninfo.com.cn/cninfo-new/disclosure/sse

# 3. ?޳???Ѷszse???й???
#    http://www.cninfo.com.cn/cninfo-new/disclosure/szse