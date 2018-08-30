import pandas as pd
import backtrader as bt
import numpy as np
import io
import csv
import datetime
import json
import os
from alpha_vantage.timeseries import TimeSeries


class PandasData_Custom(bt.feeds.PandasData):
    lines = ('predicted',)
    params = (
        ('datetime', 0),
        ('open', 1),
        ('high', None),
        ('low', None),
        ('close', 2),
        ('volume', None),
        ('predicted', 3),
    )

class tradeStrategy(bt.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.predicted = self.datas[0].predicted
        
        self.order=None
        self.buyprice=None
        self.buycomm=None
        
        self.trades = io.StringIO()
        self.trades_writer = csv.writer(self.trades)
        
        self.operations = io.StringIO()
        self.operations_writer = csv.writer(self.operations)
        
        self.portfolioValue = io.StringIO()
        self.portfolioValue_writer = csv.writer(self.portfolioValue)
        
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.datetime(0)
        print("Datetime: {} Message: {} Predicted: {}".format(dt, txt, self.dataclose[0]))
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                ordertype = "BUY"
                #self.log("BUY EXECUTED, Price: {}, Cost: {}, Comm: {}".format(order.executed.price, order.executed.value, order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                ordertype = "SELL"
                #self.log("SELL EXECUTED, Price: {}, Cost: {}, Comm: {}".format(order.executed.price, order.executed.value, order.executed.comm))

            self.trades_writer.writerow([self.datas[0].datetime.datetime(0), ordertype, order.executed.price, order.executed.value, order.executed.comm])
        
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            #self.log("Order Canceled/Margin/Rejected")
            self.trades_writer.writerow([self.datas[0].datetime.datetime(0) , 'Rejection', 0, 0, 0])
            
        self.order = None
    
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        
        self.log('OPERATION PROFIT, GROSS: {}, NET: {}'.format(trade.pnl, trade.pnlcomm))
        self.operations_writer.writerow([self.datas[0].datetime.datetime(0), trade.pnlcomm])
    
    def get_logs(self):
        '''
        Returns:
        ________
        portfolioValue (df):
        Date and Value of portfolio
        
        trades (df):
        'Date', 'Type', 'Price', 'Total Spent', 'Comission'
        
        operations (df):
        'Date', 'Profit'
        '''
        self.portfolioValue.seek(0)
        portfolioValueDf = pd.read_csv(self.portfolioValue, names=['Date', 'Value'])
        
        portfolioValueDf['Date'] = pd.to_datetime(portfolioValueDf['Date'])
        portfolioValueDf = portfolioValueDf.set_index('Date')
        portfolioValueDf = portfolioValueDf.resample('1D').agg({'Date': lambda x: x.iloc[0], 'Value': lambda x: x.iloc[-1]})['Date']
        
        self.trades.seek(0)
        tradesDf = pd.read_csv(self.trades, names=['Date', 'Type', 'Price', 'Total Spent', 'Comission'])
        
        self.operations.seek(0)
        operationsDf = pd.read_csv(self.operations, names=['Date', 'Profit'])
        
        return portfolioValueDf, tradesDf, operationsDf
    
    
    def next(self):
        #self.log('Close: {}'.format(self.dataclose[0]))
        self.portfolioValue_writer.writerow([self.datas[0].datetime.datetime(0), self.broker.get_cash()])
        
        if self.order:
            return
        
        if not self.position:
            if self.predicted[0] > self.dataclose[0]:
                self.log("BUY CREATE {}".format(self.dataclose[0]))
                self.order = self.buy()
        else:
            if self.predicted[0] < self.dataclose[0]:
                self.log("SELL CREATE {}".format(self.dataclose[0]))
                self.order = self.sell()

def sharpe_ratio(data):
    '''
    http://www.edge-fund.com/Lo02.pdf

    https://sixfigureinvesting.com/2013/09/daily-scaling-sharpe-sortino-excel/
    '''
    n = 365 ** 0.5 #365 trading days

    percentage = data.pct_change()[1:]
    sharpe = (np.average(percentage)/np.std(percentage)) * n
    return sharpe

def sortino_ratio(data):
    '''
    The ratio that only considers downside volatility
    '''
    n = 365 ** 0.5 #365 trading days
    df = pd.DataFrame(columns=['Portfolio', 'Percentage Change'])
    df['Portfolio'] = data
    df['Percentage Change'] = data.pct_change()
    df = df.fillna(method='bfill')
    negatives = df[df['Percentage Change'] < 0]['Percentage Change']
    sortino = (np.average(df['Percentage Change'])/np.std(negatives)) * n
    return sortino

def drawDown(down):
    '''
    Returns maximum draw down in terms of percentage
    '''

    minimum = ((np.amin(down) - down[0])/down[0]) * 100
    return minimum

def portfolio_return(data):
    return (data[-1] - data[0])/data[0]

def my_agg(x, column):
    names = {
        'Time': x.index[0].to_pydatetime().strftime("%B %Y"),
        'Return': (x[column].iloc[-1] - x[column].iloc[0])/x[column].iloc[0],
        'Drawdown': ((np.amin(x[column]) - x[column].iloc[0])/x[column].iloc[0])}

    return pd.Series(names, index=['Time', 'Return', 'Drawdown'])

def process_data(df, portfolioValue, trades, operations):
    '''
    Process and returns the data in an appropriate format

    Parameters:
    ___________
    df (Dataframe):
    15 minute data containing 'Date', 'Open', 'Close', 'Predicted' 

    portfolioValue (Dataframe):
    Currently contains ['Date', 'Value']

    trades (Dataframe):
    Currently Contains ['Date', 'Type', 'Price', 'Total Spent', 'Comission']

    operations (Dataframe):
    Currently Contains ['Date', 'Profit']

    Returns:
    ________
    portfolioValue, trade_data, strategy_metrics, benchmark_metrics, strategyMovementDetails, benchmarkMovementDetails
    '''

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')

    trades = trades.set_index('Date')
    operations = operations.set_index('Date')

    portfolioValue = pd.to_datetime(portfolioValue['Date'])
    portfolioValue = portfolioValue.set_index('Date')

    #Creating trade_data

    df['Buy'] = trades[trades['Type'] == 'BUY']['Price']
    df['Sell'] = trades[trades['Type'] == 'SELL']['Price']

    df['p/l'] = operations['Profit']
    df['p/l'] = df['p/l'].replace(np.nan, 0)

    df['Buy'] = df['Buy'].replace(np.nan, '')
    df['Sell'] = df['Sell'].replace(np.nan, '')

    trade_data = df[['Close', 'Buy', 'Sell', 'p/l']]
    trade_data.rename(columns={'Close': 'SettlementPointPrice'})

    #Created trade_data

    #Creating portfolioValue

    ts = TimeSeries(key='9CFF0BJ1ZPRQYEO0',output_format='pandas')
    data, meta_data = ts.get_daily_adjusted('^GSPC')
    spNew = data.reset_index()[['date', '5. adjusted close']].rename(columns={'date': 'Date', '5. adjusted close': 'Adj Close'})
    spOld = pd.read_csv('S&P.csv')[['Date', 'Adj Close']]
    spy = pd.concat([spOld, spNew[spNew['Date'] > spOld.iloc[-1]['Date']]]).reset_index(drop=True)

    spy['Date'] = pd.to_datetime(spy['Date'])
    spy = spy.set_index('Date')

    portfolioValue['s&p'] = spy['Adj Close']
    portfolioValue = portfolioValue.fillna(method='ffill')
    portfolioValue['s&pValue'] = (portfolioValue['Value'].iloc[0] / portfolioValue['s&p'].iloc[0]) * portfolioValue['s&p']
    portfolioValue = portfolioValue.drop('s&p', axis=1)

    #Created portfolioValue

    #Creating metrics
    sharpe = sharpe_ratio(portfolioValue['s&pValue'])
    sortino = sortino_ratio(portfolioValue['s&pValue'])
    drawdown = drawDown(portfolioValue['s&pValue'])
    portfolioReturn = portfolio_return(portfolioValue['s&pValue']) * 100

    backtestMetrics = {'Total Return:': str(portfolioReturn) + " %", 'Sharpe Ratio': sharpe, 'Sortino Ratio': sortino, 'Maximum Drawdown': drawdown}
    benchmark_metrics = json.dumps(backtestMetrics)

    sharpe = sharpe_ratio(portfolioValue['Value'])
    sortino = sortino_ratio(portfolioValue['Value'])
    drawdown = drawDown(portfolioValue['Value'])
    portfolioReturn = portfolio_return(portfolioValue['Value']) * 100

    strategyMetrics = {'Total Return:': str(portfolioReturn) + " %", 'Sharpe Ratio': sharpe, 'Sortino Ratio': sortino, 'Maximum Drawdown': drawdown}
    strategy_metrics = json.dumps(strategyMetrics)
    #Created Metrics

    #Creating monthly metrics
    strategyMovementDetails = portfolioValue.resample('1M').apply(my_agg, column='Value').reset_index(drop=True)
    benchmarkMovementDetails = portfolioValue.resample('1M').apply(my_agg, column='s&pValue').reset_index(drop=True)
    #Created montly metrics

    return portfolioValue, trade_data, strategy_metrics, benchmark_metrics, strategyMovementDetails, benchmarkMovementDetails

def perform_backtest(cityname, model_name, test_type, starting_cash, comission, strategy):
    '''
    Perform backtest or loads backtest data from the cache. Although the name is perform_backtest
    this can perform both forwardtest and backtest

    Parameters:
    ___________
    cityname (string):
    The name of the city

    model_name (string):
    The name of the model

    test_type (string):
    forwardtest or backtest

    starting_cash (int):
    The cash amount to start

    comission (float):
    Comission amount in percentage

    strategy (string):
    The strategy to use. Currently the possible values are s1 and s2. s1 refers to Normal and s2 refers to Agressive strategy

    Returns:
    ________
    portfolioValue (df):
    Pandas dataframe containing daily value of portfolio and buying and holding s&p500. Columns are Date, Value and s&pValue

    trade_data (df):
    Pandas dataframe containing details all dates, SettlementPointPrice, Buy, Sell and p/l. Buy column contains Buy price and Sell contains Sell price

    strategy_metrics (dictionary):
    Dictionary containing metrics of using this strategy. Currently the values are Return, Sharpe Ratio, Sortino Ratio and Maximum drawdown
    
    benchmark_metrics (dictionary):
    Dictionary containing metrics of buying and holding S&P 500 to compare. Same column as above

    strategyMovementDetails (df):
    Dataframe containing montly returns and drawdown if traded using the strategy

    benchmarkMovementDetails (df):
    Dataframe containing montly returns and drawdown if s&p 500 is held
    '''

    current_rootDir = "algorithm/models/{}/{}/{}".format(model_name, cityname, test_type)
    strategyName = "{}_{}_{}".format(strategy, starting_cash, comission)
    strategyDir = os.path.join(current_rootDir, strategyName)

    if (os.path.isdir(strategyDir)):
        with open('{}/strategyMetrics.json'.format(strategyDir)) as aa:
            strategy_metrics = json.load(aa)
        strategy_metrics = json.loads(strategy_metrics) 

        with open('{}/s&pMetrics.json'.format(strategyDir)) as aa:
            benchmark_metrics = json.load(aa)
        benchmark_metrics = json.loads(benchmark_metrics)

        portfolioValue = pd.read_csv('{}/PortfolioValue.csv'.format(strategyDir))
        trade_data = pd.read_csv('{}/trading_data.csv'.format(strategyDir))

        strategyMovementDetails = pd.read_csv('{}/strategyMovementDetails.csv'.format(strategyDir))
        benchmarkMovementDetails = pd.read_csv('{}/benchmarkMovementDetails.csv'.format(strategyDir))
    else:
        print("Performing backtest. This is gonna take a while")

        df = pd.read_csv('{}/predicted.csv'.format(current_rootDir))
        df['Open'] = df['SettlementPointPrice'].shift(1)
        df['Close'] = df['SettlementPointPrice']
        df['Date'] = pd.to_datetime(df['Date']).dt.to_pydatetime()
        df = df[['Date', 'Open', 'Close', 'Predicted']]

        data = PandasData_Custom(dataname=df)

        cerebro = bt.Cerebro()

        cerebro.adddata(data)
        cerebro.addstrategy(tradeStrategy)

        if (strategy == "s1"):
            cerebro.addsizer(bt.sizers.SizerFix, stake=10)
        elif (strategy == "s2"):
            cerebro.addsizer(bt.sizers.SizerFix, stake=2)

        cerebro.broker.setcash(starting_cash)
        cerebro.broker.setcommission(comission/100)

        run = cerebro.run()
        portfolioValue, trades, operations = run[0].get_logs() #not using opeartions for now

        portfolioValue, trade_data, strategy_metrics, benchmark_metrics, strategyMovementDetails, benchmarkMovementDetails = process_data(df, portfolioValue, trades, operations)
        
        #create directory then save
        os.makedirs(strategyDir)

        portfolioValue.to_csv('{}/PortfolioValue.csv'.format(strategyDir))
        trade_data.to_csv('{}/trading_data.csv'.format(strategyDir))

        with open("strategyMetrics.json", 'w') as fp:
            json.dump(strategy_metrics, fp)
        
        with open("s&pMetrics.json", 'w') as fp:
            json.dump(benchmark_metrics, fp)

        strategyMovementDetails.to_csv('{}/strategyMovementDetails.csv'.format(strategyDir))
        benchmarkMovementDetails.to_csv('{}/benchmarkMovementDetails.csv'.format(strategyDir))


    return portfolioValue, trade_data, strategy_metrics, benchmark_metrics, strategyMovementDetails, benchmarkMovementDetails