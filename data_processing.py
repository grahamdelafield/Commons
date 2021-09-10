import matplotlib.pyplot as plt
import altair as alt
alt.data_transformers.disable_max_rows()
import pandas as pd 
import numpy as np
import os
from scipy.ndimage import gaussian_filter


def get_files(directory='.', exts=['.']):
    '''
    Function that searches the defined directory and reutrns list
    of all files with the specified extension or ending.

    :param directory: (str) raw string of directory to be searched
    :param exts: (list) list of extensions or endings to be returned
    '''
    all_files = []
    for root, _, files in os.walk(directory, topdown=True):
        if exts == ['.']:
            all_files.extend([os.path.join(root, name) for name in files])
        for name in files:
            file_path = os.path.join(root, name)
            for ext in exts:
                if file_path.endswith(ext):
                    all_files.append(file_path)
    return all_files

def iterate_contents(column_name: str, dataframe, get_item: bool=False):
    """
    Iterates through unique items in data from column, 
    yields dataframe where column==item for each.
    
    :arg column_name:
        (str)               name of dataframe column to iterate
    :arg dataframe:
        (pd.dataframe)      dataframe containing all contents
    :arg get_item:
        (bool) <optional>   flag to request the unique item in return
        
    """
    for unique_item in dataframe[column_name].unique():
        result = dataframe[dataframe[column_name]==unique_item]
        if get_item:
            yield unique_item, result
        else:
            yield result

def find_nearest(array, value):
    '''
    Function that searches an array and returns the value nearest to the
    one passed.

    :param array: (array-like) array to be searched
    :param value: (int or float) experimental value
    '''
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]