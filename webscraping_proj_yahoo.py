  #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 21:16:33 2020

@author: pim01001
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt 



# reads in all the stocks and converts it to uppercase
stocks=pd.read_csv('/home/pim01001/Documents/Bootcamp/python/proj/yahoo/stock_info_big.csv')
stocks['Stocks']=stocks['Stocks'].str.upper()
# initialize empty dataframes
comb_df  = pd.DataFrame()
years =['2016', '2017','2018','2019']
stock_info = pd.DataFrame(columns=years)


for z in stocks['Stocks']:
    page1 = requests.get('https://finance.yahoo.com/quote/'+ z +'/financials?p='+z)
    print(page1.status_code) 
    
    yahoo = BeautifulSoup(page1.content, 'html.parser')
    ll=yahoo.find(class_="D(tbr) C($primaryColor)")

    # this will get us the Top Row
    len(list(ll.find_all('span')))
    list(ll.find_all('span'))[0].get_text()

    data= yahoo.find(class_="D(tbrg)")
    
  
    # getting col names information
    head_col = yahoo.find(class_="D(tbhg)")
    col_names=head_col.get_text(separator=':').split(':')

    
    # this gives header information for the table
    col_names.append('Ticker') 
    # col_names modified because of different financial year discrpency
    col_names_mod=[col_names[0],col_names[1],'Y2019','Y2018','Y2017','Y2016',col_names[6]]
    total= pd.DataFrame(columns=col_names_mod)
    #comb_df = pd.DataFrame(columns=col_names)
    
    # this gets data for the finacial table and for loop organizes it
    test = data.find_all(class_="D(tbr) fi-row Bgc($hoverBgColor):h")
    for i in range(len(test)):
        temp=test[i].get_text(separator=':').split(':')
        total.loc[i]=[str(temp[0])] + temp[1:6] +[str(z)]
    comb_df=comb_df.append(total.iloc[[0,4],])
    
    
    
    page2= requests.get('https://finance.yahoo.com/quote/' + z + '/history?period1=1454284800&period2=1577664000&interval=1mo&filter=history&frequency=1mo')
    
    yahoo_stock_history=BeautifulSoup(page2.content, 'html.parser')

    table=yahoo_stock_history.find(class_="W(100%) M(0)")
    table_body = table.find('tbody')
    
    #get the first colum
    stock_hist_col = table.find('thead')
    first_col_row=stock_hist_col.find_all('span')
    
    first_col_names = []
    for zz in range(len(first_col_row)):
        first_col_names.append(first_col_row[zz].get_text())
        
    
    
    stock_hist=pd.DataFrame(columns=first_col_names)
    
    row = table_body.find_all('tr')
    
    for u in range(len(row)):

        temp3=row[u].get_text(separator=':').split(':')
        # this skips lines with dividend income
        if 'Dividend' in temp3:
            continue
        else:
            stock_hist.loc[u]=temp3
    
    # gives us 
    stock_YOY_price=[]
    for n in years:
        stock_hist['index']=stock_hist['Date'].str.find(n)
        temp1=stock_hist['index']==8
        stock_YOY_price.append(pd.to_numeric(stock_hist[temp1]['Open'].str.replace(',','')).mean())
    
    # this formats the output
    stock_YOY_price=["%.2f" % member for member in stock_YOY_price]
    a_series=pd.Series(stock_YOY_price,index=stock_info.columns)
    stock_info=stock_info.append(a_series,ignore_index=True)
    # empty series for merging purposes
    a_series=pd.Series([0,0,0,0],index=stock_info.columns)
    stock_info=stock_info.append(a_series,ignore_index=True)
    # this converts number in these rows to 
    
# gets rid of commas and turn into int    
comb_df[col_names_mod[2:6]]=comb_df[col_names_mod[2:6]].apply(lambda x: x.str.replace(',','')).astype('int32')



def growth_percent(data_df):
    m,n=data_df.shape
    temp = pd.DataFrame(columns=data_df.columns)
    for b in range(n-1):
        temp.iloc[:,b]=((data_df.iloc[:,b]-data_df.iloc[:,b+1])/data_df.iloc[:,b+1])*100
        
    return temp  
      
#comb_df=comb_df.append(growth_percent(comb_df[col_names[2:6]]))
temp1=growth_percent(comb_df[col_names_mod[2:6]])
temp1=temp1.rename(columns={col_names_mod[2]:col_names_mod[2]+str(' % change'), col_names_mod[3]:col_names_mod[3]+str(' % change'),col_names_mod[4]:col_names_mod[4]+str(' % change')})
temp1[['Breakdown','Ticker']]=comb_df[['Breakdown','Ticker']]

# for combining stock YOY growth
#merges to comb_df the growth columns
comb_df=comb_df.merge(temp1, on=['Breakdown','Ticker'])
col_names=comb_df.columns
comb_df=pd.concat([comb_df,stock_info],axis=1,sort=False)
# add stock price

# rounding numbers to 2 decimal places
for h in col_names[2:6]:
    comb_df[h]=comb_df[h].apply(lambda x: '%1.2e' % x)

#comb_df=comb_df.round({col_names[2]:2,col_names[3]:2,col_names[4]:2,col_names[5]:2})
comb_df=comb_df.round({col_names[7]:2,col_names[8]:2,col_names[9]:2,col_names[5]:2})

# drops an unsused colum
comb_df=comb_df.drop(['Y2016_y'],axis=1)
# output CSV file
comb_df.to_csv(r'/home/pim01001/Documents/Bootcamp/python/proj/yahoo/comb.csv', index = False, header=True)

