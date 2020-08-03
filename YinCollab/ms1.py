# code implementation used in collaboration between
# Li and Yin Research groups
#
# code is made available as part of scientific/analytical 
# disclosure during publication
# 
# all code is distributed 'as is' and may be modified to fit 
# custom applications

import numpy as np
import pandas as pd 
import ntpath

class PeakListFile:
    '''
    Class representing an excel document containing
    peak lists copied from xCalibur.
    '''
    # TODO: implement ability to read .csv

    def __init__(self, file, has_header=True):
        assert file.endswith('.xlsx'), 'Please make sure to use .xlsx files.'
        # TODO: implement ability to read .csv
        self.filename = file
        self.header = has_header
        return

    def __repr__(self):
        return f'PeakListFile object instanitated from {self.filename}'

    # TODO: make function to error check file
    def _validate(self):
        pass
        return

    def _read_sheet(self, id_names, sheet='Sheet1'):
        if self.header:
            data = pd.read_excel(self.filename, sheet_name=sheet,
                                      skiprows=range(0,4))
        else:
            data = pd.read_excel(self.filename, sheet_name=sheet)
        # remove minor peaks                                      
        data = data[data['%Area'] > 10]
        # get base file name
        basename = ntpath.basename(self.filename).split('.')[0]
        base = basename[:-1]
        data['Sample'] = [base for i in id_names]
        # use last letter of basename as fraction identifier
        fraction = basename[-1]
        data['Fraction'] = [fraction for i in id_names]
        # set run identifier
        data['Run'] = ['run' + sheet[-1] for i in id_names]
        # set peak identification
        data['Identity'] = id_names
        data = data[['Sample', 'Fraction', 'Run', 'Identity', 'Area', 'Apex RT']]
        return data

    def _compare_peaks(self, dataframe, standard, std_conc):
        data = dataframe
        val = data[data['Identity'].str.startswith(standard)]['Area'].item()
        data['Area Ratio'] = data['Area'] / val
        data['Concentration'] = data['Area Ratio'] * std_conc
        return data
        

    def combine_sheets(self, id_names, standard, std_conc):
        xl = pd.ExcelFile(self.filename)
        df = pd.DataFrame()
        for sheet in xl.sheet_names:
            data = self._read_sheet(id_names, sheet=sheet)
            data = self._compare_peaks(data, standard, std_conc)
            if df.empty:
                df = data
            else:
                df = pd.concat([df, data])
        self.data = df
        return

    def correct_dilution(self, standard, dil_factor):
        df = self.data
        new_conc = []
        for r in zip(df['Identity'], df['Concentration']):
            ident, conc = r[0], r[1]
            if ident!=standard:
                new_conc.append(conc*dil_factor)
            else:
                new_conc.append(conc)
        df['Corrected Concentration'] = new_conc
        self.data = df
        return