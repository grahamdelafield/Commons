import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.cluster import hierarchy


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

def make_venn3(data_column: str, ident_column: str, dataframe):
    """
    Extracts data from dataframe and returns intersections of each set.
    
    :arg data_column:
        (str)   name of column containing data
    :arg ident_column:
        (str)   name of column containing identifiers
    :arg dataframe:
        (pd.DataFrame)  data to be parsed
    
    returns set intersections (tuple), group_names (list)

    """
    group_names = dataframe[ident_column].unique()
    assert len(group_names) == 3, f'Too many groups for venn3!! You provided {group_names}'

    a = set(dataframe[(dataframe[ident_column] == group_names[0])][data_column])
    b = set(dataframe[(dataframe[ident_column] == group_names[1])][data_column])
    c = set(dataframe[(dataframe[ident_column] == group_names[2])][data_column])

    a_only = a - b - c 
    b_only = b - a - c 
    c_only = c - a - b 

    abc = a & b & c

    ab = (a & b) - abc
    ac = (a & c) - abc
    bc = (b & c) - abc

    return (len(a_only), len(b_only), len(ab), len(c_only), len(ac), len(bc), len(abc)), group_names

def get_valid_counts(dataframe, column: str, needed: int, filter='exact'):
    """
    Count occurences of data in specified columns. Only keep rows containing values
    that keep the minimum number of requirements.
    
    :arg dataframe: 
        (pd.DataFrame)  dataframe containing data
    :arg column:
        (str)   column name containing data to bew counted
    :arg needed:
        (int)   number of occurrences required for row to be kept

    :arg filter:
        (str)   how data should be filtered. One of ['exact', 'greater_equal',
                'greater', 'less', 'less_equal']
        
    returns: reduced dataframe
    """
    # make sure filter does not force error
    expected_filters = ['exact', 'greater_equal', 'greater', 'less', 'less_equal']
    assert (
        filter in expected_filters,
        ValueError(f"Keyword 'filter' must be one of {expected_filters}")
    )

    # get value counts of specified column
    counts = dataframe[column].value_counts()

    # find keys that have required count
    match filter:
        case 'exact':
            valid = counts[counts.values==needed].keys()
        case 'greater_equal':
            valid = counts[counts.values>=needed].keys()
        case 'greater':
            valid = counts[counts.values>needed].keys()
        case 'less_equal':
            valid = counts[counts.values<=needed].keys()
        case 'less':
            valid = counts[counts.values<needed].keys()

    # keep only rows containing data
    kept = dataframe[dataframe[column].isin(valid)]
    return kept

def fancy_dendrogram(*args, **kwargs):
    max_d = kwargs.pop('max_d', None)
    if max_d and 'color_threshold' not in kwargs:
        kwargs['color_threshold'] = max_d
    annotate_above = kwargs.pop('annotate_above', 0)

    ddata = hierarchy.dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        plt.title('Hierarchical Clustering Dendrogram (truncated)')
        plt.xlabel('sample index or (cluster size)')
        plt.ylabel('distance')
        for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            if y > annotate_above:
                plt.plot(x, y, 'o', c=c)
                plt.annotate("%.3g" % y, (x, y), xytext=(0, -5),
                             textcoords='offset points',
                             va='top', ha='center')
        if max_d:
            plt.axhline(y=max_d, c='k')
    return ddata