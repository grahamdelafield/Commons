# the following code is intendecd for extraction, transformation, and loading
# data resulting from Ascore analysis, specifically throught the pyAscore CLI

# all code is provided 'as is' and is not guaranteed beyond its initial design

from pathlib import Path
import pandas as pd
import re
import typing

class AscoreParser:
    """Class used to ETL data output from pyAscore CLI"""

    def __init__(self, files: [str, list]) -> None:
        """
        Creates a new instance of AscoreParser.
        
        :arg files:  (str or list) file(s) to be parsed
        """
        if isinstance(files, str):
            files = [files]
        
        #TODO
        # run check to make sure file is of right type, return correct parser and delimiter
        all_files_pass = self._check_file_format(files)
        if all_files_pass:
            self._read_data(files)

    def _check_file_format(self, files: list) -> [typing.Callable, str]:
        """Check for acceptable file type, columns, """
        _found_exts = []

        for file in files:
            suff = Path(file).suffix
            _found_exts.append(suff)

        ext_err = f"You provided filetypes {set(_found_exts)} but all files should enter as the same type. Please fix and go again."
        assert len(set(_found_exts)) == 1, ext_err
        
        return True
    
    def _read_data(self, files: list) -> pd.DataFrame:
        """Read files and return formated dataframe.
        
        :arg files: (list)  Files to be parsed
        """
        ret_data = pd.DataFrame()
        _headers = []

        # iterate files, read, check headers along the way
        for file in files:
            suff = Path(file).suffix

            match suff:
                case ".tsv":
                    data = pd.read_csv(file, delimiter="\t")
                case ".txt":
                    data = pd.read_csv(file, delimiter="\t")
                case ".csv":
                    data = pd.read_csv(file)
                case ".xlsx":
                    data = pd.read_excel(file)
            if not _headers:
                _headers = data.columns
            else:
                assert set(_headers) == set(data.columns), f"We found an error in {file}. The columns don't match and need to be fixed"

            # format data and return
            data = self._format_columns(data)
            ret_data = pd.concat([ret_data, data]).reset_index(drop=True)

            # instantiate class parameter
            self.data = ret_data

        return ret_data

    def _format_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Formats column names, and data within.
        
        :arg data:  (pd.DataFrame) pandas dataframe with unformatted data
        """
        formatted_data = data.copy()
        new_columns = []

        columns = formatted_data.columns 
        for column in columns:
            # find capitals
            capitals = re.finditer(r"[A-Z]", column)

            # break words
            beginnings = [c.span()[0] for c in capitals] + [len(column)]
            words = [column[beginnings[i]:beginnings[i+1]] for i in range(len(beginnings)-1)]
            words = [w.lower() for w in words]

            # rename
            new_name = "_".join(words)
            new_columns.append(new_name)

        formatted_data.columns = new_columns

        return formatted_data


if __name__=="__main__":
    a = AscoreParser(r"/Users/delafield/code/python/pyascore_test/shift_18.tsv")
    print(a.data)