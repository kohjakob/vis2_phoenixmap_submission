"""
Streamlit page to display Phoenixmaps of parisian district "Bourse" generated from district border. Interactive display of different years.
"""
import streamlit as st
from streamlit_folium import st_folium
from st_pages import Page, show_pages
import os
import folium
import json

dir_path = os.path.dirname(__file__) + "/"
colors = ['blue', 'red', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'black', 'gray', 'pink', 'brown', 'lime', 'olive', 'teal', 'navy', 'salmon', 'gold', 'indigo', 'turquoise']

def load_year_polygons(colors):
       """
       Loads Phoenixmap polygon (from district border) for year range saved in folder (2009-2021).
       Function is NOT cached using st.cache_resource() to avoid reload problems.

       Parameters
       ----------
       colors: list(str)
              List of colors for the districts

       Returns
       ----------
       list(folium.Polygon)
              List of polygons to plot on map via .add_to(folium_map)
       """
       # Get files
       polygon_dir = os.path.join(dir_path, "ressources/polygons_bourse_year_district_borders/")
       polygon_dir_files = os.listdir(polygon_dir)
       polygon_dir_files.sort()

       year_polygons = []
       for i, (dir_file) in enumerate(polygon_dir_files):
              if (dir_file).endswith(".json"):
                     polygon_file = os.path.join(polygon_dir, (dir_file))
                     # Open files, create polygons
                     with open(polygon_file) as file:
                            polygon_data = json.load(file)
                            folium_polygon = folium.Polygon(locations=polygon_data, color=None, fill_color=colors[i], fill=True, fill_opacity=0.7, tooltip=dir_file[:-5])
                            year_polygons.append(folium_polygon)

       return year_polygons

st.set_page_config(
    page_title="Bourse by year (from district border)",
    page_icon="🔎",
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

col_1, col_2 = st.columns([1,5], gap="medium")
with col_1:
    show2010 = st.checkbox("2010", value=False)
    show2011 = st.checkbox("2011", value=False)
    show2012 = st.checkbox("2012", value=False)
    show2013 = st.checkbox("2013", value=True)
    show2014 = st.checkbox("2014", value=True)
    show2015 = st.checkbox("2015", value=False)
    show2016 = st.checkbox("2016", value=False)
    show2017 = st.checkbox("2017", value=False)
    show2018 = st.checkbox("2018", value=False)
    show2019 = st.checkbox("2019", value=False)
    years_to_show = [show2010, show2011, show2012, show2013, show2014, show2015, show2016, show2017, show2018, show2019, False, False]

with col_2:
    map = folium.Map(location=[48.86736, 2.358002], zoom_start=15.2)
    folium.TileLayer('cartodbpositron', control=False).add_to(map)
    
    year_polygons = load_year_polygons(colors)
    for i, (polygon) in enumerate(year_polygons):
            if years_to_show[i]:
                polygon.add_to(map)
                    
    st_folium(map, width=2000, height=920)

