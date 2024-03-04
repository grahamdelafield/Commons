import altair as alt 

alt_axis = alt.Axis(
    labelFontSize=14,
    labelFontWeight=600,
    labelFlush=False
)

nominal_axis = alt.Axis(
    labelAngle=0,
    labelFontSize=14,
    labelFontWeight=600,
    labelFlush=False
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

calico_colors = {
    "l_green":"#30BC5B",
    "d_green":"#28A049",
    "l_blue":"#38CCF7",
    "d_blue":"#05B5DD",
    "l_yellow":"#FFAA00",
    "d_yellow":"#FF8C00",
    "l_red":"#D31642",
    "d_red":"#B2143D",
    "l_gray":"#AAAAAA",
    "m_gray":"#6E6D6D",
    "d_gray":"#403C3C",
}

calico_light = {
    "l_green":"#30BC5B",
    "l_blue":"#38CCF7",
    "l_yellow":"#FFAA00",
    "l_red":"#D31642",
    "l_gray":"#AAAAAA",
}

calico_dark = {
    "d_green":"#28A049",
    "d_blue":"#05B5DD",
    "d_yellow":"#FF8C00",
    "d_red":"#B2143D",
    "d_gray":"#403C3C",
}