import os
import pandas as pd
from glob import glob
from collections import deque
from io import StringIO

from downloader import download
from cleaner import cleaner

<<<<<<< HEAD
from basic_utils import get_location, get_logger

import time
=======
from basic_utils import get_location, get_logger, create_directory_structure

import time
import json
>>>>>>> 3e51dc1addf24c30dd306f26d71509c0a1584532

cwd = get_location()
logging = get_logger(get_location() + "/logs/run.log")
liveURL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=12301&reportTitle=Settlement%20Point%20Prices%20at%20Resource%20Nodes,%20Hubs%20and%20Load%20Zones&showHTMLView=&mimicKey"
historicURL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13061&reportTitle=Historical%20RTM%20Load%20Zone%20and%20Hub%20Prices&showHTMLView=&mimicKey"

<<<<<<< HEAD
if not os.path.exists(cwd + "/data/processed"):
    os.makedirs(cwd + "/data/processed")

if len(glob(cwd + "/data/processed/*")) < 3:
    starting = pd.to_datetime("2010-12-01 00:00:00")
else:
    for file in glob('data/processed/*'):
        with open(file, 'r') as f:
            q = deque(f, 1)
            starting = pd.to_datetime(pd.read_csv(StringIO(''.join(q)), header=None)[0][0])   
        break
=======
with open(cwd + "/cities.json") as json_file:
    json_data = json.load(json_file)
    cities = json_data['cities']

create_directory_structure(cwd, cities)

#using HB_HOUSTON but can use anything else
try:
    with open('data/processed/HB_HOUSTON/data.csv', 'r') as f:
        q = deque(f, 1)
        starting = pd.to_datetime(pd.read_csv(StringIO(''.join(q)), header=None)[0][0])
except:
    starting = pd.to_datetime("2010-12-01 00:00:00")
>>>>>>> 3e51dc1addf24c30dd306f26d71509c0a1584532

logging.info("Starting Date: {}".format(starting))

historicDownloader = download(historicURL, "historic", starting)
historicDownloader.perform_download()

#assert downloaded if required later
<<<<<<< HEAD

liveDownloader = download(liveURL, "live", starting)
liveDownloader.perform_download()

#assert downloaded if required later

# cleaner().clean()
#assert the cleaned data exists




=======

liveDownloader = download(liveURL, "live", starting)
liveDownloader.perform_download()

#assert downloaded if required later
>>>>>>> 3e51dc1addf24c30dd306f26d71509c0a1584532

cleaner().clean()

<<<<<<< HEAD

#assert files are removed, new file is created

#Then add those conditional checks
=======
# #assert the cleaned data exists and is clean
# #totalMissing = sum((df['Date'].shift(-1)[:-1] - df['Date'][:-1]).astype('timedelta64[m]') != 15)
>>>>>>> 3e51dc1addf24c30dd306f26d71509c0a1584532
