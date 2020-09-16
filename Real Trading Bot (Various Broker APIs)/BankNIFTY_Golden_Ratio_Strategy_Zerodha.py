#Zerodha API
#Author: Darshan B

#The BankNIFTY Golden Ratio Strategy
##Scrip = BANKNIFTY Futures

## Golden Number = ((Previous Day High - Previous Day Low) + Opening Range of Today's First 10 minutes))*61.8%

### Buy Above = (Previous Day Close + Golden Number)
### Sell Below = (Previous Day Close - Goldern Number)

#### Stop Loss at 0.5% Target at 2%


from nsepython import * 
import pandas as pd
import datetime as dt
import numpy as np
from selenium import webdriver
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import logging
logging.basicConfig(level=logging.DEBUG)

who_triggered = "NONE"
qty = 25 ###enter in multiples of 25######

#################Initializing token############################
def initialize_token():
    global kite,kws
    driver = webdriver.Chrome('chromedriver.exe')
    api_key = '' 
    api_secret = ''
    kite = KiteConnect(api_key)
    print(kite.login_url())
    driver.get(kite.login_url())
    driver.implicitly_wait(50)
    username = driver.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[1]/input')
    password = driver.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[2]/input')
        
    username.send_keys("")
    password.send_keys("")
        
    driver.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[4]/button').click()
        
    driver.implicitly_wait(50)
    pin = driver.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[2]/div/input')
    pin.send_keys("")
    driver.implicitly_wait(50)
    driver.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[3]/button').click()
    time.sleep(5)
    
    code = driver.current_url
    code = re.split("[?=|&]",code)
    for i in range (0,len(code)):
        if code[i] == 'request_token':
            j = i+1
            code1 = code[j]
            
    data = kite.generate_session(code1, api_secret)
    kite.set_access_token(data["access_token"])
    kws = KiteTicker(api_key, data["access_token"])
    driver.close()

def tokenLookup(instrument_df,symbol_list):
    """Looks up instrument token for a given script from instrument dump"""
    token_list = []
    for symbol in symbol_list:
        token_list.append(int(instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]))
    return token_list

def on_ticks(ws,ticks):
    global who_triggered,qty
    for tick in ticks:
        ltp = tick['last_price']

        if (ltp > buy_above):
            print("Buy Order executed at: " +str(ltp)+". Entry Time is "+ str(run_time)+".")
            who_triggered = "BUY"
            stop_loss = round(ltp - ltp*(.995),1)
            target = round(ltp*(1.02)-ltp,1)
            kite_bo_order(ticker,"BUY",qty,ltp+2,stop_loss,target)
            
        if(ltp<sell_below):
            print("Sell Order executed at: " +str(ltp)+". Entry Time is "+ str(run_time)+".")
            who_triggered = "SELL"
            stop_loss = round(ltp*(1.005)-ltp,1)
            target = round(ltp - ltp*(.98),1)
            kite_bo_order(ticker,"SELL",qty,ltp+2,stop_loss,target)
            
        if(who_triggered != "NONE"):
            entry_price = run_time
            entry_price = ltp
            print("Stop Loss is: " + str(stop_loss)+".")
            print("Target is: " + str(target)+".")
            if ltp > stop_loss and who_triggered =="SELL":
                print("Stop Loss hit at: "+ str(bn_ltp)+". Exit Time is "+ str(run_time)+".")
                print("Net Loss: "+str(abs(entry_price-exit_price))+" points.")

            elif ltp < stop_loss and who_triggered =="BUY":
                print("Stop Loss hit at: "+ str(bn_ltp)+". Exit Time is "+ str(run_time)+".")
                print("Net Loss: "+str(abs(entry_price-exit_price))+" points.")

            elif ltp > target and who_triggered =="BUY":
                print("Target hit at: "+ str(bn_ltp)+". Exit Time is "+ str(run_time)+".")
                print("Net Profit: "+str(abs(entry_price-exit_price))+" points.")

            elif ltp < target and who_triggered =="SELL":
                print("Stop Loss hit at: "+ str(bn_ltp)+". Exit Time is "+ str(run_time)+".")
                print("Net Loss: "+str(abs(entry_price-exit_price))+" points.")    

def on_connect(ws,response):
    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_FULL,tokens)

def kite_bo_order(ticker,trans_type,qty,limit_price,sl,tgt):
    kite.place_order(tradingsymbol=instrument_id,
                             price=limit_price,
                             exchange="NSE",
                             transaction_type=trans_type,
                             quantity=qty,
                             squareoff=tgt,
                             stoploss=sl,
                             order_type="LIMIT",
                             validity = "DAY",
                             product="MIS", 
                             variety = "bo",
                             trailing_stoploss=None)  
    
#running initialization#########
initialize_token()


instrument_dump = kite.instruments()
instrument_df = pd.DataFrame(instrument_dump)

instrument_list = instrument_df.loc[(instrument_df["name"] == "BANKNIFTY") & (instrument_df["segment"] == "NFO-FUT")]
instrument_list.sort_values(by=['expiry'],inplace = True)
current_index = instrument_list.iloc[0]["tradingsymbol"]

banknifty_info = nse_quote_meta("BANKNIFTY","latest","Fut")
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


tickers = [current_index]
tokens = tokenLookup(instrument_df,tickers)
    
while True:
    now = datetime.datetime.now()
    if (now.hour >= 9 and now.minute >= 15 ):
        kws.on_ticks=on_ticks
        kws.on_connect=on_connect
        kws.connect()
    if (now.hour >= 15 and now.minute >= 30):
        sys.exit()
