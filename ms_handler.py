import numpy as np
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt 
from scipy.ndimage import gaussian_filter
from scipy.signal import argrelextrema
from pyteomics import mass

def smooth_chrom(
    xs=[], ys=[], smooth_factor=1, source=None, filename=None, save_as=None
):
    """
    Function to smooth chromatogram from MS data.
    Values can either be read from

    :param xs: (array-like) x values from chromatogram
    :param ys: (array-like) y values from chromatogram
    :param source: (string) dictates from where the function should read data.
        None --> implies data is passed as an argument
        'clip' --> implies pandas should read data from clipboard
        'excel' --> implies pandas should read data from excel file
    """
    if source is None:
        asrt_text = "If no source is provided, data arrays must be passed as arguments"
        assert xs != [] and ys != [], asrt_text
    elif source == "clip":
        df = pd.read_clipboard()
    elif source == "excel":
        df = pd.read_excel(filename)
    else:
        assert xs is not None, "Found no valid X values"
        assert ys is not None, "Found no valid Y values"
    xs = df.iloc[3:, 0].astype(float)
    ys = df.iloc[3:, 1].astype(float)
    ys = gaussian_filter(ys, smooth_factor)
    plt.plot(xs, ys)
    plt.fill_between(xs, ys, alpha=0.3)
    if save_as:
        plt.savefig(save_as)


def plot_ms2_data(
    xs, ys, peptide, frag_dict, mods=None, show_error=False, tolerance=25
):
    """
    Function to return altair plot of identified fragments for a theoretical
    peptide.

    :param xs: (array) x/time data
    :param ys: (array) intensity data
    :param peptide: (string) peptide sequence
    :param frag_dict: (dict) output returned from data_processing.fragments func
    """
    # handle -endian order of data
    data = [xs, ys]
    for i, array in enumerate(data):
        if array.dtype.byteorder == ">":  # is big-endian
            data[i] = data[i].byteswap().newbyteorder()
    xs, ys = data

    df = pd.DataFrame(
        {"x": xs, "y": ys, "fragment": [None] * len(xs), "label": [""] * len(xs)}
    )

    if mods is not None:
        assert isinstance(mods, dict), "modifications must enter as dictionary"
        for k in mods:
            if not isinstance(mods[k], list):
                frag_dict[k] = list([mods[k]])
            else:
                frag_dict[k] = mods[k]

    dom = {
        "b": "#3b5bad",
        "y": "#c42e23",
        "HexHexNAc": "#3d8f2e",
        "NeuAc": "#3d8f2e",
        "NeuAc-18": "#3d8f2e",
        "HexNac": "#3d8f2e",
        "HexNac-18": "#3d8f2e",
        "HexNac-36": "#3d8f2e",
        "HexNac-fg": "#3d8f2e",
        "Hex": "#3d8f2e",
        "Hex-18": "#3d8f2e",
    }

    err_mass, err_dist, err_kind = [], [], []

    for k, v in frag_dict.items():
        for frag in v:
            nearest = find_nearest(df.x, frag)
            error = mass_error(frag, nearest)
            if abs(error) <= tolerance:
                err_mass.append(nearest)
                err_dist.append(error)
                err_kind.append(k)
                df.loc[(df.x == nearest), "fragment"] = k
                if k in ["b"]:
                    df.loc[(df.x == nearest), "label"] = k + f"{v.index(frag)+1}"
                elif k in ["y"]:
                    df.loc[(df.x == nearest), "label"] = (
                        k + f"{len(v) - v.index(frag)+1}"
                    )
                else:
                    df.loc[(df.x == nearest), "label"] = k

    df.dropna(inplace=True)
    df.loc[:, "y"] = df.y / np.max(df.y) * 100
    df["label position"] = df.y + 5

    bars = (
        alt.Chart(df)
        .mark_bar(size=2)
        .encode(
            x=alt.X("x", title="m/z", axis=alt.Axis(grid=False)),
            y=alt.Y(
                "y",
                title="Relative Abundance",
                axis=alt.Axis(grid=False, tickCount=1),
                scale=alt.Scale(domain=(0, 100)),
            ),
            color=alt.Color(
                "fragment",
                scale=alt.Scale(domain=list(dom.keys()), range=list(dom.values())),
                legend=None,
            ),
        )
        .properties(title=peptide, width=600)
    )

    text = (
        alt.Chart(df)
        .mark_text()
        .encode(y=alt.Y("label position"), x=alt.X("x"), text="label")
    )
    chart = alt.vconcat()
    chart &= alt.layer(bars, text)
    if show_error:
        err_df = pd.DataFrame({"mass": err_mass, "error": err_dist, "kind": err_kind})
        dots = (
            alt.Chart(err_df)
            .mark_circle()
            .encode(
                x=alt.X("mass:Q", title="m/z", axis=alt.Axis(grid=False)),
                y=alt.Y(
                    "error:Q",
                    title="error (ppm)",
                    axis=alt.Axis(grid=True, tickCount=3),
                    scale=alt.Scale(domain=(-tolerance, tolerance)),
                ),
                color=alt.Color(
                    "kind:O",
                    scale=alt.Scale(domain=list(dom.keys()), range=list(dom.values())),
                ),
            )
            .properties(height=100)
        )

        line = (
            alt.Chart(pd.DataFrame({"y": [0]}))
            .mark_rule(strokeDash=[10, 10])
            .encode(y="y")
        )

        chart &= dots + line
    return chart.configure_view(strokeWidth=0)


def fragments(peptide, types=("b", "y"), max_charge=1):
    """
    Function that returns theoretical fragments of peptide.
    Modeled from : https://pyteomics.readthedocs.io/en/latest/examples/example_msms.html

    :param peptide: (str) peptide sequence
    :param types: (tuple) types of fragments desired
    :param max_charge: (int) maximum charge state of fragment ions
    """
    d = {}
    for ion_type in types:
        d[ion_type] = []
        for i in range(1, len(peptide)):
            for charge in range(1, max_charge + 1):
                if ion_type[0] in "abc":
                    if i == 0:
                        continue
                    m = mass.fast_mass(peptide[:i], ion_type=ion_type, charge=charge)
                else:
                    m = mass.fast_mass(peptide[i:], ion_type=ion_type, charge=charge)
                d[ion_type].append(m)
    return d


def prof_to_cent(xs, ys):
    """
    Function to turn profile data to centroid.
    Collects relative maximums and uses indexes of those
    maximums to decipher xs and ys arrays.

    :param xs: (array) array of x data
    :param ys: (array) array of y data
    """
    idx = argrelextrema(ys, np.greater)
    xs, ys = xs[idx], ys[idx]
    return xs, ys


def mass_error(m1: float, m2: float):
    """
    Caluclates the ppm error between two masses.
    :arg m1:    (float) mass 1
    :arg m2:    (float) mass 2
    """

    diff = m1 - m2
    quot = diff / m1
    return quot * 1e6


def mass_tolerance(mass: float, ppm: int=20):
    """
    Returns the lower and upper values of a defined tolerance window.
    Windows have the defined width on either side of the specified mass.
    
    :arg mass:  (float) the mass of interest
    :arg ppm:   (float) the desired ppm on either side of the mass
    """
    val_arr = np.array([ppm, ppm * -1])
    
    val = (val_arr / 1e6) * mass - mass
    return val * -1


modifications = {
    "oxonium": {
        "Hex-36": 127.06,
        "HexNAc-fg": 138.05,
        "Hex": 163.06,
        "HexNAc-36": 168.09,
        "HexNAc-18": 186.09,
        "HexNAc": 204.09,
        "NeuAc-18": 274.09,
        "NeuAc": 292.08,
        "HexHexNAc": 366.14,
    }
}
