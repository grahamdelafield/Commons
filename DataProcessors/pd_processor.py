# The following code is meant explecitly for the accessing, cleaning, and 
# modifying tabular data from Proteome Discoverer
# 
# All code is provided 'as is' and is not guaranteed for to fit any custom 
# workflows beyond its initial design 

import numpy as np 
import pandas as pd 
import os
import re

class PDProcessor:
    def __init__(self, files: list, filename: str=None):

        # ensure files are type list
        filetype_err = f'''Files submitted to PDProcessor must be of {type([])}
            but you have submitted {type(files)}'''
        if not isinstance(files, list):
                raise TypeError(filetype_err)

        self.files = files

        # instantiate output objects
        self.proteins = pd.DataFrame()
        self.peptides = pd.DataFrame()
        self.psms = pd.DataFrame()

        # determine name to associate with data
        for i, file in enumerate(files):
            if filename is None:
                base_name = os.path.basename(file)
            else:
                base_name = filename

            self._current_data = pd.read_excel(file)

    
    def __repr__(self):
        file_string = '\n'.join([f for f in self.files])
        return f'''PDProcessor object constructed from {file_string}'''
    
    def _rename_columns(self, dataframe):
        '''Private function to create usable column names'''

        # get all columns
        column_names = [c for c in dataframe.columns]

        # replace special characters
        char_pat = re.compile(r'[\[\]\(\)\|\.\:]')
        for i, col in enumerate(column_names):
            col = re.sub(char_pat, '', col)
            
            # turn to lower case
            col = col.lower()

            # replace name
            column_names[i] = col

        # replace pseudonymms with words
        unwanted = [r'-', r'\#', r'\%']
        replacements = [r' ', r'num', r'percent']

        for i, col in enumerate(column_names):
            for j, reg in enumerate(unwanted):
                pat = re.compile(reg)
                col = re.sub(pat, replacements[j], col)

            # remove all spaces
            col = col.replace(' ', '_')

            # replcae name with new string
            column_names[i] = col

        # insert new names to dataframe
        dataframe.columns = column_names

    def _gather_proteins(self):
        '''Private function to extract rows with protein data'''

        # extract proteins based off of column contents
        prots = self._current_data.loc[
            (self._current_data['Checked']==1), :
        ] 

        # rename columns
        self._rename_columns(prots)

        # remove any columns where all values are NaN
        prots = prots.dropna(axis=1, how='all')

        # append to output items
        self.proteins = pd.concat([self.proteins, prots])

    def _map_accession(self, parent, child):
        '''
        Private function to map protein accession/description to
        peptide and psm data
        '''

        reqd_len = max(child.index) + 100

        dummy_frame = pd.DataFrame({
            'Value':[None]*reqd_len
        }, index=range(reqd_len))

        dummy_frame = dummy_frame.merge(parent[['accession', 'description']],
                                        how='outer',
                                        left_index=True,
                                        right_index=True)

        dummy_frame.ffill(inplace=True)

        dummy_frame = dummy_frame.merge(child,
                                        left_index=True,
                                        right_index=True)
        return dummy_frame.iloc[:, 1:]


    def _gather_peptides(self):
        '''Private function to extract peptide data'''

        # extract rows based on column contents
        peps = self._current_data.loc[
            (self._current_data['Checked'].isna()) & 
            (self._current_data['Master'].isin([True, 1])), :
        ]

        # remove first column, uneeded
        peps = peps.iloc[:, 1:]

        # gather row with column names from master data object
        cols = self._current_data.iloc[1, 1:]

        # rename with extract column names
        peps.columns = cols

        # map accession and description to data
        peps = self._map_accession(self.proteins, peps)

        # drop any cols with all NaN contents
        peps = peps.dropna(axis=1, how='all')

        # make better column names
        self._rename_columns(peps)

        # clean up the peptide sequences
        peps.loc[:, 'sequence'] = peps.annotated_sequence.map(
                                                self._clean_peptides)

        # append to master object
        self.peptides = pd.concat([self.peptides, peps])

        # reset index
        self.peptides = self.peptides.reset_index()
        self.peptides = self.peptides.drop('index', axis=1)


    def _gather_psms(self):

        # extract rows based on column contents
        psms = self._current_data.loc[
            (self._current_data['Checked'].isna()) & 
            (self._current_data['Master'].isna()) &
            (self._current_data['Accession'] == True), :
        ]

        # remove first column, uneeded
        psms = psms.iloc[:, 2:]

        # gather row with column names from master data object
        cols = self._current_data.iloc[3, 2:]

        # rename with extract column names
        psms.columns = cols

        # map accession and description to data
        psms = self._map_accession(self.proteins, psms)
        
        # drop any cols with all NaN contents
        psms = psms.dropna(axis=1, how='all')

        # make better column names
        self._rename_columns(psms)

        # clean up the peptide sequences
        psms.loc[:, 'sequence'] = psms.annotated_sequence.map(
                                                self._clean_peptides)

        # append to master object
        self.psms = pd.concat([self.psms, psms])

        # reset index
        self.psms = self.psms.reset_index()
        self.psms = self.psms.drop('index', axis=1)
        
    def _clean_peptides(self, sequence):
        '''Private function to remove unneeded characters from sequence sting'''

        reg = re.compile(r'(.*\.)(\w*)(\..*)')
        match = re.search(reg, sequence)
        if match:
            return match.group(2)
        return sequence

    def join_processors(self, other):
        '''Function to join data from two PDProcessor objects'''

        # combine this processor with adjacent
        self.proteins = pd.concat([self.proteins, other.proteins])
        self.peptides = pd.concat([self.peptides, other.peptides])
        self.psms = pd.concat([self.psms, other.psms])

        # reset index of all dataframes
        for frame in [self.proteins, self.peptides, self.psms]:
            frame = frame.reset_index()
            frame = frame.drop('index', axis=1)
        
        return