import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['axes.formatter.useoffset'] = False
from scipy.signal import argrelextrema
import pyteomics
from pyteomics import auxiliary, mass, mzxml

###############################################################################

class mzXML:
    '''Class representing .raw file for ETL'''

    """Class constructed for mzXML data processing"""

    def __init__(self, mz_file):
        # convert file path to raw string
        self.path_to_file = r"{}".format(mz_file)

        # instantiate ms1 and ms2 data arrays
        self.ms1_data = None
        self.ms2_data = None

        # read in data
        self.data = pyteomics.mzxml.read(self.path_to_file, use_index=True)

        # collect data using func(get_ms_data)
        self.get_ms_data()

    def __repr__(self):
        return f"mzXML object constructed from {self.path_to_file}"

    def get_ms_data(self):
        """
        Extracts the MS1 and MS2 level data from file.

        self.ms1_data will be populated as a 3xN multidimensional array that
        contains time, precursor_masses, and precursor_mass_intensity

        self.ms2_data will be populated as a 5xN multidimensional array that
        contains time, precursor_mass, precurcor_charge, fragment_ion_masses,
        and fragment_ion_intensity

        returns: None
        """

        # instantiate return variables
        ms1_data = []
        ms2_data = []

        # iterate through each scan
        # each scan is a dictionary/hash_table
        for scan in self.data:

            # retention time, m/z values, and intensity values are found in every scan
            time = scan["retentionTime"]
            masses = scan["m/z array"]
            intensities = scan["intensity array"]

            # sort data into appropriate arrays
            if scan["msLevel"] == 1:
                ms1_data.append([time, masses, intensities])

            elif scan["msLevel"] == 2:
                # first collect additional info
                precursor_info = scan["precursorMz"][0]
                precursor_mass = precursor_info["precursorMz"]
                precursor_charge = precursor_info["precursorCharge"]

                ms2_data.append(
                    [time, precursor_mass, precursor_charge, masses, intensities]
                )
        
        # point class to multidimensional arrays
        self.ms1_data = np.array(ms1_data)
        self.ms2_data = np.array(ms2_data)

        return

    def _precursor_to_csv(self, precursor_list, max_len=2000, path=None, intensities=False):

        '''To be called from func 'get_precursors'. Returns .csv
           file of all precursors identified in mzxml object.
           
           args:
                - precursor_list (type: list or dict) iterable containing 
                  rounded precursor values. Precursor and intensities in dict.
                - max_len (type: int) value representing number of rows returned
                  from pandas dataframe
                - path (type: str) path where .csv will be saved
                - intensities (type: bool) when True, exported dataframe will
                  contain intensity values associated with precursor masses
        '''

        if path is None:
            path = self._file_path.split('.')[0]  + '_precursors.csv'
        else:
            path = path + '_precursors.csv'

        if isinstance(precursor_list, list):
            df = pd.DataFrame(precursor_list)
        elif isinstance(precursor_list, dict):
            keys = list(precursor_list.keys())
            vals = list(precursor_list.values())
            df = pd.DataFrame({'mass':keys, 'int':vals})

        df = df.iloc[:max_len, :intensities+1]
        df.to_csv(path, index=False, header=False)
        print(f'...precursors.csv file created in {path}')
        return

    def get_tree(self):
        return auxiliary.print_tree(next(self.data))

    def get_precursors(self, decimals=2, by=None):

        '''Function to pull all recognized precursor m/z values with
           more than 1 fragment.
           
           args: 
                - decimals (type: int) number of decimal points returned
                  from precursor mass
                - by (type: str) structured order of precursor masses. 
                  options ['Intensity'] '''

        precursors = []
        intensities = []

        for x in self.data:
            if x['msLevel'] == 2:
                frags = x['m/z array']
                # frag_int = x['intensity array']
                if len(frags) > 1:
                    precursor = x['precursorMz'][0]['precursorMz']
                    precursor = np.round(precursor, decimals)
                    intensity = x['precursorMz'][0]['precursorIntensity']
                    precursors.append(precursor)
                    intensities.append(intensity)
        print(f'{len(set(precursors))} precursors collected from {self._file_path}')
        if by == None:
            precursors = sorted(list(set(precursors)))
            self._precursor_to_csv(precursors)
        elif by == 'Intensity':
            d = dict(zip(precursors, intensities))
            d = dict(sorted(d.items(), key=lambda x: x[1], reverse=True))
            self._precursor_to_csv(d)
        return

    def get_scan(self, scan_num):
        '''
        Function that returns the m/z and intensity arrays from given scan number.

        :param scan_num: scan index number

        :returns: m/z array, intensity array
        '''
        if isinstance(scan_num, int):
            scan_num = str(scan_num + 1)
        elif isinstance(scan_num, str):
            pass
        scan = self.data[scan_num]
        return scan['m/z array'], scan['intensity array']


    def base_peak(self):
        xs, ys = [], []
        if self.ms1_data is None:
            for i, scan in enumerate(self.data):
                if scan['msLevel']==1:
                    xs.append(scan['retentionTime'])
                    ints = scan['intensity array']
                    ys.append(np.max(ints))
        else: # ms1 data has already been created
            data = self.ms1_data.flat
            xs = data[0::3]
            ints = data[2::3]
            for arr in ints:
                ys.append(np.max(arr))
        return np.array(xs), np.array(ys)

    def ms1_search(self, val_list, num_dec=2):
        '''
        Function to return plot, xs, and ys of multiple masses in 
        pseudo-EIC data.
        '''
        if self.ms1_data is None:
            data = self.data
        else: # ms1 data has already been created
            data = self.ms1_data
        xs, ys = [], []
        for _, scan in enumerate(data):
            if scan['msLevel'] == 1:
                xs.append(scan['retentionTime'])
                precs = np.round(scan['m/z array'], num_dec)
                prec_int = scan['intensity array']
                pull_int = prec_int[np.isin(precs, val_list)]
                if pull_int.size == 0:
                    ys.append(0)
                else:
                    ys.append(np.max(pull_int))
        return np.array(xs), np.array(ys)


    def ms1_extract(self, search_mass, tolerance=10):
        '''
        Function to return plot, xs, and ys of single mass in 
        pseudo-EIC data.
        '''
        xs, ys = [], []
        low, high = mass_tolerance(search_mass, tolerance)
        for _, scan in enumerate(self.ms1_data):
            xs.append(scan[0])
            precs = scan[1]
            ids = np.where(np.logical_and(precs >= low, precs <= high))
            if len(ids[0]) > 0:
                ys.append(np.max(scan[2][ids]))
            else:
                ys.append(0)
        return np.array(xs), np.array(ys)
    
    def ms2_search(self, search_val, kind='prof', frequency=False):
        '''
        Function to return pseudo-EIC of ms2 ion of interest.
        '''
        num_dig = len(str(search_val).split('.')[-1])
        xs, ys = np.zeros(len(self.data)), np.zeros(len(self.data))
        count = 0
        # xs, ys = [], []
        for i, scan in enumerate(self.data):
            rt = scan['retentionTime']
            xs[i] = rt
            if scan['msLevel'] == 2:
                count += 1
                if kind == 'prof':
                    try:
                        frags = np.round(scan['m/z array'], num_dig)
                        frag_int = scan['intensity array']
                        if len(frags) > 1:
                            idx = np.where(frags==search_val)
                            if idx[0]:
                                ys[i] = frag_int[idx[0]]
                    except:
                        raise ValueError('Possible profile data in file. Call function again with "kind=cent" argument.')
            
                if kind == 'cent':    
                    frags = np.round(scan['m/z array'], num_dig)
                    frag_int = scan['intensity array']
                    idx = argrelextrema(frag_int, np.greater)
                    frags = frags[idx]
                    frag_int = frag_int[idx] 
                    if len(frags) > 1:
                        idx = np.where(frags==search_val)
                        if idx[0]:
                            ys[i] = frag_int[idx[0]]
        if frequency:
            return np.array(xs), np.array(ys), count
        return np.array(xs), np.array(ys)

###############################################################################

def fragments(peptide, types=('b', 'y'), max_charge=1):
    '''
    Function that returns theoretical fragments of peptide.
    Modeled from : https://pyteomics.readthedocs.io/en/latest/examples/example_msms.html

    :param peptide: (str) peptide sequence
    :param types: (tuple) types of fragments desired
    :param max_charge: (int) maximum charge state of fragment ions
    '''
    d = {}
    for ion_type in types:
        d[ion_type] = []
        for i in range(1, len(peptide)):
            for charge in range(1, max_charge+1):
                if ion_type[0] in 'abc':
                    if i == 0:
                        continue
                    m = mass.fast_mass(
                        peptide[:i], ion_type=ion_type, charge=charge)
                else:
                    m = mass.fast_mass(peptide[i:], ion_type=ion_type, charge=charge)
                d[ion_type].append(m)
    return d

def prof_to_cent(xs, ys):
    '''
    Function to turn profile data to centroid.
    Collects relative maximums and uses indexes of those
    maximums to decipher xs and ys arrays.

    :param xs: (array) array of x data
    :param ys: (array) array of y data
    '''
    idx = argrelextrema(ys, np.greater)
    xs, ys = xs[idx], ys[idx]
    return xs, ys

def mass_tolerance(mass, ppm=10):
    '''
    Function that returns low and high end of mass tolerance range.

    :param mass: (float) mass used to calculated +/- tolerance
    :param ppm: (int) ppm mass error allowed
    '''
    low = ppm * mass / 1e6 - mass
    high = ppm * mass / 1e6 + mass
    return abs(low), abs(high)