import os
import pandas as pd
from glob import glob
from collections import deque
from io import StringIO

from downloader import download
from cleaner import cleaner

from basic_utils import get_location, get_logger

import time

cwd = get_location()
logging = get_logger(get_location() + "/logs/run.log")
liveURL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=12301&reportTitle=Settlement%20Point%20Prices%20at%20Resource%20Nodes,%20Hubs%20and%20Load%20Zones&showHTMLView=&mimicKey"
historicURL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13061&reportTitle=Historical%20RTM%20Load%20Zone%20and%20Hub%20Prices&showHTMLView=&mimicKey"

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

logging.info("Starting Date: {}".format(starting))

historicDownloader = download(historicURL, "historic", starting)
historicDownloader.perform_download()

#assert downloaded if required later

liveDownloader = download(liveURL, "live", starting)
liveDownloader.perform_download()

#assert downloaded if required later

#cleaner().clean()
#assert the cleaned data exists





#assert downloading has completed


#assert files are removed, new file is created

#Then add those conditional checks