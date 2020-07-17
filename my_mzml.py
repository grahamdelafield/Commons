from pyteomics import mzml, mzxml, auxiliary
import numpy as np
import pandas as pd


class mzXML:
    """Class representing .raw file for ETL"""

    def __init__(self, mz_file):
        self._file_path = mz_file
        self.data = mzxml.read(mz_file, use_index=True)

    def __repr__(self):
        return f"mzXML object instantiated from {self._file_path}"

    def _precursor_to_csv(self, precursor_list, path=None):

        """To be called from func 'get_precursors'. Returns .csv
           file of all precursors identified in mzxml object."""

        path = self._file_path.split(".")[0]  + "precursors.csv"
        df = pd.DataFrame(precursor_list)
        df.to_csv(path, index=False, header=False)
        print(f"...precursors.csv file created in {path}")
        return

    def get_tree(self):
        return auxiliary.print_tree(next(self.data))

    def get_precursors(self, decimals=3):
        """function to pull all recognized precursor m/z
           values with more than 1 fragment.
           
           args: 
           
           decimals - number of decimal points returned from 
           precursor mass"""

        precursors = []

        for x in self.data:
            if x["msLevel"] == 2:
                frags = x["m/z array"]
                frag_int = x["intensity array"]
                if len(frags) > 1:
                    precursor = x["precursorMz"][0]["precursorMz"]
                    precursor = np.round(precursor, decimals)
                    precursors.append(precursor)
        print(f"{len(set(precursors))} precursors collected from {self._file_path}")
        
        self._precursor_to_csv(sorted(list(set(precursors))))
        return