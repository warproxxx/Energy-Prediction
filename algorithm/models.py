import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from keras.layers import Input, LSTM, Dense, Activation, Dropout
from keras.models import Model, load_model

from basic_utils import get_logger, get_location

from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error

import logging

import json

def default(o):
    if isinstance(o, np.integer): return int(o)
    raise TypeError

class tri_model_15_minute():
    def __init__(self):
        self.sequence_length = 24

    def get_data(self, df):
        data = df['SettlementPointPrice'].values
        data_out = []

        for i in range(len(data)-self.sequence_length+1):
            data_out.append(data[i:i+self.sequence_length])

        data = np.array(data_out)
        return data
    
    def get_XY(self, df):
        '''
        Returns X and Y in appropriate formate when df is sent to it 
        '''
        data = self.get_data(df)
        X = data[:, :-1]
        y = data[:, -1]
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        y = np.reshape(y, (y.shape[0], 1))
        return X, y

    def split_train_test(self, X, y, test_size=0.2):
        self.trainTestIndicator = np.zeros(X.shape[0])
        train_ind = int(round((1-test_size)*X.shape[0]))

        self.X_train = X[:train_ind,:, :]
        self.Y_train = y[:train_ind, :]
        
        self.trainTestIndicator[:train_ind] = 1

        self.X_test = X[train_ind:,:, :]
        self.Y_test = y[train_ind:,:]

        return self.X_train, self.Y_train, self.X_test, self.Y_test, self.trainTestIndicator
    
    def get_model(self, train_x, train_y, batch_size, epochs):
        inp = Input(shape=(None, 1))
        out = LSTM(50, return_sequences=True)(inp)
        out = Dropout(0.2)(out)
        out = LSTM(100, return_sequences=False)(out)
        out = Dropout(0.2)(out)
        out = Dense(1, activation='linear')(out)

        model = Model(inp, out)

        model.compile(loss="mse", optimizer="adam")
        
        model.fit(train_x, train_y, batch_size=batch_size, epochs=epochs, validation_split=0.05, verbose=2)
        
        return model

    def get_predictions(self, model, df, X, runtype):
        predicted = model.predict(X)

        df['Predicted'] = [None]*(df.shape[0]-len(predicted)) + list(predicted.reshape(-1))

        try:
            df['Indicator'] = [None]*(df.shape[0]-len(predicted)) + list(self.trainTestIndicator.reshape(-1))
        except:
            #it is forward test so all test
            df['Indicator'] = 0

        df['Direction'] = (df['Predicted'] > df['SettlementPointPrice']).astype(int)

        if (runtype == "forwardfill"):
            df = df[100:].reset_index(drop=True)

        actualDirection = (df['SettlementPointPrice'].shift(-1) > df['SettlementPointPrice']).astype(int)

        metrics = {}

        df = df.fillna(method='bfill')

        metrics['RMS Error'] = mean_squared_error(df['SettlementPointPrice'].shift(-1).fillna(method='ffill'),df['Predicted'])
        metrics['R2 Score'] = r2_score(df['SettlementPointPrice'].shift(-1).fillna(method='ffill'),df['Predicted'])

        metrics['Directional Accuracy'] = sum(df['Direction'] == actualDirection)/df['Direction'].shape[0]
        metrics['True Positive'] = np.sum(np.logical_and(df['Direction']==1, actualDirection==1))
        metrics['True Negative'] = np.sum(np.logical_and(df['Direction']==0, actualDirection==0))
        metrics['False Positive'] = np.sum(np.logical_and(df['Direction']==1, actualDirection==0))
        metrics['False Negative'] = np.sum(np.logical_and(df['Direction']==1, actualDirection==0))

        metrics['Precision'] = metrics['True Positive'] / (metrics['True Positive'] + metrics['False Positive'])
        metrics['Recall'] = metrics['True Positive'] / (metrics['True Positive'] + metrics['False Negative'])

        metrics['F1 Score'] = (2 * metrics['Precision'] * metrics['Recall']) / (metrics['Precision'] + metrics['Recall'])

        if (runtype == "forwardtest"):
            metrics['Current Prediction'] = df.iloc[-1]['Predicted']

        return df, metrics
        
class tri_model_1_hour(tri_model_15_minute): 
    def get_data(self, df):
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        df = df.resample('1H').agg({'Date': lambda x: x.iloc[0], 'SettlementPointPrice': lambda x: x.iloc[-1]})['Date']
        df = df.reset_index()

        data = df['SettlementPointPrice'].values
        data_out = []

        for i in range(len(data)-self.sequence_length+1):
            data_out.append(data[i:i+self.sequence_length])

        data = np.array(data_out)
        return data

class model_building(object):
    def __init__(self, model_name):
        '''
        Parameters:
        ___________
        model_name: Different types of model created. Currently supported
        tri_model_15_minute, tri_model_1_hours
        '''
        self.logger = get_logger(get_location() + '/logs/model.log')
        self.location = get_location()
        self.model_name = model_name

        if (self.model_name == 'tri_model_15_minute'):
            self.model = tri_model_15_minute()
        elif (self.model_name == 'tri_model_1_hours'):
            self.model = tri_model_1_hour()

    def get_XY(self, df):
        '''
        Modifies the df so it can be suitably used with the correct model and returns X and y

        Parameters:
        ___________
        df: (dataframe)
        The dataframe to process

        Returns:
        ________
        X (numpy): 
        X from the data that can be sent to keras

        y (numpy): 
        y from the data that can be sent to keras
        '''

        X, y = self.model.get_XY(df)
        return X, y

    def split_train_test(self, X, y, test_size=0.2):
        '''
        Parameters:
        ___________
        X (list or pandas or numpy):
        X in keras format to split it

        y (list or pandas or numpy):
        y in keras format to split it

        Returns:
        ________
        X_train, Y_train, X_test, Y_test, trainTestIndicator

        trainTestIndicator contains 1 and 0 where 1 indicates training and 0 indicates test
        '''
        X_train, Y_train, X_test, Y_test, trainTestIndicator = self.model.split_train_test(X, y, test_size)
        return X_train, Y_train, X_test, Y_test, trainTestIndicator

    def get_model(self, train_x, train_y, batch_size, epochs):
        '''
        Returns the appropriate model to perform calculations on.

        Parameters:
        __________
        train_x: (array)
        '''
        model = self.model.get_model(train_x, train_y, batch_size, epochs)
        return model
        
    def save_model(self, model, city):
        '''
        Saves the specified model in correct directroy.

        Parameters:
        ___________
        model (keras model):
        The model to save

        city (string):
        The name of city to save in
        '''
        saveIn = self.location + "/models/{}/{}/model.h5".format(self.model_name, city)

        try:
            if not os.path.exists(self.location + "/models/{}/{}".format(self.model_name, city)):
                os.makedirs(self.location + "/models/{}/{}".format(self.model_name, city))

            model.save(saveIn)
            self.logger.info("Model saved in {}".format(saveIn))
        except Exception as e:
            self.logger.info("Model Saving failed. Exception: {}".format(str(e)))
        
    def load_model(self, city):
        '''
        Loads the model

        Parameters:
        ___________
        The city whose model should be loaded for the current name

        Returns:
        ________
        model (Keras model):
        The loaded model
        '''
        location = self.location + "/models/{}/{}/model.h5".format(self.model_name, city)

        try:
            if os.path.exists(location):
                model = load_model(location)
            else:
                self.logger.info("{} not found!".format(location))
        except Exception as e:
            self.logger.info("Failed to load model. Exception: {}".format(str(e)))

        return model
    
    def save_predictions(self, df, X, model, city, runtype):
        '''
        Saves prediction by adding it to the column

        Parameters:
        ___________
        df (pandas dataframe):
        The pandas dataframe to perfrom the prediction from

        X (Numpy):
        The X values to be sent manually to save time

        model (Keras Model): 
        Model to perform predictions off

        city (string):
        City whose prediction is taking place. For saving in folder
        
        runtype (string):
        backtest or forwardtest
        '''
        finalDf, metrics = self.model.get_predictions(model, df, X, runtype=runtype)

        saveLocation = self.location + "/models/{}/{}/{}".format(self.model_name, city, runtype)

        if not os.path.exists(saveLocation):
            os.makedirs(saveLocation)

        finalDf.to_csv(saveLocation + "/predicted.csv", index=False)
        self.logger.info("Saved to {}".format(saveLocation + "/predicted.csv"))

        data = json.dumps(metrics, default=default)

        with open(saveLocation + "/metrics.json", 'w') as fp:
            json.dump(data, fp)

        self.logger.info("Saved to {}".format(saveLocation + "/metrics.json"))