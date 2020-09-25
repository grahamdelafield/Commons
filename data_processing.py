import pandas as pd 
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

def smooth_chrom(xs=[], ys=[], smooth_factor=1, source=None, filename=None, save_as=None):
    '''
    Function to smooth chromatogram from MS data.
    Values can either be read from 
    
    :param xs: (array-like) x values from chromatogram
    :param ys: (array-like) y values from chromatogram
    :param source: (string) dictates from where the function should read data.
        None --> implies data is passed as an argument
        'clip' --> implies pandas should read data from clipboard
        'excel' --> implies pandas should read data from excel file 
    '''
    if source is None:
        asrt_text = 'If no source is provided, data arrays must be passed as arguments'
        assert xs != [] and ys != [], asrt_text
    elif source=='clip':
        df = pd.read_clipboard()
    elif source=='excel':
        df = pd.read_excel(filename)
    xs = df.iloc[3:, 0].astype(float)
    ys = df.iloc[3:, 1].astype(float)
    ys = gaussian_filter(ys, smooth_factor)
    plt.plot(xs, ys)
    plt.fill_between(xs, ys, alpha=0.3)
    if save_as:
        plt.savefig(save_as)