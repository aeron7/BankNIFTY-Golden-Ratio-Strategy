#!/usr/bin/env python
# coding: utf-8

from nsepython import * 

#The BankNIFTY Golden Ratio Strategy
##Scrip = BANKNIFTY Futures

## Golden Number = ((Previous Day High - Previous Day Low) + Opening Range of Today's First 10 minutes))*61.8%

### Buy Above = (Previous Day Close + Golden Number)
### Sell Below = (Previous Day Close - Goldern Number)

#### Stop Loss at 0.5% Target at 2%


#Getting All the Necessary Variables

banknifty_info=nse_quote_meta("BANKNIFTY","latest","Fut")

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

#Entering the Trade

while True: 
    
    bn_ltp = nse_quote_ltp("BANKNIFTY","latest","Fut")
    print("Current Value of BankNIFTY: " + str(bn_ltp))
    
    who_triggered = "NONE"
    
    #Amit's Test
    ##bn_ltp = 21949
    
    if(bn_ltp>buy_above):
        print("Buy Order executed at: " +str(bn_ltp)+". Entry Time is "+ str(run_time)+".")
        who_triggered = "BUY"
        stop_loss = bn_ltp*(.995)
        target = bn_ltp*(1.02)
    
    if(bn_ltp<sell_below):
        print("Sell Order executed at: " +str(bn_ltp)+". Entry Time is "+ str(run_time)+".")
        who_triggered = "SELL"
        stop_loss = bn_ltp*(1.005)
        target = bn_ltp*(.98)
    
    if(who_triggered != "NONE"):
        entry_time = run_time
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
            print("Target hit at: "+ str(bn_ltp)+". Exit Time is "+ str(run_time)+".")
            print("Net Profit: "+str(abs(entry_price-exit_price))+" points.")
            break
            
        if(bn_ltp<stop_loss):
            print("Stop Loss hit at: "+ str(bn_ltp)+". Exit Time is "+ str(run_time)+".")
            print("Net Loss: "+str(abs(entry_price-exit_price))+" points.")
            break
    
    if(who_triggered == "SELL"):
        
        if(bn_ltp<target):
            print("Target hit at: "+ str(bn_ltp)+". Exit Time is "+ str(run_time)+".")
            print("Net Profit: "+str(abs(entry_price-exit_price))+" points.")
            break
            
        if(bn_ltp>stop_loss):
            print("Stop Loss hit at: "+ str(bn_ltp)+". Exit Time is "+ str(run_time)+".")
            print("Net Loss: "+str(abs(entry_price-exit_price))+" points.")
            break
        
        time.sleep(10)
    
