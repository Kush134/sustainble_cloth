import json
import re
import requests
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pytesseract
from image_text import extract_textile
from PIL import Image
from email import charset
import matplotlib.pyplot as plt
from scipy import stats
from streamlit_lottie import st_lottie

#### Graphing requirements ####

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
        u_size = 40
        u_color = "#DD403A"
    else:
        u_size = 35
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
    vertline = alt.Chart(df).mark_rule(color="white").encode(x=alt.X("user:Q"))

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


#### Graphing requirements ####

dictionary = {
    "flax": "flax",
    "cotton": "cotton",
    "coton": "cotton",
    "wool": "wool",
    "viscose": "viscose",
    "polypropylene": "polypropylene",
    "polyester": "polyester",
    "acrylic": "acrylic",
    "nylon": "nylon",
    "hemp": "hemp",
}


def load_lottieurl(url: str):
    """Load a Lottie animation from a URL."""
    result = requests.get(url)
    if result.status_code != 200:
        return None
    return result.json()


lottie_fashion = load_lottieurl(
    "https://assets6.lottiefiles.com/packages/lf20_gn0tojcq.json"
)

st.title("🐙 Clothes for Good ")

st.write(
    "Show us a clothing tag and we will show you the environmental footprint of this purchase 🌵"
)


left_col, right_col = st.columns([1, 3])
with left_col:
    st.write("")
    st.write("")
    st.subheader("""Your compass for shopping clothes sustainably!""")

with right_col:
    st_lottie(lottie_fashion, speed=1, height=200, key=None)

st.subheader("Tell us more about this item 👑!")

col1, col2 = st.columns(2)

with col1:
    genre = st.radio(
        "What kind of clothing is it?",
        (
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
        ),
        horizontal=True,
    )

with col2:
    size = st.select_slider(
        "What is the size?",
        options=["Kids", "Small", "Medium", "Large", "Extra Large"],
    )

materials = {}

file = st.file_uploader("Upload a picture of the item", type=["png", "jpg", "jpeg"])
if file is not None:
    # To read image file buffer as a PIL Image:
    pytesseract.pytesseract.tesseract_cmd = r"/app/.apt/usr/bin/tesseract"
    img = Image.open(file, mode="r")
    processed_image = pytesseract.image_to_string(img)
    materials = extract_textile(processed_image, dictionary)

# Get the weight matrix
weight = pd.read_csv("cloth_type.csv", index_col=0) / 1000
# Get the material matrix
footprint = pd.read_csv("material_cost.csv", index_col=0)

# Get the specific weight of the clothing
if (genre is not None) & (size is not None):
    clothing_weight = weight.loc[genre, size]

# Get the specific footprint of the clothing
if len(materials) > 0:
    st.subheader("The clothes you uploaded has the following materials:")
    for material, percentage in materials.items():
        st.write(f"{material}: {percentage}%")

total_footprint = {"energy": 0, "co2": 0, "water": 0}
for mat, percent in materials.items():
    for cost_type in total_footprint.keys():
        total_footprint[cost_type] += round(
            clothing_weight * percent * footprint.loc[mat, cost_type]
        )
## just some fake number for figures

st.subheader("Here is the environmental footprint of your purchase 🌲🌳 ")
energy_chart, co2_chart, water_chart = plot_all(total_footprint, genre, df_average, dic_std)

col1, col2 = st.columns([1,4])
with col1:
    st.write(
        "A total of", total_footprint["energy"], f"killowat-hours went into making the {genre}."
    )
    if total_footprint["energy"] >= 18.5:
        st.write("The electricity used here can power and heat up an entire household for one week straight. 🏡")

with col2:
    st.altair_chart(energy_chart, use_container_width=True)



col1, col2 = st.columns([1,4])
with col1:
    st.write(
        f"Making the {genre} contributed to", total_footprint["co2"], f"kg of CO2 emission."
    )
    mileage = round(total_footprint["co2"] / 0.4)
    st.write("The CO2 emmited is equivalent to driving a car for", mileage, "miles. 🚗")
    if total_footprint["co2"] >= 222:
        st.write("You can save up to 3kg of CO2 here without this purchase!")
with col2:
    st.altair_chart(co2_chart, use_container_width=True)


col1, col2 = st.columns([1,4])
with col1:
    st.write(
        "A total of", total_footprint["water"], f"liters of water went into make the {genre}."
    )
    if total_footprint["water"] >= 689:
        st.write("The water used here can feed someone for more than a year. 🚰")
with col2:
    st.altair_chart(water_chart, use_container_width=True)