import altair as alt

alt_axis = alt.Axis(labelFontSize=14, labelFontWeight=600, labelFlush=False)

nominal_axis = alt.Axis(
    labelAngle=0, labelFontSize=14, labelFontWeight=600, labelFlush=False
)

alt_header = alt.Header(
    labelFontSize=14,
    labelFontWeight=600,
)

sci_min_axis = alt.Axis(
    grid=False,
    domainWidth=3,
    domainColor="#000000",
    tickColor="#000000",
    tickWidth=2,
    labelFontSize=14,
    labelFontWeight=600,
    labelFlush=False,
    offset=5
)

volcano_legend = alt.Legend(
    orient="bottom", direction="horizontal", labelFontWeight=600, labelFontSize=12
)

choice_colors = {
    "d_blue": "#2a385b",
    "m_blue": "#4f618e",
    "l_blue": "#6b7da8",
    "d_orange": "#af4a06",
    "m_orange": "#c6601b",
    "l_orange": "#f08137",
    "d_gray": "#575757",
    "m_gray": "#727272",
    "l_gray": "#999999",
}

choice_pallet = {
    'd_blue': '#2a385b',
    'l_blue': '#5c6684',
    'd_orange': '#af4a06',
    'l_orange': '#e08a4e',
    'd_green': '#6e9075',
    'l_green': '#a1c2a8',
    'l_gray': '#c2c2c2',
    'white': '#f2f2f2',
    'l_purple': '#a58891',
    'd_purple': '#785963',
    'd_gray': '#727272'
}

calico_colors = {
    "l_green": "#30BC5B",
    "d_green": "#28A049",
    "l_blue": "#38CCF7",
    "d_blue": "#05B5DD",
    "l_yellow": "#FFAA00",
    "d_yellow": "#FF8C00",
    "l_red": "#D31642",
    "d_red": "#B2143D",
    "l_gray": "#AAAAAA",
    "m_gray": "#6E6D6D",
    "d_gray": "#403C3C",
}

modified_calico = {
    "l_green": "#30BC5B",
    "d_green": "#249243",
    "l_blue": "#57d6fc",
    "d_blue": "#0497d1",
    "l_yellow": "#FFAA00",
    "d_yellow": "#dd7a00",
    "l_red": "#e6314c",
    "d_red": "#b21414",
    "l_gray": "#AAAAAA",
    "m_gray": "#6E6D6D",
    "d_gray": "#403C3C",
}

calico_light = {
    "l_green": "#30BC5B",
    "l_blue": "#38CCF7",
    "l_yellow": "#FFAA00",
    "l_red": "#D31642",
    "l_gray": "#AAAAAA",
}

calico_dark = {
    "d_green": "#28A049",
    "d_blue": "#05B5DD",
    "d_yellow": "#FF8C00",
    "d_red": "#B2143D",
    "d_gray": "#403C3C",
}

cal_palette = {
    'd_green': '#247343',
    'l_green': '#4ea16e',
    'd_blue': '#476c9b',
    'l_blue': '#6388b8',
    'd_red': '#983b3f',
    'l_red': '#b55356',
    'd_yellow': '#dba52c',
    'l_yellow': '#efc150',
    'd_gray': '#403C3C',
    'm_gray': '#6E6D6D',
    'l_gray': '#AAAAAA',
}

d3_colors = {
    "blue":"#1f77b4", # muted blue
    "organge":"#ff7f0e", # safety orange
    "green":"#2ca02c", # cooked asparagus green
    "red":"#d62728", # brick red
    "purple":"#9467bd", # muted purple
    "brown":"#8c564b", # chestnut brown
    "pink":"#e377c2", # raspberry yogurt pink
    "gray":"#7f7f7f", # middle gray
    "yellow":"#bcbd22", # curry yellow-green
    "light_blue":"#17becf", # blue-teal
}

tmt_channels = [
    "126",
    "127n", "127c",
    "128n", "128c",
    "129n", "129c",
    "130n", "130c",
    "131n", "131c",
    "132n", "132c",
    "133n", "133c",
    "134n", "134c",
    "135n"
]

# altair themes


def calico_theme(font):
    """
    Calico Theme Using Mark OT Font

    Usage:
    >>> alt.themes.register('markot', calico_theme)
    >>> alt.themes.enable('markot')
    """
    # font = "Mark OT"

    def theme_call():

        return {
            "config": {
                "title": {"font": font},
                "axis": {"labelFont": font, "titleFont": font},
            }
        }
    
    return theme_call
