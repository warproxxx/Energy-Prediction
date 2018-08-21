# -*- coding: utf-8 -*-
"""
Created on Mon Aug 8 20:17:20 2018
@author: Sumit Choudhary
"""
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.models import load_model
try:
    import pickle
except:
    import cpickle

class data_preprocess(object):
    def __init__(self):
        #self.rtm_data_path = r'Historical RTM Load Zone and Hub Prices.csv'
        self.year_filter = [2018, 2017, 2016, 2015]
        
    def load_data(self, data_path):
        try:
            raw_data = pd.read_csv(data_path)
            print('data loaded: {0} records'.format(raw_data.shape[0]))
            #convert the date format to pandas standard
            raw_data['Delivery Date'] = pd.to_datetime(raw_data['Delivery Date'])
        except Exception as e:
            print('Data Loading error :-> ' + e.message)
            return None
        return raw_data

    def preprocess_data(self, data):
        '''this method does basic pre-processing and filters relevant data'''
        try:
            #create average hourly price data
            average_hourly_price = data.groupby(by = ['Settlement Point Name', 'Delivery Date', 'Delivery Hour'])\
                        ['Settlement Point Price'].mean().reset_index(name='Average_Settlement_Price')
            average_hourly_price['year'] = average_hourly_price['Delivery Date'].dt.year
            average_hourly_price['month'] = average_hourly_price['Delivery Date'].dt.month
            average_hourly_price['day'] = average_hourly_price['Delivery Date'].dt.day
            average_hourly_price.rename(columns={'Delivery Hour':'hour', 'Delivery Date':'date',\
                                                 'Settlement Point Name':'hub', \
                                                 'Average_Settlement_Price':'price'}, inplace=True)                            
            #filter recent years' price data
            average_hourly_price = average_hourly_price[average_hourly_price.year.isin(self.year_filter)]
        except Exception as e:
            print('Data preprocessing error :-> ' + e.message)
            return data
        return average_hourly_price[['hub', 'date', 'year', 'month', 'day', 'hour', 'price']]
    
    def get_hub_level_data(self, data):
        '''this method takes as input a complete data and divides it into hub level data and returns 
        a dictionary of hub level data'''
        groups = {}
        try:
            for name, group in data.groupby(['hub']):
                groups[name] = group
        except Exception as e:
            print('Data grouping error :-> ' + e.message)
        return groups
    
    def stack_daily_data_to_matrix(self, data, sequence_length = 24, mean_shift = False):
        '''stacks the hourly data into a 24 length daily array for every 24 hours'''
        data = data.sort_values(by=['year', 'month', 'day', 'hour'])
        data = data['price'].values
        data_out = []
        for i in range(len(data)-sequence_length+1):
            data_out.append(data[i:i+sequence_length])
        data_out = np.array(data_out)
        if mean_shift:
            mean_value = data_out.mean()
            data_out -= mean_value
        return data_out

class model_building(object):
    def __init__(self):
        self.sequence_length = 24
        self.mean = 0
        
    def split_train_test(self, data, test_fraction=0.2):
        train_ind = int(round((1-test_fraction)*data.shape[0]))
        train_set = data[:train_ind,:]
        
        #shuffle the train set
        np.random.shuffle(train_set)
        
        X_train = train_set[:,:-1]
        Y_train = train_set[:,-1]
        
        X_test = data[train_ind:, :-1]
        Y_test = data[train_ind:, -1]
        
        #reshape the data to suit the LSTM network
        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
        
        return X_train, Y_train, X_test, Y_test
    
    def build_model(self, train_x, train_y):
        # build the model
        model = Sequential()
        
        # layer 1: LSTM
        model.add(LSTM( input_dim=1, output_dim=50, return_sequences=True))
        model.add(Dropout(0.2))
        
        # layer 2: LSTM
        model.add(LSTM(output_dim=100, return_sequences=False))
        model.add(Dropout(0.2))
        
        # layer 3: dense
        # linear activation: a(x) = x
        model.add(Dense(output_dim=1, activation='linear'))
        
        # compile the model 
        model.compile(loss="mse", optimizer="rmsprop")
        
        # train the model 
        model.fit(train_x, train_y, batch_size=512, nb_epoch=50, validation_split=0.05, verbose=1)
        
        return model
    
    def evaluate_model(self, model, test_x, test_y):
        # evaluate the result 
        test_mse = model.evaluate(test_x, test_y, verbose=1)
        print ('\nThe mean squared error (MSE) on the test data set is %.3f over %d test samples.' % (test_mse, len(test_y)))
        return test_mse
        
    def predict_price(self, model, test_x):
        # get the predicted values 
        predicted_values = model.predict(test_x)
        num_test_samples = len(predicted_values)
        predicted_values = np.reshape(predicted_values, (num_test_samples,1))
        
        return predicted_values
    
    def plot_result(self, test_y, predicted_values, model_name, show=False):
        # plot the results 
        fig = plt.figure()
        plt.plot(test_y)
        plt.plot(predicted_values)
        plt.xlabel('Hour')
        plt.ylabel('Electricity Price')
        if show:
            plt.show()
        if not os.path.exists(r"./accuracy"):
            os.makedirs("./accuracy")
        fig.savefig(os.path.join("./accuracy", model_name + '.jpg', bbox_inches='tight'))
        fig.clear()
        
    def save_values(self, predicted_values, test_y):
        # save the result into txt file 
        test_result = np.vstack((predicted_values, test_y))
        a = [['predicted_price', 'actual_price']]
        a.extend(test_result)
        np.savetxt('electricity_price_forcasting.txt', a)
        
    def save_model(self, model, model_name):
        try:
            #save the model for later use
            if not os.path.exists("./models"):
                os.makedirs("./models")
            model.save(os.path.join("./models", model_name + '.h5'))
            print(model_name + " model saved!")
        except:
            print(model_name + " model saving failed!!")
        
    def load_model(self, model_name):
        model = None
        try:
            #load the saved model
            if os.path.exists(os.path.join("./models", model_name + '.h5')):
                model = load_model(os.path.join("./models", model_name + '.h5'))
            else:
                print(model_name + " model not found!")
        except:
            print(model_name + " model loading failed!!")
        return model




##data start##

if __name__ == "__main__":
    rtm_data_path = r'Historical RTM Load Zone and Hub Prices.csv'
    
    #create a preprocessing object
    preprocess = data_preprocess()

    #load data    
    rtm_data = preprocess.load_data(rtm_data_path)
    
    #pre-process
    rtm_data = preprocess.preprocess_data(rtm_data)
    
    #get hub-level data
    hub_level_data = preprocess.get_hub_level_data(rtm_data)
    
    #create a model builder class object
    model_builder = model_building()
    
    #build models for each hub
    for hub, hub_data in hub_level_data.items():
        print('building model for ' + hub)
        
        #stack the data for the hours into days
        data = preprocess.stack_daily_data_to_matrix(hub_data)
        
        #split train test
        train_x, train_y, test_x, test_y = model_builder.split_train_test(data, 0.1)
        
        #build model
        model = model_builder.build_model(train_x, train_y)
        
        #test model
        mse = model_builder.evaluate_model(model, test_x, test_y)
        
        #predict values
        predicted_values = model_builder.predict_price(model, test_x)
        
        #save model
        model_builder.save_model(model, hub)

        #plot model
        try:
            model_builder.plot_result(test_y, predicted_values, "Final Plot")
        except:
            pass
        
    print('model building finished!!')