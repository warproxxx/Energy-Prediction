import os
import pandas as pd
from glob import glob
from collections import deque
from io import StringIO

from downloader import download
from cleaner import cleaner

from basic_utils import get_location, get_logger, create_directory_structure

import time
import json
from train import perform_training

cwd = get_location()
logging = get_logger(get_location() + "/logs/run.log")
liveURL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=12301&reportTitle=Settlement%20Point%20Prices%20at%20Resource%20Nodes,%20Hubs%20and%20Load%20Zones&showHTMLView=&mimicKey"
historicURL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13061&reportTitle=Historical%20RTM%20Load%20Zone%20and%20Hub%20Prices&showHTMLView=&mimicKey"

while True:
    try:
        with open(cwd + "/cities.json") as json_file:
            json_data = json.load(json_file)
            cities = json_data['cities']

        create_directory_structure(cwd, cities)

        runtype = "forwardtest"

        #using HB_HOUSTON but can use anything else
        try:
            with open('data/processed/HB_HOUSTON/forwardtest/data.csv', 'r') as f:
                q = deque(f, 1)
                starting = pd.to_datetime(pd.read_csv(StringIO(''.join(q)), header=None)[0][0])
        except:
            try:
                with open('data/processed/HB_HOUSTON/backtest/data.csv', 'r') as f:
                    q = deque(f, 1)
                    starting = pd.to_datetime(pd.read_csv(StringIO(''.join(q)), header=None)[0][0]) 
            except:
                runtype = "backtest"
                starting = pd.to_datetime("2010-12-01 00:00:00")

        logging.info("Starting data collection for {} in date: {}".format(runtype, starting))

        historicDownloader = download(historicURL, "historic", starting)
        historicDownloader.perform_download()

        liveDownloader = download(liveURL, "live", starting)
        liveDownloader.perform_download()

        #assert downloaded if required later

        cleaner(runtype).clean()

        #assert the cleaned data exists and is clean
        #totalMissing = sum((df['Date'].shift(-1)[:-1] - df['Date'][:-1]).astype('timedelta64[m]') != 15)

        #add code for training here too after testing that above functions work
        perform_training()
    except Exception as e:
        logging.info("Got error - {}".format(str(e)))

    time.sleep(300)