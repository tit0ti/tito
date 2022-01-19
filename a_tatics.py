#!/usr/bin/env python
# coding: utf-8

# In[29]:


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
code_list = ['KRW-BTC','KRW-XRP','KRW-LINK']
k = 0.02  #타킷변동성
n = len(code_list)

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

# 전일 오전 레인지 구하기
def get_mor_range(ticker):
    high_list = []
    low_list = []
    df = pyupbit.get_ohlcv(ticker, interval='minutes60', count=24)
    for i in range(11):
        a = df.iloc[i]['high']
        high_list.append(a)
        b = df.iloc[i]['low']
        low_list.append(b)
    high_list.sort()
    high = high_list[0] #전일 고가
    low_list.sort()
    low = low_list[0] #전일 저가
    mor_range = high -low
    return mor_range

#현재가 조회 (당일시가)
def get_current_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval='minutes60', count=1)
    current_price = df.iloc[0]['close']
    return current_price

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
    high_list.sort()
    high = high_list[0] #전일 오전 고가
    low_list.sort()
    low = low_list[0] #전일 오전 저가
    open_price = df.iloc[0]['open'] #전일 시가
    avb = (high - low) / open_price
    return avb

# 20일평균 노이즈
def get_avg_noise_20(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="days", count= 21)
    case = []
    for i in range(20):
        noise_20 = 1- abs((df.iloc[i]['open'] - df.iloc[i]['close']) / (df.iloc[i]['high'] - df.iloc[i]['low']))
        case.append(noise_20)
    n = len(case)
    avg_noise_20 = sum(case)/ n
    return avg_noise_20

#티커로 ma구하기
def get_ma3(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minutes60", count= 36)
    ma3 = df['close'].rolling(36).mean().iloc[-1]
    return ma3
def get_ma5(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minutes60", count= 60)
    ma5 = df['close'].rolling(60).mean().iloc[-1]
    return ma5
def get_ma10(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minutes60", count= 120)
    ma10 = df['close'].rolling(120).mean().iloc[-1]
    return ma10
def get_ma20(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minutes60", count= 180)
    ma20 = df['close'].rolling(180).mean().iloc[-1]
    return ma20

#3,5,10,20일 평균 이동평균선 스코어
def get_ma_score(ticker):
    last_candle_close = get_current_price(ticker)
    ma3 = get_ma3(ticker) <= last_candle_close
    ma5 = get_ma5(ticker) <= last_candle_close
    ma10 = get_ma10(ticker) <=last_candle_close
    ma20 = get_ma20(ticker) <= last_candle_close
    ma_score = (ma3 + ma5 + ma10 + ma20)/ 4
    return ma_score

def job():
    range_list = []
    noise_list = []
    ma_score_list = []
    avb_list = []
    current_price_list = []
    krw_balance = upbit.get_balance("KRW") #현금
    for i in code_list:
        a =get_current_price(i)
        current_price_list.append(a)
        time.sleep(0.2)
    for i in code_list:
        a = get_mor_range(i)
        range_list.append(a) # range
        time.sleep(0.2)
    for i in code_list:
        a = get_avg_noise_20(i)
        noise_list.append(a) #noise
        time.sleep(0.2)
    for i in code_list:
        a = get_ma_score(i)
        ma_score_list.append(a) # ma스코어
        time.sleep(1)
    for i in code_list:
        a = get_avb(i)
        avb_list.append(a) #변동성
        time.sleep(0.2)
    target_price = []
    bid_money = []
    for i in range(n):
        a = current_price_list[i] + (range_list[i]* noise_list[i]) # 목표가격
        b = k / avb_list[i] * ma_score_list[i] * krw_balance / n / 2  # 투자금액
        target_price.append(a)
        bid_money.append(b)
        time.sleep(0.2)
    for j in range(n):
        msg = "전략A : {}\n".format(code_list[j]) + "목표가격 : {}\n".format(target_price[j]) + "투자금액 : {} ".format(bid_money[j])
        bot.sendMessage(chat_id=chat_id, text= msg)
    return 0

schedule.every().day.at("23:59").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)


# In[ ]:




