import altair as alt
import vega



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


def graham_altair_theme():
    markColor = "#5c6684"  # blue, fifth color from category palette
    strokeColor = "#403C3C"
    axisColor = "#000000"
    backgroundColor = "#FFFFFF"
    font = "Open Sans"
    labelFont = "Open Sans"
    sourceFont = "Open Sans"
    gridColor = "#DEDDDD"
    
    # Okabe Ito colorblindsafe palette
    # https://thenode.biologists.com/data-visualization-with-flying-colors/research/
    category_palette = [
            # '#2a385b',
            '#5c6684',
            # '#af4a06',
            '#e08a4e',
            '#6e9075',
            # '#a1c2a8',
            # '#c2c2c2',
            # '#f2f2f2',
            # '#a58891',
            '#785963',
            '#727272'
                   ]
    sequential_palette = [        
            '#5c6684',
            "#c2c2c2",
            '#e08a4e',
                         ],
    return {
        "width": 450,
        "height": 200,   
        "config": {
            "title": {
                "anchor": "start",
                "dy": -15,
                "fontSize": 18,
                "font": font,
                "fontColor": "#000000"
            },
            "axisX": {
               "domain": True,
               "domainColor": axisColor,
               "domainWidth": 2,
               "offset":2,
               "grid": False,
               "labelFontSize": 12,
               "labelFont": labelFont,
               "labelAngle": 0,
               "labelOverlap": "parity",
               "labelFontWeight":600,
               "tickColor": axisColor,
               "tickWidth":2,
               "tickSize": 5,
               "titleFontSize": 14,
               "titlePadding": 10,
               "titleFont": font,
            #    "title": "",
                "labelFlush":False
           },
           "axisY": {
               "domain": False,
               "domainWidth":2,
               "domainColor":axisColor,
            #    "offset":5,
               "grid": True,
               "gridColor": gridColor,
               "gridWidth": 1,
               "labelFontSize": 12,
               "labelFont": labelFont,
               "labelFontWeight":600,
               "labelPadding": 8,
               "tickColor":axisColor,
               "ticks":False,
               "tickWidth":2,
               "tickSize":5,
            #    "titleAlign": "left",
            #    "titleAnchor": "start",
               "titleFontSize": 14,
               "titlePadding": 10,
               "titleFont": font,
            #    "titleAngle": 0,
            #    "titleY": -15,
            #    "titleX": 18,
           },
           "background": backgroundColor,
           "legend": {
               "labelFontSize": 12,
               "labelFontWeight":600,
               "labelFont": labelFont,
               "symbolSize": 100,
               "symbolType": "square",
               "titleFontSize": 12,
               "titlePadding": 10,
               "titleFont": font,
               "title": "",
            #    "orient": "top-right",
            #    "offset": 5,
               "fillColor":"#FFFFFF",
               "strokeColor":"#000000",
               "strokeDash":[8,4],
               "padding":5
           },
           "view": {
               "stroke": "transparent",
           },
           "range": {
               "category": category_palette,
               "diverging": sequential_palette
           },
           "area": {
               "fill": markColor,
           },
           "line": {
               "color": markColor,
               "stroke": markColor,
               "strokewidth": 5,
           },
           "trail": {
               "color": markColor,
               "stroke": markColor,
               "strokeWidth": 0,
               "size": 1,
           },
           "path": {
               "stroke": markColor,
               "strokeWidth": 0.5,
           },
           "point": {
               "filled": True,
               "opacity":1,
               "stroke":markColor,
               "fill":"#FFFFFF"
           },
           "text": {
               "font": sourceFont,
               "color": markColor,
               "fontSize": 11,
               "align": "right",
               "fontWeight": 400,
               "size": 11,
           }, 
           "bar": {
                "fill": markColor,
                "stroke": strokeColor,
            }, 
       },
    }
