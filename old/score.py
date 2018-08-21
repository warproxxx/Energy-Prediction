# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 09:47:47 2018

@author: Sumit114358
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

from electricity_cost_prediction import model_building
from electricity_cost_prediction import data_preprocess
import sys

if __name__=='__main__':
    arguments = sys.argv[1:]
    
    if len(arguments) == 0:
        print("Please provide a file for scoring!!")
        filename = "Historical RTM Load Zone and Hub Prices.csv"
        #sys.exit()
    else:
        filename = arguments[0]
    
    #pre-process object
    preprocess = data_preprocess()
    
    #load the data
    data = preprocess.load_data(filename)
    
    #pre process data
    data = preprocess.preprocess_data(data)
    
    
    #hub level data
    hub_level_data = preprocess.get_hub_level_data(data)
    
    #model class
    model_builder = model_building()
    
    for hub, hub_data in hub_level_data.items():
        print("Scoring {0} data!!".format(hub))

        #sort the data
        hub_data = hub_data.sort_values(by=['year', 'month', 'day', 'hour']).reset_index(drop=True)

        #stack the daily data into predicting data
        data = preprocess.stack_daily_data_to_matrix(hub_data, sequence_length=23)

        #load model for the hub
        model = model_builder.load_model(hub)


        #predict price
        predicted_values = model_builder.predict_price(model, data.reshape(-1,23,1))

        #append the predicted values with actual data
        hub_data['predicted_price'] = [None]*(hub_data.shape[0]-len(predicted_values)) + list(predicted_values.reshape(-1))

        #save the data
        if not os.path.exists("./scored"):
            os.makedirs("./scored")
            
        hub_data.to_csv("./scored/" + hub + ".csv", index=False)
        
    print("Scoring done!!")