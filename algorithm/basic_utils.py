import os
import inspect
import logging

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
    saveIn = os.path.dirname(fullLocation)

    if not os.path.exists(saveIn):
        os.makedirs(saveIn)
    
    try:
        loggerName = fullLocation.split("/")[-1]
    except:
        loggerName = fullLocation

    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(fullLocation, 'a')
    logger.addHandler(handler)
    return logger

def create_directory_structure(rootDir, cities):
    '''
    Create the required directory structure

    Parameters:
    ___________
    rootDir (string)
    '''
    os.makedirs("{}/data/downloading/live".format(rootDir), exist_ok=True)
    os.makedirs("{}/data/downloading/historic".format(rootDir), exist_ok=True)

    for city in cities:
        os.makedirs("{}/data/processed/{}/models".format(rootDir, city), exist_ok=True)