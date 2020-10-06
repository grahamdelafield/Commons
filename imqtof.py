import sys
import csv
import ntpath
import pandas as pd
import altair as alt



class IMQCsv:

    def __init__(self, filename, chrom_data=False, samples=None):
        assert filename.endswith('.csv'), 'Class IMQCsv only accepts .csv files'
        self.file = filename
        if chrom_data:
            self.data = self._read_chrom(samples)
            return
        self.data = self._read_file()
        return

    def __repr__(self):
        text = (f'IMQCsv object instantiated on file {self.file}. Methods ' + 
               f'within are built to work with tabular (.csv) data exported ' +
               f'from Agilent 6560.')
        return text

    def _read_file(self):
        return pd.read_csv(self.file)
    
    def feat_to_inclusion(self, columns=None, ce=35, drt=0.5, 
                          iso_width='narrow'):
        '''
        Function to transform feature list .csv file into a targeted MS2
        inclusion list.

        attrs:
            - columns (list): Columns available to construct ['On', 'Prec. m/z',
                              'Z','Ret. Time (min)', 'Delta Ret. Time (min)',
                              'Iso. Width','Collision Energy',
                              'Acquisition Time (ms/spec)'] 
            - ce (int): Colision energy to be used during MS2.
            - drt (float): Delta retention time. 
            iso_width (str): Isolation width to be used in selection. Options 
                             are ['wide', 'medium', 'narrow']
        '''
        iso_map = {'narrow':'Narrow (~1.3 m/z)'}

        df = self.data
        mz = df["m/z"]
        z = df["Z"]
        rt = df["RT"]
        drt = [drt] * len(df)
        ce = [ce] * len(df)
        iso_w = [iso_map[iso_width]] * len(df)
        
        ordered_data = [mz, z, rt, drt, ce, iso_w]
        columns = ['Prec. m/z', 'Z', 'Ret. Time (min)',
                   'Delta Ret. Time (min)', 'Collision Energy',
                   'Iso. Width']

        out_name = "".join(self.file.split(".")[:-1])
        out_name = out_name + "_Inclusion.csv"

        new_df = pd.DataFrame(dict(zip(columns, ordered_data)))
        new_df.to_csv(out_name, index=False)

    def _create_frame(self, sample, times, ints):
        samples = [sample] * len(times)
        df = pd.DataFrame({
            "Sample":samples,
            "Times":times,
            "Intensity":ints
        })
        return df

    def _make_chart(self, df, name):
        line = alt.Chart(df).mark_line().encode(
            x=alt.X("Times:Q", title="Time (min)"),
            y=alt.Y("Intensity:Q", title="Intensity (counts)"),
            color="Sample:O"
            ).properties(width=800, title=name)
        return line

    def _read_chrom(self, samples):
        with open(self.file, 'r') as f:
            res = []
            contents = f.read()
            contents = contents.replace('\x00', '')
            contents = contents.split('\n')
            d = []
            for c in contents:
                if c.startswith('#'):
                    if d == []:
                        pass
                    else:
                        res.append(d)    
                elif c == '':
                    continue
                else:
                    d.append(c)
            res.append(d)

        df = pd.DataFrame()
        for i, sample in enumerate(samples):
            data = res[i]
            data = [d.split(',') for d in data]
            points = [t[0] for t in data]
            time = [t[1] for t in data]
            intens = [t[2] for t in data]
            names = [sample]*len(data)
            if df.empty:
                df = pd.DataFrame({
                    'Sample':names,
                    'idx':points,
                    'Time':time,
                    'Intensity':intens
                })
            else:
                sub = pd.DataFrame({
                    'Sample':names,
                    'idx':points,
                    'Time':time,
                    'Intensity':intens
                })
                df = pd.concat([df, sub])
        return df

    def chrom_to_plot(self, ext=".png", use_cwd=False):
        names, times, ys =  [], [], []

        with open(self.file, "r", encoding="utf-8") as file:
            r = csv.reader(file)
            for i, row in enumerate(r):
                if row[0].startswith('#') and row[0].endswith(".d"):
                    names.append(row)
                    mins, ints = [], []
                elif row[0].startswith('#') and not row[0].endswith(".d"):
                    continue
                elif row[0] != "":
                    mins.append(row[1])
                    ints.append(row[2])
                if row[0] == "":
                    times.append(mins)
                    ys.append(ints)
            times.append(mins)
            ys.append(ints)

        charts = []
        for i, time_l in enumerate(times):
            name = input(f"Give name for sample{names[i][0]}:\t")
            df = self._create_frame(name, time_l, ys[i])

            chart = self._make_chart(df, name)
            charts.append(chart)

        if use_cwd:
            out_name = ntpath.basename(self.file)
            out_name = ''.join(out_name.split('.')[:-1])
        else:
            out_name = "".join(self.file.split(".")[:-1])
        out_name = out_name + '_Chromatogram' + ext


        alt.vconcat(*charts).save(out_name)
        


