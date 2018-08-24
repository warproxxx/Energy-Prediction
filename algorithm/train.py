from models import model_building

import numpy as np
import pandas as pd
import os
from glob import glob

from basic_utils import get_logger, get_location

logger = get_logger(get_location() + "/logs/model.log")

for location in glob('data/processed/*'):
    city = location.replace("data/processed/", "")
    f = location + "/data.csv"
    df = pd.read_csv(f)

    logger.info("Read {}".format(f))

    models = ['tri_model_15_minute', 'tri_model_1_hours']

    for model in models:
        model_builder = model_building(model)
        data = model_builder.get_data(df)

        logger.info("Got data of size {}".format(data.shape))

        train_x, train_y, test_x, test_y = model_builder.split_train_test(data, 0.1)

        logger.info("Train X: {} Train Y: {} Test X: {} Test Y: {}. Now training".format(train_x.shape, train_y.shape, test_x.shape, test_y.shape))

        if (model == "tri_model_15_minute"):
            model = model_builder.get_model(train_x, train_y, batch_size=512,  epochs=10)
        elif (model == "tri_model_1_hours"):
            model = model_builder.get_model(train_x, train_y, batch_size=512,  epochs=50)
            
        logger.info("Model trained")

        model_builder.save_model(model, city)
