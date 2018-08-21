import requests
import re
import os
import inspect
from bs4 import BeautifulSoup
import pandas as pd
import time
import pickle
import zipfile
import logging
import random

def get_name():
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    filename = module.__file__

    full_path = os.path.realpath(filename)

    return full_path

def get_location():
    '''
    Returns the directory of located script
    
    Parameters:
    ___________
    datadir: The current root directory

    Returns:
    ________
    dir_location
    '''

    path = get_name()
    dir_location = os.path.dirname(path)
    return dir_location

def get_logger(fullLocation):
    '''
    fullLocation (string):
    Name of file along with Full location. Alternatively just file name
    '''
    
    try:
        loggerName = fullLocation.split("/")[-1]
    except:
        loggerName = fullLocation

    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(fullLocation, 'w')
    logger.addHandler(handler)
    return logger


class download:
    def __init__(self, url, datatype, logger=None):
        '''
        Parameters:
        ___________
        url (string):
        The URL to download from

        datatype (string):
        live or historic
        '''
        self.datatype = datatype

        if (datatype == "historic"):
            savefolder = "data/historic"
        elif (datatype == "live"):
            savefolder = "data/live"

        self.url = url

        self.savepath = os.path.join(get_location(), savefolder)

        if not os.path.exists(self.savepath):
            os.makedirs(self.savepath)

        self.HEADERS_LIST = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0', 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0']

        if logger == None:
            self.logger = get_logger(get_location() + "/logs/downloader.log")
        else:
            self.logger = logger

    def perform_download(self):
        start_time = time.time()
        root = "http://mis.ercot.com"

        soup = self.try_get_page_soup(self.url)
        rows = soup.find_all("tr")

        self.logger.info("Total Rows: {}".format(len(rows)))
        data = []

        for i, row in enumerate(rows):
            if i% 100 == 0:
                self.logger.info("{}/{}".format(i, len(rows)))

            #get the text written in the row
            row_link = row.find_all("a")
            
            if len(row_link) > 0:
                row_link = row_link[0].get("href")
                filename = str(row.find_all("td", {"class": "labelOptional_ind"})[0].text)
                #this is the valid data entry
                #now check if the data is the csv data or the xml data

                if self.datatype == "historic":
                    toFind = ".zip"
                else:
                    toFind = "_csv.zip"

                if toFind in row.text:
                    #download the file
                    self.logger.info("Downloading {}".format(filename))

                    page = self.get_response(root + row_link)

                    if(page != None):
                        with open(os.path.join(self.savepath, filename), "wb") as f:
                            f.write(page.content)
                        zf = zipfile.ZipFile(os.path.join(self.savepath, filename))
                        zf.extractall(self.savepath)
                        zfile = os.path.join(self.savepath, zf.infolist()[0].filename)
                        zf.close()

                        #delete the zip file
                        os.remove(os.path.join(self.savepath, filename))

                        #load the data
                        df = self.load_data(zfile)                
                        
                        #delete the csv file
                        os.remove(zfile)
                        
                        if df is not None:
                            data.append(df)
        
        self.logger.info("total data points: {0}".format(sum([a.shape[0] for a in data])))

        data = pd.concat(data)
        data.to_csv(os.path.join(self.savepath, "rough.csv"), index=False) #temporary
        data = self.clean_data(data)
        data.to_csv(os.path.join(self.savepath, "all_data.csv"), index=False)
        end_time = time.time()
        self.logger.info("done in {}".format((end_time-start_time)/60))

    def clean_data(self, df):
        if (self.datatype == "live"):
            try:
                historicPoints = pd.read_csv(os.path.join(self.savepath, "all_data.csv").replace("live", "historic"))['SettlementPointName']
                df[df['SettlementPointName'].isin(historicPoints.unique())].reset_index(drop=True)
            except:
                historicPoints = ['HB_BUSAVG', 'HB_HOUSTON', 'HB_HUBAVG', 'HB_NORTH', 'HB_SOUTH', 'HB_WEST', 'LZ_AEN', 'LZ_CPS', 'LZ_HOUSTON', 'LZ_LCRA', 'LZ_NORTH','LZ_RAYBN', 'LZ_SOUTH', 'LZ_WEST']
                df[df['SettlementPointName'].isin(historicPoints)]
        elif (self.datatype == "historic"):
            df = df.rename(columns={'Delivery Date': 'DeliveryDate', 'Delivery Hour': 'DeliveryHour', 'Delivery Interval': 'DeliveryInterval', 'Repeated Hour Flag': 'DSTFlag', 'Settlement Point Name': 'SettlementPointName', 'Settlement Point Type': 'SettlementPointType', 'Settlement Point Price': 'SettlementPointPrice'})
            df = df[['DeliveryDate', 'DeliveryHour', 'DeliveryInterval', 'DSTFlag', 'SettlementPointName', 'SettlementPointType', 'SettlementPointPrice']]
        
        return df

    def try_get_page_soup(self, page_url):
        soup = None
        
        try:
            headers =  {'User-Agent': random.choice(self.HEADERS_LIST)}
            page = requests.get(page_url, headers=headers)
            retry = 1
            while(page.status_code != 200):
                if retry > 3:
                    break
                time.sleep(10)
                page = requests.get(page_url, headers=headers)
                retry += 1
            if page.status_code != 200:
                print("page failed: " + page_url)
            else:
                soup = BeautifulSoup(page.text, "lxml")
        except:
            soup = None
            
        return soup

    def get_response(self, page_url):
        page = None
        try:
            headers = {'User-Agent': random.choice(self.HEADERS_LIST)}
            page = requests.get(page_url, headers)
        except:
            print("error loading the page: {0}".format(page_url))
        return page
            

    def load_data(self, filename):
        df = None

        try:
            if (self.datatype == "live"):
                df = pd.read_csv(filename, encoding='latin1')   
            elif (self.datatype == "historic"):
                df = pd.read_excel(filename)
        except:
            pass    
        return df

# historicDownloader = download("http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13061&reportTitle=Historical%20RTM%20Load%20Zone%20and%20Hub%20Prices&showHTMLView=&mimicKey", "historic")
# historicDownloader.perform_download()

liveDownloader = download("http://mis.ercot.com/misapp/GetReports.do?reportTypeId=12301&reportTitle=Settlement%20Point%20Prices%20at%20Resource%20Nodes,%20Hubs%20and%20Load%20Zones&showHTMLView=&mimicKey", "live")
liveDownloader.perform_download()