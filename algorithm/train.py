from models import model_building

import numpy as np
import pandas as pd
import os
from glob import glob

from basic_utils import get_logger, get_location

class trainer():
    def __init__(self, models=None):
        self.logger = get_logger(get_location() + "/logs/model.log")
        self.locations = glob('data/processed/*')

        if (models == None):
            self.models = ['tri_model_15_minute', 'tri_model_1_hours']
        else:
            self.models = models
        
        self.currLocation = get_location()

    def train(self):
        for location in self.locations:
            city = location.replace("data/processed/", "")
            bTestDirectory = self.currLocation + "/models/{}/{}/backtest/".format(self.models[0],city)

            if (os.path.isdir(bTestDirectory)):
                runtype = "forwardtest"
                forward = pd.read_csv(location + '/forwardtest/data.csv')
                df = pd.concat([pd.read_csv(location + '/backtest/data.csv')[-100:], forward]).reset_index(drop=True)
                self.logger.info("Read data.csv for forwardtest")
            else:
                runtype = "backtest"
                f = location + "/backtest/data.csv"
                df = pd.read_csv(f)
                self.logger.info("Read {} for backtest".format(f))

            for model in self.models:
                model_builder = model_building(model)
                X, y = model_builder.get_XY(df)
                self.logger.info("Got data. The size of X is {} and that of y is {}".format(X.shape, y.shape))

                if (runtype == "backtest"):
                    train_x, train_y, test_x, test_y = model_builder.split_train_test(X, y, 0.1)
                    
                    self.logger.info("Train X: {} Train Y: {} Test X: {} Test Y: {}. Now training".format(train_x.shape, train_y.shape, test_x.shape, test_y.shape))

                    if (model == "tri_model_15_minute"):
                        model = model_builder.get_model(train_x, train_y, batch_size=512,  epochs=10)
                    elif (model == "tri_model_1_hours"):
                        model = model_builder.get_model(train_x, train_y, batch_size=512,  epochs=50)
                        
                    self.logger.info("Model trained")

                    model_builder.save_model(model, city)
                    model_builder.save_predictions(df, X, model, city, runtype='backtest')
                else:
                    model = model_builder.load_model(city)
                    model_builder.save_predictions(df, X, model, city, runtype='forwardtest')
        