from binance.error import ClientError
from binance.um_futures import UMFutures
import logging
import pandas as pd
import logging

pd.options.mode.chained_assignment = None

'''
binnce futures api wrapper
'''

def get_klines(client,symbol='BTCUSD', interval='1m'):
    klines=client.klines(symbol, interval)
    t=[]
    for i in klines:
        time=int(i[0])/1000
        copen=float(i[1])
        high=float(i[2])
        low=float(i[3])
        close=float(i[4])
        vol=float(i[5])
        t.append([time,copen,high,low,close,vol])

    d=pd.DataFrame(t, columns=['Time','Open','High','Low','Close','Vol'])
    d['Time'] = pd.to_datetime(d['Time'],unit='s')
    d.drop(['Open', 'Vol'], axis=1, inplace=True)
    return d

def change_position_mode(client):
    try:
        response = client.change_position_mode(
            dualSidePosition="true"
        )
        logging.info(response)
        return response
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return None

def  get_position_mode(client):
    try:
        response = client. get_position_mode()
        logging.info(response)
        return response
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return None

def change_leverge(client, symbol='BTCUSDT', leverage=2):
    try:
        response = client.change_leverage(symbol=symbol, leverage=leverage)
        logging.info(response)
        return response
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message))
        return None
      
def sell_market(client, symbol='BTC_USDT', amount=0.0001): 
    '''sell by market'''
    try:
        response = client.new_order_test(
            symbol=symbol,
            side="SELL",
            type="MARKET",
            quantity=amount,
            positionSide="SHORT"
        )
        logging.info(response)
        
        return response
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message))
        return None
    
#for sl only
def buy_market(client, symbol='BTC_USDT', amount=0.0001):
    '''buy by market'''
    try:
        response = client.new_order_test(
            symbol=symbol,
            side="BUY",
            type="MARKET",
            positionSide="LONG",
            quantity=amount,
        )
        logging.info(response)
        
        return response
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message))
        return None
#for sl only 
def sell_limit(client, symbol="BTC_USDT", amount=0.00001, price=10000000.0):
    '''sell by limit'''
    try:
        response = client.new_order_test(
            symbol=symbol,
            side="SELL",
            type="LIMIT",
            quantity=amount,
            timeInForce="GTC",
            positionSide="LONG",
            price=price
#            stopPrice=price
        )
        logging.info(response)
        
        return response
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message))
        return None 
    
def buy_limit(client, symbol="BTC_USDT", amount=0.00001, price=1.0):
    '''buy by limit'''
    try:
        response = client.new_order_test(
            symbol=symbol,
            side="BUY",
            type="LIMIT",
            quantity=amount,
            timeInForce="GTC",
            positionSide="SHORT",
            price=price
#            stopPrice=price
        )
        logging.info(response)
        
        return response
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message))
        return None   
    

      
def get_balance(client):
    try:
        response = client.balance()
        logging.info(response)
        return response
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
            error.status_code, error.error_code, error.error_message))
        return None
            
def cancel_order(client, orderid):
    try:
        response = client.cancel_order(
        symbol="BTCUSD_PERP", orderId=123456
        )
        logging.info(response)
        return response
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message))
        return None
            
def cancel_open_orders(client, symbol="BTCUSD_PERP"):
    try:
        response = client.cancel_open_orders(symbol="BTCUSD_PERP")
        logging.info(response)
        return response
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
            error.status_code, error.error_code, error.error_message))
        return None
            

