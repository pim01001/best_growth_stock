#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 08:45:31 2020

@author: pim01001
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd

page2= requests.get('https://finance.yahoo.com/quote/GOOG/history?period1=1454284800&period2=1577664000&interval=1mo&filter=history&frequency=1mo')

yahoo_stock_history=BeautifulSoup(page2.content, 'html.parser')

table=yahoo_stock_history.find(class_="W(100%) M(0)")
table_body = table.find('tbody')

#get the first colum
stock_hist_col = table.find('thead')
first_col_row=stock_hist_col.find_all('span')

first_col_names = []
for z in range(len(first_col_row)):
    first_col_names.append(first_col_row[z].get_text())
    


stock_hist=pd.DataFrame(columns=first_col_names)

row = table_body.find_all('tr')

for u in range(len(row)):
    stock_hist.loc[u]=row[u].get_text(separator=':').split(':')

# gives us 
years =['2016', '2017','2018','2019']
stock_YOY_price=[]
for n in years:
    stock_hist['index']=stock_hist['Date'].str.find(n)
    temp1=stock_hist['index']==8
    stock_YOY_price.append(pd.to_numeric(stock_hist[temp1]['Open'].str.replace(',','')).mean())

# this formats the output
stock_YOY_price=["%.2f" % member for member in stock_YOY_price]