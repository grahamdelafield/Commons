import matplotlib.pyplot as plt
import numpy as np
import os
import re
from scipy.cluster import hierarchy
from modlamp.descriptors import PeptideDescriptor

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

def get_valid_counts(dataframe, column: str, needed: int, criteria='exact'):
    """
    Count occurences of data in specified columns. Only keep rows containing values
    that keep the minimum number of requirements.
    
    :arg dataframe: 
        (pd.DataFrame)  dataframe containing data
    :arg column:
        (str)   column name containing data to bew counted
    :arg needed:
        (int)   number of occurrences required for row to be kept

    :arg criteria:
        (str)   how data should be filtered. One of ['exact', 'greater_equal',
                'greater', 'less', 'less_equal']
        
    returns: reduced dataframe
    """
    # make sure filter does not force error
    allowed_criteria = ['exact', 'greater_equal', 'greater', 'less', 'less_equal']
    
    assertion = criteria in allowed_criteria
    val_err = ValueError(f"Keyword 'criteria' must be one of {allowed_criteria}")
    assert assertion, val_err

    # get value counts of specified column
    counts = dataframe[column].value_counts()

    # find keys that have required count
    match criteria:
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
    """Create dendrogram from hierarchical clustering data"""
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

def chunk(arr, max_num):
    """
    <generator>
    
    Takes list of values or masses, chunks the list
    according to a predefined step size.
    
    :arg arr:   (list, np.array)    the list of masses to be combined
    :arg max_num:   (int)   maximum number of values to exist in chunks
    
    yields list
    """
    # print(len(arr)//max_num)
    for i in range(0, len(arr)//max_num):
        yield arr[i::len(arr)//max_num]

def consecutive_chunks(arr: list, N: int):
    """
    Iterate through array and generate chunks of specified length N. These chunks
    are constrainted to be adjacent to one another in the array.

    :arg arr:
        (list, np.array)    array to be parsed
    :arg N:
        (int)               length of chunk to be generated
    """
    for i in range(0, len(arr), N):
        yield arr[i:i+N]


def alignment_to_bits(alignment_df):
    """
    Takes an alignment matrix from LogoMaker and returns 
    the same matrix in bits
    
    :arg alignment_df:  (pd.DataFrame)  The alignment matrix from LogoMaker
    """

    align_transpose = alignment_df.T.copy()

    # calcualte % occupancy by each amino acid in position
    for column in align_transpose.columns:
        align_transpose[column] = align_transpose[column]/align_transpose[column].sum()

    # calculate base probability
    initial = 20 * -0.05 * np.log2(0.05)
    
    for column in align_transpose:
        col_vals = align_transpose[column].values
        col_vals = col_vals[np.where(col_vals>0)]

        running_sum = 0
        for val in col_vals:
            running_sum += -1*val*np.log2(val)

        align_transpose[column] = align_transpose[column]*(initial-running_sum)

    return align_transpose.T

def fc_significance(row, p, f, change_threshold=2):
    """Operate on pandas dataframe to determine statistically signficant fold change."""
    pval = row[p]
    fold_change = row[f]
    if pval > 0.05:
        return "not significant" 
    if fold_change >= change_threshold:
        return "upregulated"
    elif fold_change <= -change_threshold:
        return "downregulated"
    else:
        return "not significant"
    
def pep_desc(seq: str, scale="gravy") -> float:
    """
    Takes in peptide sequence and returns descriptor score.
    
    :arg seq:   (str)   peptide sequnce on which score will be calculated
    :arg scale: (str)   one of the approved scales in Modlamp.PeptideDescriptor
    
    returns float"""
    desc = PeptideDescriptor(seq, scale)
    desc.calculate_global()
    return desc.descriptor[0][0]


def sequence_logo_modifier(logo, peptide_length, **kwargs):
    """
    Takes in sequence logo from package Logomaker and returns logo with modified
    attributes.
    
    :arg logo:  (Logomaker.Logo)    sequence logo to be modified
    """
    hfont = {'fontname':'Arial', 'weight':"bold", "size":12}

    logo.ax.set_xticklabels(range(-1, peptide_length+2, 2),  **hfont)
    logo.ax.spines[['right', 'top']].set_visible(False)
    y_labels = logo.ax.get_yticklabels()
    logo.ax.set_ylabel("Bits", **hfont)
    logo.ax.set_xlabel("Position", **hfont)
    logo.ax.set_yticklabels(y_labels, **hfont)
    logo.ax.set_title(kwargs.get("title", "Untitled Logo"), **hfont)

    return logo 

def insert_modification(sequence: str, motif: str, insertion: str):
    """
    Parse the sequence and make insertion everywhere the motif is found.
    :arg sequence:  (str)   sequence to be parsed
    :arg motif:     (str)   motif that indicates where insertion should be made
                            can be text or regular expression
    :arg insertion: (str)   the insertion that should be made after each motif

    usage:
        >>> sequnce = "GRAHAMDELAFIELDISAWESOME"
        >>> motif = "D"
        >>> insertion = "[+18]"

        insert_modification(sequence, motif, insertion) --> "GRAHAMD[+18]ELAFIELD[+18]ISAWESOME"
    """

    recognition_pattern = re.compile(motif)
    
    insertion = motif+insertion

    new_sequence = re.sub(recognition_pattern, insertion, sequence)

    return new_sequence