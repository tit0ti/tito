#!/usr/bin/env python
# coding: utf-8

# In[6]:


import pyupbit
import time
import datetime
import pandas as pd
import telegram # pip install python-telegram-bot
import json
import os
import pytz
import schedule

access = "p6WIbQ6x0L4jfdhRtRvOLaFqU4PHL6iF43VUyyNZ"
secret = "3cB0K6mdnBGTUVkbDiK87xYj18qslonXc4bAxxTG"
chat_id = "5024342640"
bot = telegram.Bot(token = '5026879581:AAH4d2l9cGTk9RcpTLzVWyZiorsHgrs2h50')
upbit = pyupbit.Upbit(access, secret)
code_list = ['KRW-BTC','KRW-ETH','KRW-LINK']

# 오후 수익률
def get_day_revenue(ticker):
    df = pyupbit.get_ohlcv(ticker, interval='minutes60', count=24)
    day_revenue = (df.iloc[23]['close']- df.iloc[11]['close'])/ df.iloc[11]['close']
    return day_revenue

# 오후 거래량
def get_day_volume(ticker):
    df = pyupbit.get_ohlcv(ticker, interval='minutes60', count=24)
    day_volume = (df.iloc[23]['volume']- df.iloc[12]['volume'])
    return day_volume

# 오전거래량
def get_mor_volume(ticker):
    df = pyupbit.get_ohlcv(ticker, interval='minutes60', count=24)
    mor_volume = (df.iloc[0]['volume']- df.iloc[11]['volume'])
    return mor_volume

# 오전변동성
def get_avb(ticker):
    high_list = []
    low_list = []
    df = pyupbit.get_ohlcv(ticker, interval='minutes60', count=24)
    for i in range(11):
        a = df.iloc[i]['high']
        high_list.append(a)
        b = df.iloc[i]['low']
        low_list.append(b)
        time.sleep(0.2)
    high_list.sort()
    high = high_list[10] #전일 오전 고가
    low_list.sort()
    low = low_list[0] #전일 오전 저가
    open_price = df.iloc[0]['open'] #전일 시가
    avb = (high- low) / open_price
    return avb

# 잔고조회
def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0
# krw_balance = upbit.get_balance("KRW")


def job_B():
    krw_balance = upbit.get_balance("KRW")
    n= len(code_list)
    day_revenue = []
    day_volume = []
    mor_volume = []
    invest_ratio = []
    having_coin = []
    market_timing =[]
    for i in code_list:
        a = get_day_revenue(i)
        day_revenue.append(a)
    time.sleep(0.2)
    #오전 거래량
    for i in code_list:
        a = get_day_volume(i)
        day_volume.append(a)
    time.sleep(0.2)
    #오후 거래량
    for i  in code_list:
        a = get_mor_volume(i)
        mor_volume.append(a)
    time.sleep(0.2)
    # 투자비중
    for i  in code_list:
        k = 0.02
        avb = get_avb(i)
        a= (krw_balance/2)/ n *(k / avb)
        invest_ratio.append(a)
    time.sleep(0.2)
    # 마켓타이밍
    for i in range(n):
        a = day_revenue[i] > 0 and day_volume[i] > mor_volume[i]
        if a ==0:
            a = 'OFF'
        else:
            a = 'ON'
        market_timing.append(a)
        time.sleep(0.2)
    for i in range(n):
        print(code_list[i], market_timing[i],invest_ratio[i])
        msg = "전략B : {}\n".format(code_list[i]) + "마켓 : {}\n".format(market_timing[i]) + "투자금액 : {} ".format(invest_ratio[i])
        bot.sendMessage(chat_id=chat_id, text= msg)
    return 0


schedule.every().day.at("23:59").do(job_B)

while True:
    schedule.run_pending()
    time.sleep(1)


# In[ ]:




