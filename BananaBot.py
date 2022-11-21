import logging
import pandas as pd
import logging

pd.options.mode.chained_assignment = None

import api_wrapper
import helpers

class BananaRSIBOL():
    '''
    main bot class
    '''

    def __init__(self,  client,ticker='BTCUSDT', sl_percent=0.01, amount=1,
                 interval="1m", precious=6, DEBUG=False, LOCAL_TEST=False):
        '''DEBUG and DEBUG_CANDLES uses for local only test without api calls'''
        self.ticker=ticker
        self.client=client
        self.interval=interval
        self.position=0
        self.data=None
        self.amount=amount
        self.sl_percent=sl_percent;        
        self.sl_price=None
        self.DEBUG=DEBUG
        self.LOCAL_TEST=LOCAL_TEST
        self.precious=precious

        self.order=None
        self.sl_order=None
        if self.DEBUG:
            self.l=logging.getLogger(ticker) 
            self.l.setLevel(logging.INFO) 
            self.l.info("created bot for "+ self.ticker + ", with tf " + self.interval +", and amouunt: "+ str(self.amount))

        self.lst_candle_time=None
        self.d_enterTime=None
        self.d_enterPrice=None
        self.d_enterRSI=None
        self.d_direction=None
        self.d_tp=0
        self.d_sl=0

    def update(self,data=None, P=14, order=5, K=2):
        if self.LOCAL_TEST==False:
            #retrieve candles
            data= api_wrapper.get_klines(self.client,self.ticker, self.interval)
            #if self.DEBUG:
            #    self.l.info(': candle data:' + str(len(data))+' candles updated' )

            data = helpers.getPeaks(data, key='Close', order=order, K=K)
            data = helpers.calcRSI(data, P=P)
            data = helpers.getPeaks(data, key='RSI', order=order, K=K)
            data = helpers.bollinger_bands(data, trend_periods=20, close_col='Close')

            #if self.DEBUG:
            #    self.l.info(' : peaks and rsa with bolbands candles updated' )

        self.data=data

        if self.position==0:
            self.position=self.checkForEnter()
        else:
            position=self.checkForClose()
        #tp checks
            if position==1 and self.position==1:
                self.position=0
                self.sl_price=0
            elif position==-1 and self.position==-1:
                self.position=0
                self.sl_price=0
        #sl check
            close=self.checkForSL()

            if not close == 0:
                self.position=0
                self.sl_order=None
                self.sl_price=0



    def checkForEnter(self):
        position=0
        row= self.data.tail(1)

        #print(row)
        #print(row['Close_lows'].iloc[0])
        
        if row['Close_lows'].iloc[0] == -1 and row['RSI_lows'].iloc[0] == 1: # Buy if indicator to higher low and price to lower low
            if row['RSI'].iloc[0] < 50:
                position=1
                slp=float(round(
                    float(row['Close'].iloc[0]) -
                    float(row['Close'].iloc[0] * self.sl_percent),
                     self.precious))
                self.sl_price=slp
                if not self.LOCAL_TEST:
                    self.order= api_wrapper.buy_market(self.client, symbol=self.ticker, amount=self.amount)
                    
                    if self.DEBUG:
                        self.l.info(': created order to buy: '+str(self.order))
                        self.l.info(': creating sl order for ' +self.ticker +', on price: '+  str(self.sl_price))
                    self.sl_order=api_wrapper.sell_limit(self.client, symbol=self.ticker, amount=self.amount, price=self.sl_price)

                    if self.DEBUG:
                        self.l.info(': created sl order: '+str(self.sl_order))
                    
        elif row['Close_highs'].iloc[0]  == 1 and row['RSI_highs'].iloc[0] == -1: # Short if price to higher high and indicator to lower high
            if row['RSI'].iloc[0] > 50:
                position = -1
                slp=float(round(
                    float(row['Close'].iloc[0])+
                    float(row['Close'].iloc[0] * self.sl_percent),
                    self.precious))
                #print("SLP" + str(slp))
                self.sl_price=slp

                if not self.LOCAL_TEST:
                    self.order=api_wrapper.sell_market(self.client, symbol=self.ticker, amount=self.amount)
                    
                    if self.DEBUG:
                        self.l.info(': created order to sell: '+str(self.order))
                        self.l.info(': creating sl order for ' +self.ticker +', on price: '+  str(self.sl_price))
                    self.sl_order=api_wrapper.buy_limit(self.client, symbol=self.ticker, amount=self.amount, price=self.sl_price)

                    if self.DEBUG:
                        self.l.info(': created sl order: '+str(self.sl_order))

        if not position ==0 and self.DEBUG:
            self.d_enterTime=row['Time'].iloc[0]
            self.d_enterPrice=row['Close'].iloc[0]
            self.d_enterRSI=row['RSI'].iloc[0]
            self.d_direction=position

        return position


    def checkForClose(self):
        position=0
        #check for last N lines
        row= self.data.tail(1) 
        #mydata=self.data[self.data['Time'>=self.lst_candle_time]]
        #for i, row in mydata.iterrows():


        if self.position==1 and row['High'].iloc[0] > row['Upper'].iloc[0]:#sell
            position=1
            #print('profit')
            if not self.LOCAL_TEST:
                result= api_wrapper.cancel_open_orders(self.client, symbol=self.ticker)
                if self.DEBUG:
                    self.l.info(": sl canceled" + str(result))

        elif self.position==-1 and row['Low'].iloc[0] < row['Lower'].iloc[0]:#buy
            position=-1 
            #print('profit')
            if not self.LOCAL_TEST:
                result = api_wrapper.cancel_open_orders(self.client, symbol=self.ticker)
                if self.DEBUG:
                    self.l.info(": sl canceled" + str(result))

        if self.DEBUG and not position ==0:
            exitTime=row['Time'].iloc[0]
            exitPrice=row['Close'].iloc[0]
            exitBolUp=row['Upper'].iloc[0]
            exitBolDown=row['Lower'].iloc[0]

            enterTime=self.d_enterTime
            enterPrice=self.d_enterPrice
            enterRSI=self.d_enterRSI
            enterDirection=self.d_direction

            self.d_tp=abs(enterPrice - exitPrice) * self.amount
            self.l.info('TP >> '+ str(round(abs(enterPrice - exitPrice) * self.amount)) +'\t enter: '+str(enterTime)+', enterPRice: ' +str(enterPrice)+', enterRsi: '+str(enterRSI)+', direction: '+str(enterDirection)+', exitTime: ' + str(exitTime)+', exitPrice: '+str(exitPrice)+', exitBolUp:'+str(exitBolUp) + ', exitBolDown: '+str(exitBolDown))

            self.d_enterTime=None
            self.d_enterPrice=None
            self.d_enterRSI=None
            self.d_direction=None
        #self.sl_price=None

        return position
    
    def checkForSL(self):
        #check for last N lines
        row= self.data.tail(1)
        close=0
        if self.position==1 and row['Low'].iloc[0] < self.sl_price:
            close=-1   
        elif self.position==-1 and row['High'].iloc[0] > self.sl_price:
            close=1

        if self.DEBUG and not close ==0:
            exitTime=row['Time'].iloc[0]
            exitPrice=row['Close'].iloc[0]
            enterTime=self.d_enterTime
            enterPrice=self.d_enterPrice
            enterRSI=self.d_enterRSI
            enterDirection=self.d_direction

            self.d_sl=abs(enterPrice - exitPrice) * self.amount
            self.l.info('SL >> '+ str(round(abs(enterPrice - exitPrice)* self.amount)) +'\t enter: '+str(enterTime)+', enterPRice: ' +str(enterPrice)+', enterRsi: '+str(enterRSI)+', direction: '+str(enterDirection)+', exitTime: ' + str(exitTime)+', exitPrice: '+str(exitPrice))#+', exitBolUp:'+str(exitBolUp) + ', exitBolDown: '+str(exitBolDdown))
            
            self.d_enterTime=None
            self.d_enterPrice=None
            self.d_enterRSI=None
            self.d_direction=None
            
        return close