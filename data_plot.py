import re
import random
import matplotlib.pyplot as plt
import numpy as np
import altair as alt
import pandas as pd
from scipy import stats


def making_fake_data(avg, std, etype):
    fake_data = np.random.normal(avg, std, 1000)
    df = pd.DataFrame({etype: fake_data})
    return df


def df_usr(user_cost, avg, std, etype):
    df = making_fake_data(avg, std, etype)
    df.iloc[-1] = user_cost
    df["user"] = user_cost
    return df


def type_value(etype):
    if etype == "water":
        color = "#35A7FF"
        vtline = 0.0015
        devi = 300
        uni = "L"
    elif etype == "co2":
        color = "#FFD25A"
        vtline = 0.07
        devi = 10
        uni = "Kg"
    else:
        color = "#F7717D"
        vtline = 0.03
        devi = 20
        uni = "kWh"
    return color, vtline, devi, uni


def make_density(user_cost, avg, std, etype):
    df = df_usr(user_cost, avg, std, etype)
    pct = round(stats.percentileofscore(df[etype], user_cost, "weak"), 3)
    color0, vtline, devi, uni = type_value(etype)
    if pct > 50:
        u_size = 35
        u_color = "#DD403A"
    else:
        u_size = 30
        u_color = "#3D348B"
    # make plot
    base = (
        alt.Chart(df)
        .transform_density(
            etype,
            as_=[etype, "density"],
        )
        .mark_area(color=color0, opacity=0.5)
        .encode(
            x=alt.X(f"{etype}:Q", axis=alt.Axis(title=f"{etype} waste ({uni})")),
            y="density:Q",
        )
    )
    vertline = alt.Chart(df).mark_rule(color='white').encode(x=alt.X("user:Q"))

    text = (
        alt.Chart()
        .mark_text(text=str(pct) + "%", dx=10, dy=0, size=u_size, color=u_color)
        .encode(x=alt.datum(user_cost + devi), y=alt.datum(vtline))
    )

    chart = (
        alt.layer(base, vertline, text, data=df)
        .transform_calculate(user=str(user_cost))
        .configure_view(stroke="transparent")
        .configure_view(strokeOpacity=0)
        .configure_axis(labelFontSize=10, titleFontSize=18, grid=False)
    )
    return chart


def plot_all(
    user_cost, cloth_type, df_average, dic_std
):  # input dict, add size, and type
    chart_list = []
    for etype in ["energy", "co2", "water"]:
        avg = df_average.loc[cloth_type, etype]
        std = dic_std[etype]
        chart = make_density(user_cost[etype], avg, std, etype)
        chart_list.append(chart)
    return chart_list


# making average for simulated data
df_average = pd.DataFrame(
    {
        "energy": [15.47, 16.2, 18.5, 31.5, 28, 1.9, 7, 21, 7, 0.5],
        "water": [65, 338, 222, 585, 520, 35.75, 130, 390, 130, 8.77],
        "co2": [1.95, 7.8, 6.67, 13.5, 12, 0.8, 3, 9, 3, 0.2],
    },
    index=[
        "T-Shirt",
        "Sweatshirt",
        "Sweater",
        "Jacket",
        "Blazer",
        "Underwear",
        "Dress",
        "Pants",
        "Shorts",
        "Socks",
    ],
)
# making std for simulated data
dic_std = {"energy": 12, "co2": 5, "water": 200}


def main_plot():
    # test_user_cost= {"energy": 14, "co2": 6, "water": 120}
    charts = plot_all(
        {"energy": 14, "co2": 6, "water": 120}, "T-Shirt", df_average, dic_std
    )
    return charts


c = main_plot()
