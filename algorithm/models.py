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

try:
    import pickle
except:
    import cpickle

class tri_model_15_minute():
    def __init__(self):
        self.sequence_length = 24

    def get_data(self, df):
        self.df = df

        data = df['SettlementPointPrice'].values
        data_out = []

        for i in range(len(data)-self.sequence_length+1):
            data_out.append(data[i:i+self.sequence_length])

        data = np.array(data_out)
        return data

    def split_train_test(self, data, test_fraction=0.2):
        self.trainTestIndicator = np.zeros(data.shape[0])
        train_ind = int(round((1-test_fraction)*data.shape[0]))

        train_set = data[:train_ind,:]

        self.trainTestIndicator[:train_ind] = 1

        self.X_train = train_set[:,:-1]
        self.Y_train = train_set[:,-1]

        self.X_test = data[train_ind:, :-1]
        self.Y_test = data[train_ind:, -1]

        self.X_train = np.reshape(self.X_train, (self.X_train.shape[0], self.X_train.shape[1], 1))
        self.X_test = np.reshape(self.X_test, (self.X_test.shape[0], self.X_test.shape[1], 1))

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

    def get_predictions(self, model):
        X = np.append(self.X_train, self.X_test, axis=0)
        predicted = model.predict(X)

        self.df['Predicted'] = [None]*(self.df.shape[0]-len(predicted)) + list(predicted.reshape(-1))
        self.df['Indicator'] = [None]*(self.df.shape[0]-len(predicted)) + list(self.trainTestIndicator.reshape(-1))

        self.df['Direction'] = (self.df['Predicted'] > self.df['SettlementPointPrice']).astype(int)
        
        actualDirection = (self.df['SettlementPointPrice'].shift(-1) > self.df['SettlementPointPrice']).astype(int)
        
        metrics = {}

        # self.df = self.df.fillna(method='bfill')
        # self.df = self.df.fillna(method='ffill')

        # metrics['RMS Error'] = mean_squared_error(self.df['SettlementPointPrice'].shift(-1),self.df['Predicted'])
        # metrics['R2 Score'] = r2_score(self.df['SettlementPointPrice'].shift(-1),self.df['Predicted'])

        metrics['Directional Accuracy'] = sum(self.df['Direction'] == actualDirection)/self.df['Direction'].shape[0]
        metrics['True Positive'] = np.sum(np.logical_and(self.df['Direction']==1, actualDirection==1))
        metrics['True Negative'] = np.sum(np.logical_and(self.df['Direction']==0, actualDirection==0))
        metrics['False Positive'] = np.sum(np.logical_and(self.df['Direction']==1, actualDirection==0))
        metrics['False Negative'] = np.sum(np.logical_and(self.df['Direction']==1, actualDirection==0))

        metrics['Precision'] = metrics['True Positive'] / (metrics['True Positive'] + metrics['False Positive'])
        metrics['Recall'] = metrics['True Positive'] / (metrics['True Positive'] + metrics['False Negative'])

        metrics['F1 Score'] = (2 * metrics['Precision'] * metrics['Recall']) / (metrics['Precision'] + metrics['Recall'])

        return self.df, metrics
        
class tri_model_1_hour(tri_model_15_minute): 
    def get_data(self, df):
        self.df = df

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

    def get_data(self, df):
        '''
        Modifies the data so it can be suitably used with the correct model
        '''
        data = self.model.get_data(df)
        return data

    def split_train_test(self, data, test_fraction=0.2):
        '''
        Parameters:
        ___________
        data (list or pandas or whatever):
        The data to split

        Returns:
        ________
        X_train, Y_train, X_test, Y_test, trainTestIndicator

        trainTestIndicator contains 1 and 0 where 1 indicates training and 0 indicates test
        '''
        X_train, Y_train, X_test, Y_test, trainTestIndicator = self.model.split_train_test(data, test_fraction)
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
    
    def save_predictions(self, model, city):
        finalDf, metrics = self.model.get_predictions(model)
        saveLocation = self.location + "/models/{}/{}".format(self.model_name, city)
        finalDf.to_csv(saveLocation + "/predicted.csv", index=False)
        self.logger.info("Saved to {}".format(saveLocation + "/predicted.csv"))

        with open(saveLocation + "/metrics.json", 'wb') as fp:
            pickle.dump(metrics, fp, protocol=pickle.HIGHEST_PROTOCOL)

        self.logger.info("Saved to {}".format(saveLocation + "/metrics.json"))