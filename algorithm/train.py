from models import model_building

import numpy as np
import pandas as pd
import os
from glob import glob

for f in glob('data/processed/*'):
    location = os.path.basename(f).replace('.csv', '')
    df = pd.read_csv(f)
    model_builder = model_building()
    data = model_builder.get_data_from_pd(df)
    train_x, train_y, test_x, test_y = model_builder.split_train_test(data, 0.1)

    model = model_builder.tri_model(train_x, train_y)
    predicted_values = model_builder.predict_price(model, test_x)
    model_builder.save_model(model, location, "initial")
    print('model building finished!!')