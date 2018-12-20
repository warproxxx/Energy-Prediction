# Energy Price Prediction - A full algotrading system

![Screenshot](https://i.imgur.com/w8NhHkC.png)

A live version can be found at http://52.11.89.192:8000/dashboard/

This is a fully functional algorithmic system that extracts live and historic energy data, cleans it, runs machine learning model to train and perform prediction on future (forward testing) and past (backtesting) data.

This repositry focuses more on backtesting and visualization than on ML algorithm and the validity of trades. 

algorithm/downloader.py extract live and historic energy price data from http://mis.ercot.com/ to save it into csv files. Then data is cleaned and machine learning models are stored in algorithm/models.py

Training can be  doing using algorithm/train.py manually. It is easy to add new model.

After training is done, we can have the system consider the new algorithm algorithm/run.py. The system is dynamic. By deleting or adding folders inside algorithm/models and placing files like there is, we can move or remove models.

Backtesting can be done per requested using the web interface. We can chose how to interpret the strategy to make trades. To run:

`python3 manage.py runserver`
