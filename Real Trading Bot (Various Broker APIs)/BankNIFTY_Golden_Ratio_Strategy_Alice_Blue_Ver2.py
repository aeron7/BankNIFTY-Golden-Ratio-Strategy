#Alice Blue API V2
#Author: Rishav Raj

#The BankNIFTY Golden Ratio Strategy
##Scrip = BANKNIFTY Futures

## Golden Number = ((Previous Day High - Previous Day Low) + Opening Range of Today's First 10 minutes))*61.8%

### Buy Above = (Previous Day Close + Golden Number)
### Sell Below = (Previous Day Close - Goldern Number)

#### Stop Loss at 0.5% Target at 2%

from nsepython import *
from alice_blue import *
from datetime import datetime
​
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
​
​
#Get the Previous Day OHLC data
#Define a funciton to get the golden number and buyabove sell below data
def goldennumber():
    global buy_above #define as global valriables
    global sell_below 
​
    bn_info=nse_quote_meta("BANKNIFTY","latest","Fut")
    expiry_date = bn_info['expiryDate']
    historical_data = nsefetch('https://www.nseindia.com/api/historical/fo/derivatives?&expiryDate='+str(expiry_date)+'&instrumentType=FUTIDX&symbol=BANKNIFTY')
    historical_data = historical_data['data']
    historical_data = pd.DataFrame(historical_data)
​
    previous_day_high = historical_data['FH_TRADE_HIGH_PRICE'].iloc[0]
    previous_day_low = historical_data['FH_TRADE_LOW_PRICE'].iloc[0]
    previous_day_close = historical_data['FH_PREV_CLS'].iloc[0]
​
    range_high = bn_info['highPrice']
    range_low = bn_info['lowPrice']
    opening_range = float(range_high) - float(range_low)
​
    #Calculate the Golden Number
    golden_number = ((float(previous_day_high) - float(previous_day_low)) + opening_range) * .618
​
    #Get the trade entry values
    buy_above = int((float(previous_day_close) + golden_number))
    sell_below = int((float(previous_day_close) - golden_number))
​
​
#get token
#access_token =  AliceBlue.login_and_get_access_token(username="", password="", twoFA="",  api_secret="")
username = ''
password = ''
twoFA=''
​
client_id = ''
client_secret = ''
redirect_url= ''
​
access_token = AliceBlue.login_and_get_access_token(username=username, password=password, twoFA=twoFA,  api_secret=client_secret, redirect_url=redirect_url, app_id=client_id)
​
alice = AliceBlue(username=username, password=password, access_token=access_token, master_contracts_to_download=['NSE', 'BSE', 'MCX', 'NFO'])
​
#login to get master contracts to get the script info from AliceBlue
​
#get expiry date
bn_info = nse_quote_meta('BANKNIFTY','latest','Fut')
bn_expiry= datetime.strptime(bn_info['expiryDate'], "%d-%b-%Y").date()
​
#get instrument data from Alice
#for BankNifty
bn_Fut = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date=bn_expiry, is_fut=True, strike=None, is_CE = False)
​
​
#initializing bn_ltp & socket_opened
bn_ltp = bn_ltp = nse_quote_ltp("BANKNIFTY","latest","Fut")
socket_opened = False 
​
#Functions for getting data from Alice Blue
​
def open_callback():
    global socket_opened
    socket_opened = True
​
def quote_update(message):
    global bn_ltp
    bn_ltp = message['ltp']
​
def  socket_error(error):
    print(error)
​
#Start Execution
​
goldennumber()
print("Buy Above:" + str(buy_above))
print('Sell Below:' + str(sell_below))
​
​
#initialize bn data from Alice
alice.start_websocket(subscribe_callback=quote_update,
                        socket_open_callback=open_callback,
                        socket_error_callback = socket_error,
                        run_in_background=True)
while(socket_opened==False):    
    pass
alice.subscribe(bn_Fut, LiveFeedType.COMPACT)
​
#Trade Executions 
​
while True: 
​
    print("Current Value of BankNIFTY : " + str(bn_ltp))
    who_triggered = "NONE"
​
    if(bn_ltp>buy_above):
        print("Buy Order executed at: " + str(bn_ltp) + " Entry Time :"+ str(run_time))
        who_triggered = "BUY"
        stop_loss = bn_ltp*(.995)
        target = bn_ltp*(1.02)
​
        #Place order on Alice
        alice.place_order(transaction_type=TransactionType.Buy,
                        instrument=bn_Fut,
                        quantity = 25,  # 1 lot or should i use 25 here as 1 lot = 25 units?
                        order_type=OrderType.Limit,
                        product_type=ProductType.Intraday,
                        price=bn_ltp,
                        trigger_price=None,
                        stop_loss=stop_loss,
                        square_off=target,
                        trailing_sl=None,
                        is_amo=False)
​
    elif(bn_ltp<sell_below):
        print("Sell Order executed at: " + str(bn_ltp)+ " Entry Time :"+ str(run_time))
        who_triggered = "SELL"
        stop_loss = bn_ltp*(1.005)
        target = bn_ltp*(.98)
​
        #Place order on Alice
        #We are placing a Limit order with Target & stop loss 
        alice.place_order(transaction_type=TransactionType.Buy,
                        instrument=bn_Fut,
                        quantity = 25,  # 1 lot or should i use 25 here as 1 lot = 25 units?
                        order_type=OrderType.Limit,
                        product_type=ProductType.Intraday,
                        price=bn_ltp,
                        trigger_price=None,
                        stop_loss=stop_loss,
                        square_off=target,
                        trailing_sl=None,
                        is_amo=False)
​
    if(who_triggered != "NONE"):
        entry_time = run_time
        entry_price = bn_ltp
        print("Stop Loss : " + str(stop_loss))
        print("Target : " + str(target))
        break
    
    time.sleep(10)
​
# Trade Management
​
while True:
    print("Current Value of BankNIFTY: " + str(bn_ltp))
    exit_time = run_time
    exit_price = bn_ltp
    if(who_triggered == "BUY"):
        if(bn_ltp>target):
            print("Target hit at: "+ str(bn_ltp)+"Exit Time : "+ str(run_time))
            print("Net Profit: "+str(abs(entry_price-exit_price)))
            break
        if(bn_ltp<stop_loss):
            print("Stop Loss hit at: "+ str(bn_ltp)+"Exit Time : "+ str(run_time))
            print("Net Loss: "+str(abs(entry_price-exit_price)))
            break
    elif(who_triggered == "SELL"):
        if(bn_ltp<target):
            print("Target hit at: "+ str(bn_ltp)+"Exit Time : "+ str(run_time))
            print("Net Profit: "+str(abs(entry_price-exit_price)))
            break
​
        if(bn_ltp>stop_loss):
            print("Stop Loss hit at: "+ str(bn_ltp)+"Exit Time : "+ str(run_time))
            print("Net Loss: "+str(abs(entry_price-exit_price)))
            break