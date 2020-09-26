from pyteomics import mzml, mzxml, auxiliary
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['axes.formatter.useoffset'] = False

class mzXML:
    """Class representing .raw file for ETL"""

    def __init__(self, mz_file):
        self._file_path = mz_file
        self.data = mzxml.read(mz_file, use_index=True)

    def __repr__(self):
        return f"mzXML object instantiated from {self._file_path}"

    def _precursor_to_csv(self, precursor_list, max_len=2000, path=None, intensities=False):

        """To be called from func 'get_precursors'. Returns .csv
           file of all precursors identified in mzxml object.
           
           args:
                - precursor_list (type: list or dict) iterable containing 
                  rounded precursor values. Precursor and intensities in dict.
                - max_len (type: int) value representing number of rows returned
                  from pandas dataframe
                - path (type: str) path where .csv will be saved
                - intensities (type: bool) when True, exported dataframe will
                  contain intensity values associated with precursor masses
        """

        if path is None:
            path = self._file_path.split(".")[0]  + "_precursors.csv"
        else:
            path = path + "_precursors.csv"

        if isinstance(precursor_list, list):
            df = pd.DataFrame(precursor_list)
        elif isinstance(precursor_list, dict):
            keys = list(precursor_list.keys())
            vals = list(precursor_list.values())
            df = pd.DataFrame({"mass":keys, "int":vals})

        df = df.iloc[:max_len, :intensities+1]
        df.to_csv(path, index=False, header=False)
        print(f"...precursors.csv file created in {path}")
        return

    def get_tree(self):
        return auxiliary.print_tree(next(self.data))

    def get_precursors(self, decimals=2, by=None):

        """Function to pull all recognized precursor m/z values with
           more than 1 fragment.
           
           args: 
                - decimals (type: int) number of decimal points returned
                  from precursor mass
                - by (type: str) structured order of precursor masses. 
                  options ["Intensity"] """

        precursors = []
        intensities = []

        for x in self.data:
            if x["msLevel"] == 2:
                frags = x["m/z array"]
                frag_int = x["intensity array"]
                if len(frags) > 1:
                    precursor = x["precursorMz"][0]["precursorMz"]
                    precursor = np.round(precursor, decimals)
                    intensity = x["precursorMz"][0]["precursorIntensity"]
                    precursors.append(precursor)
                    intensities.append(intensity)
        print(f"{len(set(precursors))} precursors collected from {self._file_path}")
        if by == None:
            precursors = sorted(list(set(precursors)))
            self._precursor_to_csv(precursors)
        elif by == "Intensity":
            d = dict(zip(precursors, intensities))
            d = dict(sorted(d.items(), key=lambda x: x[1], reverse=True))
            self._precursor_to_csv(d)
        return

    def ms1_search(self):
        pass
    
    def ms_search(self, search_val, ms_level):
        '''
        Function to return pseudo-EIC of ms2 ion of interes.
        '''
        num_dig = len(str(search_val).split('.')[-1])
        # xs, ys = np.zeros(len(self.data)), np.zeros(len(self.data))
        xs, ys = [], []
        for i, scan in enumerate(self.data):
            if scan['msLevel'] == ms_level:
                xs.append(scan['retentionTime'])
                frags = np.round(scan['m/z array'], num_dig)
                frag_int = scan['intensity array']
                if len(frags) > 1:
                    idx = np.where(frags==search_val)
                    if idx[0]:
                        ys[i] = frag_int[idx[0]]
        plt.plot(xs, ys)
        plt.show()