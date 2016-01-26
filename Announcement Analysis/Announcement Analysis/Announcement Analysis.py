# -*- coding: utf-8 -*-
#------------------------------------------------------
import requests, sys, json
import re    # 正则表达式
from bs4 import BeautifulSoup    # 解析网页HTML
import pandas as pd    # 使用DataFrame保存、输出结果
from urlparse import *    # 解析网址
import ast
from datetime import date,datetime,time
import xlrd, xlwt    # version1 将分类结果保存到excel中再人为决策
# version2 将分类结果保存到sql中，盘中实时更新、提醒（if any）
#from sqlalchemy import create_engine    # pandas连接数据库的engine
#weight_engine = create_engine("mssql+pymssql://sa:666666@192.168.38.216/CSI_IndexWeight", encoding = 'UTF-8', echo = False)
#sql = "select EFFDATE,SECCODE,ISHARE from CSI_WEIGHT_HS300 where EFFDATE >= " + startdate + " and EFFDATE <= " + enddate + " order by EFFDATE,SECCODE"
#%time index_weight = pd.read_sql_query(sql, weight_engine)
#------------------------------------------------------


# 过程中以dictionary保存code、title、url
results = {'code':[], 'title':[], 'url':[]}


# 获取整个页面的源代码
def getHtml(url, headers={}, encoding=''):
    #print url
    #print headers
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception('HTTP request error: %d' % resp.status_code)
    if encoding != '':
        resp.encoding = encoding
    return resp.text


# 获取上交所公告
def getSSEAnnouncement(productId='', keyWord='', reportType='ALL', reportType2='', beginDate='', endDate=''):
    global results

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
        print item[0], item[1], item[3]
        results['code'].append(item[0])
        results['title'].append(item[1])
        results['url'].append('http://2016.sse.com.cn'+item[3])

date_of_today = datetime.today()
date_of_today = datetime.strftime(date_of_today, '%Y-%m-%d')
getSSEAnnouncement(beginDate=date_of_today, endDate=date_of_today)


# 获取深交所公告
#另外http://disclosure.szse.cn/m/search0425.jsp
#这是一个post的url地址，post的内容如这样: leftid=1&lmid=drgg&pageNo=2&stockCode=&keyword=&noticeType=&startTime=2016-01-25&endTime=2016-01-25&tzy=
#TODO: 写一个类似上海证券交易所的传各种参数的函数
def getSZSELast24h():
    global results

    respText = getHtml(url='http://disclosure.szse.cn//disclosure/fulltext/plate/szlatest_24h.js', encoding='gbk')
    literalList = respText[17:-2]
    last24 = ast.literal_eval(literalList)
    for item in last24:
        # example for item: ["300501","finalpage/2016-01-25/1201936491.PDF","海顺新材：首次公开发行股票并在创业板上市投资风险特别公告","PDF","353","2016-01-25","2016-01-25 00:00"]
        code, url = item[0], item[1]
        title = item[2]
        print code, title.decode('utf-8'), url
        results['code'].append(item[0])
        results['title'].append(item[2].decode('utf-8'))
        results['url'].append('http://disclosure.szse.cn/'+item[1])

getSZSELast24h()



# 为每一类公告在excel中增加一个sheet页
def addSheet2Excel(workbook, sheetname, data):
    sheet = workbook.add_sheet(sheetname, cell_overwrite_ok = True)
    for j in range(len(data.columns)):
        sheet.write(0, j, data.columns[j])
    for i in range(len(data.values)):
        for j in range(len(data.values[i])):
            sheet.write(i+1, j, data.values[i][j])
    return workbook

# 将公告分类保存到excel中
results = pd.DataFrame(results)
#results.to_excel('results.xlsx', '全部公告'.decode('utf-8'))
excel = xlwt.Workbook()
excel = addSheet2Excel(excel, u'全部公告', results)

# 信息披露类别：
# 8业绩预告、业绩快报和盈利预测
yjyg = results[results.title.apply(lambda x:u'业绩预' in x or u'业绩快报' in x or u'盈利预测' in x)]
excel = addSheet2Excel(excel, u'业绩预告', yjyg)

# 12股东增持或减持股份
gdzc = results[results.title.apply(lambda x:u'股东增持' in x)]
excel = addSheet2Excel(excel, u'股东增持', gdzc)

# 16重大资产重组
zccz = results[results.title.apply(lambda x:u'重大资产重组' in x)]
excel = addSheet2Excel(excel, u'重大资产重组', zccz)

# 17吸收合并
xshb = results[results.title.apply(lambda x:u'吸收合并' in x)]
excel = addSheet2Excel(excel, u'吸收合并', xshb)

# 18回购股份
hggf = results[results.title.apply(lambda x:u'回购股份' in x)]
excel = addSheet2Excel(excel, u'回购股份', hggf)

# 21股权激励及员工持股计划
cgjh = results[results.title.apply(lambda x:u'股权激励' in x or u'员工持股计划' in x)]
excel = addSheet2Excel(excel, u'员工持股计划', cgjh)

excel.save(date_of_today+'.xls')