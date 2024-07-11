## This module is meant to provide a means of interacting with, transforming,
## and loading data exported from MassPike.
#
# All code is provided 'as is' and is not guaranteed for to fit any custom
# workflows beyond its initial design

from pathlib import Path
import pandas as pd
import os
import re


class MassPikeProcessor:
    """Class for extracting, transforming, and loading data exported from MassPike."""

    def __init__(self, files: list|str, **kwargs) -> None:
        """
        Read and check all files passed in.
        :arg files:     (list or str)   MassPike files to be read in
        :arg ignore_headers:    (bool)  whether the headers should be checked for
                                        congruency
        """

        # if only one file, change to list
        if isinstance(files, str):
            files = [files]

        # if files pass check
        if self._check_files(files, **kwargs):
            self.files = files
            self.data = self._read_datafiles()
            self._format_data()

        return

    def __repr__(self) -> str:
        file_list = "\n".join(self.files)
        return f"""MassPikeProcessor constrcuted on files\n {file_list}"""

    def _check_files(self, files: list, **kwargs) -> bool:
        """Check filetype and incoming columns to ensure compatibility"""

        # check all file suffixes
        suffs = set([Path(file).suffix for file in files])
        if len(suffs)>1 or suffs!={".csv"}:
            raise ValueError("Not all filetypes are the expected type.")

        # if users pass "ignore_headers", all files read and concatenated
        ignore_headers = kwargs.get("ignore_headers", False)
        if ignore_headers:
            return True

        # else make sure all headers are the same
        valid_headers = self._check_headers(files)
        if not valid_headers:
            raise ValueError(
                """
                Parsing all files, we found the column names were not consistent.
                If this is on purpose, initialize MassPikeProcessor again with the
                "ignore_headers" flag
                """
            )

        return True

    def _check_headers(self, files: list) -> bool:
        """Iterates and reads files, checks to see if all columns are the same."""

        found_headers = None
        for file in files:
            # grab first few lines of file, collapse headers
            read_file = pd.read_csv(file)
            read_heads = sorted(read_file.columns.tolist())

            # check for header consistency
            if found_headers is None:
                found_headers = read_heads
            else:
                if found_headers != read_heads:
                    return False

        return True

    def _read_datafiles(self):
        """Read each datafile and instantiate dataframe."""

        df = pd.DataFrame()
        for file in self.files:
            _df = pd.read_csv(file)
            df = pd.concat([df, _df]).reset_index(drop=True)

        return df
    

    def _format_data(self):
        """Make custom edits to data."""

        # edit column names 
        columns = [c.lower().replace(" ", "_") for c in self.data.columns]

        # replace chars
        regs = [r"\&\#916\;", r"\#", r"[\+\.\\\/]"]
        repls = ["delta_", "num", ""]

        for i, column in enumerate(columns):
            for j, reg in enumerate(regs):
                column = re.sub(reg, repls[j], column)
            columns[i] = column
        
        self.data.columns = columns

        # remove all links
        columns = [c for c in columns if not re.search("link", c )]
        self.data = self.data[columns]

        return 
    
    def add_special_column(self, col_name: str, col_values: str|int|float|list):
        """
        Add new column to dataframe.
        
        :arg col_name:      (str)   name of new column
        :arg col_values:    (any)   values to be inserted in column
        """

        self.data.loc[:, col_name] = col_values

        return 
    
    def join_processors(self, new):
        """
        Add current second instance of MassPikeProcessor to current.
        
        :arg new:   (MassPikeProcessor) Second instance of MassPikeProcessor to
                                        be joined with current
        """

        self.data = pd.concat([self.data, new.data])
        # self.files.append(new.files)