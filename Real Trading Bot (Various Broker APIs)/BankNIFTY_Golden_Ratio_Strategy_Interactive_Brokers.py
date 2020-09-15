#Interactive Brokers API
#Author: Priyank Sharma

#The BankNIFTY Golden Ratio Strategy
##Scrip = BANKNIFTY Futures

## Golden Number = ((Previous Day High - Previous Day Low) + Opening Range of Today's First 10 minutes))*61.8%

### Buy Above = (Previous Day Close + Golden Number)
### Sell Below = (Previous Day Close - Goldern Number)

#### Stop Loss at 0.5% Target at 2%

from ibapi.comm import *
from ibapi.message import IN, OUT
from ibapi.client import EClient
from ibapi.connection import Connection
from ibapi.reader import EReader
from ibapi.utils import *
from ibapi.execution import ExecutionFilter
from ibapi.scanner import ScannerSubscription
from ibapi.order_condition import *
from ibapi.contract import *
from ibapi.order import *
from ibapi.order_state import *

import datetime
import datetime as dt
from datetime import timedelta
#import quandl as qdl
# Install https://www.anaconda.com/download/
#import pandas_datareader as pdr
import pandas as pd
# Import Matplotlib's `pyplot` module as `plt`
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
#import statsmodels.api as sm
# Import the `datetools` module from `pandas`
#from pandas.core import datetools
import pandas.tseries as pdts
import talib
import pandas_ta as ta
from nsepython import *
from datetime import*
from ib_insync import *

util.startLoop()
ib=IB()
ib.connect('127.0.0.1', 4002, clientId=1092)

def PlaceOrder (contract,action,limitprice ):
    print (contract,action, lots)
    #[details] = ib.reqTickers(contract)
                #print (details)
                #print (2*(details.ask-details.bid)/(details.ask+details.bid),symbol)
    #if ((details.ask-details.bid)/(details.ask+details.bid)<0.02):
    order = Order()
    order.action = action
    order.orderType = "LMT"
    order.totalQuantity = 25
    if (action=="BUY"):
        order.lmtPrice=limitprice
    else :
        order.lmtPrice=limitprice

    trade1 = ib.placeOrder(contract, order)


#Getting All the Necessary Variables
symbol="BANKNIFTY"
banknifty_info=nse_quote_meta(symbol,"latest","Fut")
fetch_url="https://www.nseindia.com/api/historical/fo/derivatives?&expiryDate="+str(banknifty_info['expiryDate'])+"&instrumentType=FUTIDX&symbol=BANKNIFTY"
historical_data = nsefetch(fetch_url)
historical_data = pd.DataFrame(historical_data['data'])
previous_day_high = historical_data['FH_TRADE_HIGH_PRICE'].iloc[0]
previous_day_low = historical_data['FH_TRADE_LOW_PRICE'].iloc[0]
range_high = banknifty_info['highPrice']
range_low = banknifty_info['lowPrice']
opening_range = range_high-range_low
golden_number = (float(previous_day_high)-float(previous_day_low)+opening_range)*.618
previous_day_close = banknifty_info['prevClose']
buy_above = int(previous_day_close+golden_number)
sell_below = int(previous_day_close-golden_number)
print("Buy BankNIFTY Above: "+str(buy_above)+".")
print("Sell BankNIFTY Below: "+str(sell_below)+".")

y=datetime.strptime((banknifty_info['expiryDate']),"%d-%b-%Y").strftime("%Y%m%d")
contract = Contract()
contract.symbol = symbol
contract.secType = "FUT"
contract.exchange = "NSE"
contract.currency = "INR"
contract.lastTradeDateOrContractMonth = y

#Entering the Trade
while True:
    bn_ltp = nse_quote_ltp("BANKNIFTY","latest","Fut")
    print("Current Value of BankNIFTY: " + str(bn_ltp))
    who_triggered = "NONE"
    #Amit's Test
    ##bn_ltp = 21949
    if(bn_ltp>buy_above):
        PlaceOrder(contract,"BUY",bn_ltp)
        print("Buy Order executed at: " +str(bn_ltp)+". Entry Time is "+ str(run_time)+".")
        who_triggered = "BUY"
        stop_loss = bn_ltp*(.995)
        target = bn_ltp*(1.02)
    if(bn_ltp<sell_below):
        PlaceOrder(contract,"SELL",bn_ltp)
        print("Sell Order executed at: " +str(bn_ltp)+". Entry Time is "+ str(run_time)+".")
        who_triggered = "SELL"
        stop_loss = bn_ltp*(1.005)
        target = bn_ltp*(.98)
    if(who_triggered != "NONE"):
        entry_price = run_time
        entry_price = bn_ltp
        print("Stop Loss is: " + str(stop_loss)+".")
        print("Target is: " + str(target)+".")
        break
    time.sleep(10)
	
#Managing the Trade
while True:
    bn_ltp = nse_quote_ltp("BANKNIFTY","latest","Fut")
    print("Current Value of BankNIFTY: " + str(bn_ltp))
    exit_time = run_time
    exit_price = bn_ltp
    if(who_triggered == "BUY"):
        if(bn_ltp>target):
            PlaceOrder(contract,"SELL",bn_ltp)
            print("Target hit at: "+ str(bn_ltp)+". Exit Time is "+ str(run_time)+".")
            print("Net Profit: "+str(abs(entry_price-exit_price))+" points.")
            break
        if(bn_ltp<stop_loss):
            PlaceOrder(contract,"SELL",bn_ltp)
            print("Stop Loss hit at: "+ str(bn_ltp)+". Exit Time is "+ str(run_time)+".")
            print("Net Loss: "+str(abs(entry_price-exit_price))+" points.")
            break
    if(who_triggered == "SELL"):
        if(bn_ltp<target):
            PlaceOrder(contract,"BUY",bn_ltp)
            print("Target hit at: "+ str(bn_ltp)+". Exit Time is "+ str(run_time)+".")
            print("Net Profit: "+str(abs(entry_price-exit_price))+" points.")
            break
        if(bn_ltp>stop_loss):
            PlaceOrder(contract,"BUY",bn_ltp)
            print("Stop Loss hit at: "+ str(bn_ltp)+". Exit Time is "+ str(run_time)+".")
            print("Net Loss: "+str(abs(entry_price-exit_price))+" points.")
            break
        time.sleep(10)
