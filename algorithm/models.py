import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.models import load_model

import logging

try:
    import pickle
except:
    import cpickle

class model_building(object):
    def __init__(self, logger):
        self.sequence_length = 24
        self.mean = 0
        self.logger = logger

    def get_data_from_pd(self, df):
        '''
        Parameters:
        ___________
        df (Pandas dataframe): 
        Get numpy array of datas
        '''
        data = df['SettlementPointPrice'].values
        data_out = []

        for i in range(len(data)-self.sequence_length+1):
            data_out.append(data[i:i+self.sequence_length])

        data = np.array(data_out)
        return data

        
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
    
    def tri_model(self, train_x, train_y):
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
        model.fit(train_x, train_y, batch_size=512, nb_epoch=50, validation_split=0.05, verbose=2)
        
        return model
    
    def evaluate_model(self, model, test_x, test_y):
        # evaluate the result 
        test_mse = model.evaluate(test_x, test_y, verbose=1)
        self.logger.info ('\nThe mean squared error (MSE) on the test data set is %.3f over %d test samples.' % (test_mse, len(test_y)))
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
        
    def save_model(self, model, model_name, dirname):
        try:
            #save the model for later use
            if not os.path.exists("./models"):
                os.makedirs("./models")
            model.save(os.path.join("./models/{}".format(dirname), model_name + '.h5'))
            self.logger.info(model_name + " model saved!")
        except:
            self.logger.info(model_name + " model saving failed!!")
        
    def load_model(self, model_name):
        model = None
        try:
            #load the saved model
            if os.path.exists(os.path.join("./models", model_name + '.h5')):
                model = load_model(os.path.join("./models", model_name + '.h5'))
            else:
                self.logger.info(model_name + " model not found!")
        except:
            self.logger.info(model_name + " model loading failed!!")
        return model
