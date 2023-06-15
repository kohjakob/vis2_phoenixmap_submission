"""
Streamlit page with brief project intro and explainer graphic.
"""
import streamlit as st
import os
from PIL import Image
from st_pages import Page, show_pages

dir_path = os.path.dirname(__file__) + "/"

st.set_page_config(
    page_title="Explainer",
    page_icon="👋",
    layout="wide",
)
show_pages(
    [
        Page(os.path.join(dir_path, "page_intro.py"), "Explainer", "👋"),
        Page(os.path.join(dir_path, "page_all_districts.py"), "Paris districts", "🥐"),
        Page(os.path.join(dir_path, "page_bourse_convex_hull.py"), "Bourse by year (from convex hull)", "🔎"),
        Page(os.path.join(dir_path, "page_bourse_district_borders.py"), "Bourse by year (from district border)", "🔎"),
    ]
)

st.title("Phoenixmap")

st.write("This demo is an implementation of a 2D spatial distribution visualization based on \"Phoenixmap\" [1]. \
        Phoenixmap is a 2D visualization approach applicable for spatio-temporal distributions. It differs from classical approaches like Heatmaps especially in allowing \
        visualizing multiple categories of data in the same space.")

image = Image.open(os.path.join(dir_path, "ressources/construction_explainer.png"))
st.image(image, caption='Short explainer on the construction of Phoenixmap')

st.divider()
st.write("[1] Zhao et. al, \"Phoenixmap: An Abstract Approach to Visualize 2D Spatial Distributions\", 2020 (https://arxiv.org/abs/2002.00732)")
