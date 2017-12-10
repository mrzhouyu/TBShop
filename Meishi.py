#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/10 2:46
# @Author  : Yu
# @Site    : 
# @File    : Meishi.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
from pyquery import PyQuery as pq
from config import *
import pymongo
import time
from multiprocessing import Pool
'''
数据库配置
'''
client=pymongo.MongoClient(MONGO_HOST)
db=client[MONGO_DB]

'''
selenium初始化
'''
#引入config.py配置文件
driver=webdriver.PhantomJS(service_args=PHANTOMJS_ARGS)
#设置浏览器窗口尺寸
driver.set_window_size(1400,900)
def selenium_search():
    print('正在进入网站第一页...')
    #引入异常处理
    try:
        driver.get('https://www.taobao.com/')
        #等待输入框判断 直到输入框加载出来
        T_input=WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#q')))
        #等待按钮判断
        submit=WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button')))
        #输入框输入内容
        T_input.send_keys('美食')
        #点击提交
        submit.click()
        #判断页面或者总页数是否显示出来
        pages=WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))
        # 加载完毕解析页面
        get_page_info()
        #返回选择器的内容
        return pages.text
    except TimeoutException:
        #异常处理 重新请求
        return selenium_search()

def next_page(page):
    print('翻页到第{}页'.format(page))
    #得到下一页的输入框和确定按钮
    try:
        T_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        # 等待按钮判断
        submit = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        # 清楚输入框已经有的内容  重新输入框输入内容
        T_input.clear()
        T_input.send_keys(page)
        # 点击提交
        submit.click()
        #提交后判断是否翻页成功 根据选择器出现的内容判断
        WebDriverWait(driver,10).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page)))
        #加载完毕解析页面
        get_page_info()
    except TimeoutException:
        next_page(page)

def get_page_info():
    #等待页面信息加载出来
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item')))
    html=driver.page_source
    print('开始分析源代码')
    doc=pq(html)
    #查找信息
    items=doc('#mainsrp-itemlist .items .item').items()
    print('正在解析数据...')
    for item in items:
        contents={
            'image':item.find('.pic .img').attr('src'),
            'price':item.find('.price').text(),
            'deals':item.find('.deal-cnt').text()[:-3],
            'name':item.find('.title').text(),
            'shopname':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        save_Mongodb(contents)
    print('当前页面数解析存储完毕...')


def save_Mongodb(datas):
    try:
        if db[MONGO_TABLE].insert(datas):
            print('保存到数据库成功')
    except Exception:
        print('保存数据失败',datas)

def main():
    try:
        all_pages=selenium_search()
        #清洗数据得到总页数整数
        all_pages=int(re.search(r'(\d+)',all_pages).group(1))
        #遍历所有页面
        for number in range(2,all_pages+1):
            try:
                next_page(number)
            except:
                print('第{}页出现错误'.format(number))
                # 这一步很有必要 某一页出现异常不至于结束整个程序 尽可能获得多的数据
                if number<100:
                    continue
    except Exception:
        print('ERROR')
    finally:
    #执行完毕关闭浏览器...
        driver.close()

if __name__ == '__main__':
    start_time=time.time()
    main()
    print('程序执行完毕','总共花费了{}s'.format(time.time()-start_time))