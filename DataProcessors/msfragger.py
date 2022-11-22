############################################################
# module to load, transform, return typical msfragger data #
############################################################

import pandas as pd
import re 

class msf_processor:
    def __init__(self, files: list):
        
        # make sure files are list of strings
        in_list_err = f"""Files must be submitted as a list. You provided a {type(files)}"""
        file_type_err = f"""Invalid list entry. All files must enter as strings containing absolute path of the document."""

        if not isinstance(files, list):
            raise TypeError(in_list_err)
        
        if not all(isinstance(file, str) for file in files):
            raise TypeError(file_type_err)


        self.data_files = files
        self.data = pd.DataFrame()
        
        for file in self.data_files:
            data = pd.read_csv(file, delimiter='\t')
            self.data = pd.concat([self.data, data])
            self.data.reset_index(inplace=True, drop=True)
        
        self._rename_columns()
 

    def __repr__(self):
        p1 = "MSF Processor constructed on the following data:"
        return '\n'.join([p1]+self.data_files)

    def _rename_columns(self):
        """Rename all columns to something more manageable"""

        # get old_columns
        columns = [c for c in self.data.columns]

         # replace special characters
        char_pat = re.compile(r"[\[\]\(\)\|\.\:\\\/\+]")
        for i, col in enumerate(columns):
            col = re.sub(char_pat, "", col)

            # turn to lower case
            col = col.lower()

            # replace name
            columns[i] = col

        # replace pseudonymms with words
        unwanted = [r"-", r"\#", r"\%"]
        replacements = [r" ", r"num", r"percent"]

        for i, col in enumerate(columns):
            for j, reg in enumerate(unwanted):
                pat = re.compile(reg)
                col = re.sub(pat, replacements[j], col)

            # remove all spaces
            col = col.replace(" ", "_")

            # replcae name with new string
            columns[i] = col

        # set new columns
        self.data.columns = columns 

        return 


    def add_special_column(self, col_name: str, col_value):
        """
        Adds new column to current dataframe.
        
        :arg col_name:  (str)   name of new column
        :arg col_value: (any)   data to be contained in new column
        """

        self.data.loc[:, col_name] = col_value

        return 

    def join_processors(self, other):
        """
        Combines one dataframe with another. Handles index and others.
        
        :arg other: (pd.DataFrame)  dataframe to be merged with current
        """
        self.data_files.extend(other.data_files)
        self.data = pd.concat([self.data, other.data])
        self.data.reset_index(inplace=True, drop=True)

        return
    