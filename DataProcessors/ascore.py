# the following code is intendecd for extraction, transformation, and loading
# data resulting from Ascore analysis, specifically throught the pyAscore CLI

# all code is provided 'as is' and is not guaranteed beyond its initial design

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import re
import typing
import logomaker

class AscoreParser:
    """Class used to ETL data output from pyAscore CLI"""

    def __init__(self, files: [str, list]) -> None:
        """
        Creates a new instance of AscoreParser.
        
        :arg files:  (str or list) file(s) to be parsed
        """
        if isinstance(files, str):
            files = [files]
        
        # run check to make sure file is of right type, return correct parser and delimiter
        all_files_pass = self._check_file_format(files)
        if all_files_pass:
            self._read_data(files)
            self._format_data()
        
        self.make_logo(self.data)

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
        Formats column names
        
        :arg data:  (pd.DataFrame) pandas dataframe with unformatted columns
        """
        formatted_frame = data.copy()
        new_columns = []

        columns = formatted_frame.columns 
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

        formatted_frame.columns = new_columns

        return formatted_frame

    def _format_data(self) -> None:
        """Formats columns within dataframe"""

        formatted_data = self.data.copy()

        # fill in missing positions
        formatted_data.loc[:, "alt_sites"] = formatted_data.alt_sites.fillna("")

        # turn tuples into positions
        formatted_data.loc[:, "alt_sites"] = formatted_data.apply(self.position_tuples, axis=1)

        # split scores
        formatted_data.loc[:, "ascores"] = formatted_data.astype(str)
        formatted_data.loc[:, "ascores"] = formatted_data.ascores.str.split(";")

        # explode dataframe based on sites and scores
        formatted_data = formatted_data.explode(["ascores", "alt_sites"])

        # reformat sites column
        formatted_data.loc[:, "alt_sites"] = formatted_data.alt_sites.map(lambda x: [pos for pos in x])

        # explode based on possible sites
        formatted_data = formatted_data.explode("alt_sites").reset_index(drop=True)


        # transform locations to peptides
        pos = formatted_data.apply(self.pos_to_symbol, axis=1, result_type="expand")
        pos.columns = ["mod_peptide", "trunc_peptide"]
        formatted_data = formatted_data.merge(pos, left_index=True, right_index=True)

        self.data = formatted_data

    def position_tuples(self, row: pd.Series) -> list:
        """
        Changes string positions to tuples of ints.
        
        :arg row:   (pd.Series) row of dataframe
        """
        # grab and split sites
        sites = row["alt_sites"]
        site_str = sites.split(";")

        # create new tuples
        new_info = []
        for group in site_str:
            group = group.split(",")

            # when no site was localized, there is an empty string
            # we put in a 0 for posterity
            group = [int(i) if i!="" else 0 for i in group]
            new_info.append(tuple(group))
            
        return new_info

    def pos_to_symbol(self, row: pd.Series, buffer_len=15) -> pd.DataFrame:
        """
        Adds hash (#) c-terminal to the localized position.

        :arg row:           (pd.Series) row of dataframe
        :arg buffer_len:    (int)   the expected length of all truncated sequences
        """
        # grab position of mod and sequence
        pos = row["alt_sites"] 
        seq = row["localized_sequence"]

        # remove any other mods found
        seq = re.sub(r"\[\d*\]", "", seq)

        # add hash to sequence
        mod_seq = seq[:pos] + "#" + seq[pos:]
        
        # create truncated sequence
        # the localized position will be the first amino acid
        trunc_seq = seq[pos-1:]
        trunc_seq = trunc_seq + "x"*(buffer_len-len(trunc_seq))

        return mod_seq, trunc_seq
    
    def make_logo(self, data: pd.DataFrame):
        logo_mat = logomaker.alignment_to_matrix(data.trunc_peptide)
        logo_mat = logo_mat.drop("x", axis=1)

        _, ax = plt.subplots(1, 1, figsize=(1, 3))
        tl = logomaker.Logo(
            logo_mat.iloc[0:1, :],
            color_scheme="weblogo_protein",
            ax=ax)
        tl.style_spines(visible=False)
        tl.style_spines(spines=['left', 'bottom'], visible=True)
        plt.show()

if __name__=="__main__":
    a = AscoreParser(r"/Users/delafield/code/python/pyascore_test/AcmMass/Shift_7104.tsv")
    print(a.data)