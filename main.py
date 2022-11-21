from http import client
from binance.um_futures import UMFutures
from binance.error import ClientError
import logging
from binance.lib.utils import config_logging
import logging
import time
import json

from BananaBot import BananaRSIBOL
from api_wrapper import cancel_open_orders, change_leverge, change_position_mode, get_position_mode,buy_limit, buy_market,sell_limit,sell_market

TICKERS=[]
AMOUNTS=[]
SL_PERCENTS=[]
LEVERAGES=[]
TIMEFRAMES=[]
PRECIOUSES=[]
KEY=''
SECRET=''

cdata=None
with open("config.json") as file:
    cdata=json.load(file)
    KEY=cdata['key']
    SECRET=cdata['sec']
    
    ticks=cdata["tickers"]
    
    for i in range(0,len(ticks)):
        e=ticks[i]
        TICKERS.append(e['ticker'])
        PRECIOUSES.append(e['precious'])
        AMOUNTS.append(float(e['amount']))
        SL_PERCENTS.append(float(e['sl']))
        LEVERAGES.append(int(e['leverage']))
        TIMEFRAMES.append(e['tf'])
        print(str(e) + ' loaded')

print('config.json loaded')


config_logging(logging, logging.INFO)
client =  UMFutures(key=KEY,secret=SECRET)

#print('buy test')
#buy_market(client=client, symbol='ETCUSDT',amount= float(AMOUNTS[0]))

#print('sell test')
#sell_limit(client=client, symbol='ETCUSDT', amount= float(AMOUNTS[0]), price=38.1)

BOTS=[]

for i in range(len(TICKERS)):
    r=change_leverge(client, TICKERS[i], LEVERAGES[i])
    print("changed laverage for " + TICKERS[i] +' to: ' +str(LEVERAGES[i]) +" with result: "+str(r))
    r1= get_position_mode(client=client)
    print("current order position mode is " + str(r1))
    if not str(r1)=="{'dualSidePosition': True}":
        r2=change_position_mode(client=client)
        print("changed position to dualsided for " + TICKERS[i] + " with result: "+str(r2))

    b=BananaRSIBOL(client, ticker=TICKERS[i],
                   sl_percent=SL_PERCENTS[i],
                   interval="1m",
                   amount=AMOUNTS[i],
                   precious=PRECIOUSES[i],
                   DEBUG=True,
                   LOCAL_TEST=False)
    BOTS.append(b)

try:
    while True:
        for b in BOTS:
            b.update()
            time.sleep(0.999)
except Exception as e:
    print("Cancel all orders")
    for i in TICKERS:
        cancel_open_orders(client,i)
    raise(e)