from data_plot.bt import perform_backtest
from glob import glob
import os
from algorithm.basic_utils import get_logger

logger = get_logger('algorithm/logs/backtest.log')

test_type = 'backtest'
starting_cash = 10000
comission = 0.01

strategies = ['s1', 's2']

for model in glob('algorithm/models/*'):
    model = os.path.basename(model)
    
    for city in glob('algorithm/models/{}/*'.format(model)):
        city = os.path.basename(city)

        for strategy in strategies:
            logger.info("Performing backtest for {}/{}/{}".format(model, city, strategy))
            _, _, _, _, _, _ = perform_backtest(city, model, test_type, starting_cash, comission, strategy)