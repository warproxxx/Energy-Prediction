from glob import glob
import os
import pandas as pd
from basic_utils import get_logger, get_location

class cleaner:
    def __init__(self, logger=None):
        if logger == None:
            self.logger = get_logger(get_location() + "/logs/cleaner.log")
        else:
            self.logger = logger

        self.historicLocations = []
        self.liveLocations = []

        self.historicFolder = 'data/downloading/historic'
        self.liveFolder = 'data/downloading/live'

        for f in glob('{}/*'.format(self.historicFolder)):
            location = os.path.basename(f).replace('.csv', '')
            
            if (location != "nan"):
                self.historicLocations.append(location)

        for f in glob('{}/*'.format(self.liveFolder)):
            location = os.path.basename(f).replace('.csv', '')
            
            if (location != "nan"):
                self.liveLocations.append(location)

        self.locations = list(set(self.historicLocations).intersection(self.liveLocations))

    def fix_data(self, df):
        '''
        Convert DeliveryDate, DeliveryHour and DeliveryInterval column to pd.to_datetime. Also remove the DSTFlag and SettlementPointType column. 
        Also arranges in ascending order
        '''
        df['Date'] = pd.to_datetime(pd.to_datetime(df['DeliveryDate']) + (df['DeliveryHour']-1).astype('timedelta64[h]') + ((df['DeliveryInterval']) * 15).astype('timedelta64[m]'))
        df = df.drop(columns=['DeliveryDate', 'DeliveryHour', 'DeliveryInterval', 'DSTFlag', 'SettlementPointType', 'SettlementPointName'], axis=1)
        df = df.sort_values('Date').reset_index(drop=True)

        return df[['Date', 'SettlementPointPrice']]

    def fixJoin(self, live, historic):
        '''
        Drop Duplicates and fix missing timelines
        '''
        
        df = pd.concat([live, historic]).sort_values('Date')
        dupShape = df.shape[0]

        df = df.drop_duplicates('Date').reset_index(drop=True)
        duplicates = dupShape - df.shape[0]
        self.logger.info("Total Duplicates: {}".format(duplicates))
        
        totalMissing = sum((df['Date'].shift(-1)[:-1] - df['Date'][:-1]).astype('timedelta64[m]') != 15)
        
        self.logger.info("Total Missing Dates: {}".format(totalMissing))
        missingDates = list(df[:-1][(df['Date'].shift(-1)[:-1] - df['Date'][:-1]).astype('timedelta64[m]') != 15]['Date'])
        self.logger.info("The Missing dates are around: {}".format(missingDates))
        
        dates = pd.DataFrame(pd.date_range(df.iloc[0]['Date'],df.iloc[-1]['Date'],freq='15T'))
        dates.columns = ['Date']
        
        df.set_index('Date', inplace=True)
        dates.set_index('Date', inplace=True)
        
        full_data = pd.concat([df, dates], axis=1).fillna(method='ffill')
        full_data.index.name = 'Date'
        
        return full_data.reset_index()

    def clean(self):
        if (len(self.locations) > 2):
            for location in self.locations:
                historic = pd.read_csv('{}/{}.csv'.format(self.historicFolder, location))
                live = pd.read_csv('{}/{}.csv'.format(self.liveFolder, location))

                live = self.fix_data(live)
                historic = self.fix_data(historic)

                df = self.fixJoin(live, historic)

                df.to_csv('data/processed/{}/data.csv'.format(location), index=False, mode='a')
                self.logger.info("Saved to data/processed/{}/data.csv".format(location))
                
                os.remove('{}/{}.csv'.format(self.historicFolder, location))
                self.logger.info("{}/{}.csv removed".format(self.historicFolder, location))

                os.remove('{}/{}.csv'.format(self.liveFolder, location))
                self.logger.info("{}/{}.csv removed".format(self.liveFolder, location))
        else:
            for location in self.liveLocations:
                live = pd.read_csv('{}/{}.csv'.format(self.liveFolder, location))

                live = self.fix_data(live)
                
                live.to_csv('data/processed/{}/data.csv'.format(location), index=False, header=None, mode='a')
                self.logger.info("Appended to data/processed/{}/data.csv".format(location))

                os.remove('{}/{}.csv'.format(self.liveFolder, location))
                self.logger.info("{}/{}.csv removed".format(self.liveFolder, location))