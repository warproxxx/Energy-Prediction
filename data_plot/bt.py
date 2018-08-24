import numpy as np
import pandas as pd
import datetime  # For datetime objects
import time
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
from backtrader.feeds import PandasData

class PandasData_Signal(PandasData):
    lines = ('Predicted',)
    params = (('Predicted', 5), )

# Create a Stratey
class TestStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries

        self.datasignal = self.datas[0].Predicted
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.cashrecord = pd.DataFrame(['Date', 'Value'])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
        
    def get_cash_record(self):
        try:
            self.cashrecord = self.cashrecord.drop(0, axis=1)
        except:
            pass
        
        return self.cashrecord

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.datasignal[0])
        self.cashrecord = self.cashrecord.append({'Date': self.datas[0].datetime.datetime(0) , 'Value': self.broker.get_cash()}, ignore_index=True)

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        
        try:
            # Check if we are in the market
            if not self.position:

                # Not yet ... we MIGHT BUY if ...
                if self.datasignal[1] > self.datasignal[0]:
                    # BUY, BUY, BUY!!! (with default parameters)
                    self.log('BUY CREATE, %.2f' % self.datasignal[0])

                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()

            else:
                # Already in the market ... we might sell
                if self.datasignal[1] < self.datasignal[0]:
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                    self.log('SELL CREATE, %.2f' % self.datasignal[0])
                    print(self.log('Current Cash {}'.format(self.broker.get_cash())))
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.sell()
        except:
            pass

def execute_backtesting(location):
	file= location + '.csv'
	df = pd.read_csv('temp_data/HB_HOUSTON.csv',  encoding='utf-8')[:1000]
	df = df.drop('Unnamed: 0', axis=1)
	np.random.seed(1)
	df['Date'] = [int(time.mktime(datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').timetuple())) for x in df['Date']] 
	df['Datetime'] = [datetime.datetime.fromtimestamp(x) for x in df['Date']]
	df = df.drop('Date', axis=1)
	df['Signal'] = np.random.rand(df.shape[0])
	df['Open'] = df['SettlementPointPrice']
	df['High'] = df['SettlementPointPrice']
	df['Low'] = df['SettlementPointPrice']
	df['Close'] = df['SettlementPointPrice']
	df['Predicted'] = ((df['Predicted'] - df['Open'])/df['Open']) * 100
	df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Predicted']]
    
	data = PandasData_Signal(dataname=df, datetime=0 ,open=1, high=2, low=3, close=4, Predicted=5)
    # Create a cerebro entity
	cerebro = bt.Cerebro()

    # Add a strategy
	cerebro.addstrategy(TestStrategy)


    # Add the Data Feed to Cerebro
	cerebro.adddata(data)

    # Set our desired cash start
	cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
	cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission - 0.1% ... divide by 100 to remove the %
	cerebro.broker.setcommission(commission=0.001)
	# Print out the starting conditions
	print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
	# Run over everything
	rr = cerebro.run()
	# Print out the final result
	print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
	bt_data = rr[0].get_cash_record()
	df = pd.DataFrame(data=bt_data)
	df = df.fillna(method='bfill')
	df['Date'] = df['Date'].astype(str)
	
	return df