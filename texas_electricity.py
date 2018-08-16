# -*- coding: utf-8 -*-
"""
Created on Fri Aug 2 18:10:06 2018
"""
import requests
import re
import os
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd
import time
import pickle
import zipfile

save_path = r"FOLDER_TO_SAVE_DATA"

start_time = time.time()
user_agent = UserAgent()

def try_get_page_soup(page_url):
    soup = None
    
    try:
        headers = {'User-Agent':str(user_agent.random)}
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
            soup = BeautifulSoup(page.text)
    except:
        soup = None
        
    return soup

def get_response(page_url):
    page = None
    try:
        headers = {'User-Agent':str(user_agent.random)}
        page = requests.get(page_url, headers)
    except:
        print("error loading the page: {0}".format(page_url))
    return page
        

def load_data(filename):
    df = None
    try:
        df = pd.read_csv(filename, encoding='latin1')        
    except:
        pass    
    return df

start_page = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=12300&reportTitle=LMPs%20by%20Resource%20Nodes,%20Load%20Zones%20and%20Trading%20Hubs&showHTMLView=&mimicKey"
folder = "LMPs by Resource Nodes, Load Zones and Trading Hubs"
root = "http://mis.ercot.com"

if not os.path.exists(os.path.join(save_path, folder)):
    os.makedirs(os.path.join(save_path, folder))
    
save_path = os.path.join(save_path, folder)

soup = try_get_page_soup(start_page)
rows = soup.find_all("tr")

print(len(rows))

data = []

for i, row in enumerate(rows):
    if i% 100 == 0:
        print(i)
    #get the text written in the row
    row_link = row.find_all("a")
    if len(row_link) > 0:
        row_link = row_link[0].get("href")
        filename = str(row.find_all("td", {"class": "labelOptional_ind"})[0].text)
        #this is the valid data entry
        #now check if the data is the csv data or the xml data
        if "_csv.zip" in row.text:
            #download the file
            page = get_response(root + row_link)
            if(page != None):
                with open(os.path.join(save_path, filename), "wb") as f:
                    f.write(page.content)
                zf = zipfile.ZipFile(os.path.join(save_path, filename))
                zf.extractall(save_path)
                zfile = os.path.join(save_path, zf.infolist()[0].filename)
                zf.close()

                #delete the zip file
                os.remove(os.path.join(save_path, filename))

                #load the data
                df = load_data(zfile)                
                
                #delete the csv file
                os.remove(zfile)
                
                if df is not None:
                    data.append(df)
                    

print("total data points: {0}".format(sum([a.shape[0] for a in data])))

data = pd.concat(data)
data.to_csv(os.path.join(save_path, "all_data.csv"), index=False)
end_time = time.time()
print("done!")
print((end_time-start_time)/60)