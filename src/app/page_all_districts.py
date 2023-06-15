"""
Streamlit page to display Phoenixmaps for all 20 parisian districts for user-selected year range. Optional display of district-wise sampled listings and heatmaps.
"""
import streamlit as st
from streamlit_folium import st_folium
from st_pages import Page, show_pages
from folium.plugins import HeatMap
import folium
import os
import json
import random

dir_path = os.path.dirname(__file__) + "/"
colors = ['blue', 'red', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'black', 'gray', 'pink', 'brown', 'lime', 'olive', 'teal', 'navy', 'salmon', 'gold', 'indigo', 'turquoise']

@st.cache_resource(show_spinner=False)
def load_district_polygons(lower_year, upper_year, colors):
       """
       Loads districts Phoenixmap polygons for year range defined by lower_year, upper_year in the defined colors.
       Function is cached using st.cache_resource().

       Parameters
       ----------
       lower_year : int
              Minimum year of listings incorporated into calculation of Phoenixmaps
       upper_year : int
              Maximum year of listings incorporated into calculation of Phoenixmaps
       colors: list(str)
              List of colors for the districts

       Returns
       ----------
       list(folium.Polygon)
              List of polygons to plot on map via .add_to(folium_map)
       """
       # Get files, sort alphabetically
       polygon_dir = os.path.join(dir_path, "ressources/polygons_{}_{}/".format(lower_year, upper_year))
       polygon_dir_files = os.listdir(polygon_dir)
       polygon_dir_files.sort()

       district_polygons = []
       for i, (dir_file) in enumerate(polygon_dir_files):
              if (dir_file).endswith(".json"):
                     polygon_file = os.path.join(polygon_dir, (dir_file))
                     # Open files, create polygons
                     with open(polygon_file) as file:
                            polygon_data = json.load(file)
                            if polygon_data != None:
                                   folium_polygon = folium.Polygon(locations=polygon_data, color=None, fill_color=colors[i], fill=True, fill_opacity=0.7)
                                   district_polygons.append(folium_polygon)

       return district_polygons

@st.cache_resource(show_spinner=False)
def load_tooltip_polygons(colors):
       """
       Loads districts Phoenixmap polygons for districts with respective district-name as tooltip in the defined (semi-transparent) colors.
       Function is cached using st.cache_resource().

       Parameters
       ----------
       colors: list(str)
              List of colors for the districts

       Returns
       ----------
       list(folium.Polygon)
              List of polygons to plot on map via .add_to(folium_map)
       """
       district_border_file = os.path.join(dir_path, "ressources/district_borders.json")

       district_border_polygons = []
       # Open file, sort alphabetically
       with open(district_border_file, "r") as file:
              districts_data = json.load(file)
              districts = list(districts_data.keys())
              districts.sort()

              # Create polygons
              for i, (district) in enumerate(districts):
                     district_polygon = []
                     for entry in districts_data[district]:
                            district_polygon.append(([entry["latitude"], entry["longitude"]]))
                     folium_polygon = folium.Polygon(locations=district_polygon, color=colors[i], fill=True, fill_opacity=0.1, tooltip=district, weight=0)
                     district_border_polygons.append(folium_polygon)

       return district_border_polygons


@st.cache_resource(show_spinner=False)
def load_district_heatmaps(districts_listings):
       """
       Loads districts Heatmaps for defined district_listings.
       Function is cached using st.cache_resource().

       Parameters
       ----------
       districts_listings: list(list(tuple(float, float)))
              List of list of district listings coordinates

       Returns
       ----------
       list(folium.plugins.HeatMap)
              List of Heatmaps to plot on map via .add_to(folium_map)
       """
       heatmaps = []
       for district in districts_listings:
              heatmaps.append(HeatMap(district, radius=13, max_zoom=14, blur=14))
       return heatmaps

@st.cache_resource(show_spinner=False)
def load_circle_markers(districts_listings, colors):
       """
       Loads CircleMarkers for defined district_listings.
       Function is cached using st.cache_resource().

       Parameters
       ----------
       districts_listings: list(list(tuple(float, float)))
              List of list of district listings coordinates
       colors: list(str)
              List of colors for the districts

       Returns
       ----------
       list(folium.plugins.CircleMarker)
              List of CircleMarkers to plot on map via .add_to(folium_map)
       """
       markers = []
       for i, (district) in enumerate(districts_listings):
              for house in district:
                     markers.append(folium.CircleMarker(location=house, radius=2, color=colors[i]))
       return markers

@st.cache_resource(show_spinner=False)
def load_listings_sample(lower_year, upper_year, sample_size):
       """
       Loads sample-sized district listing locations for year range defined by lower_year, upper_year in the defined colors.
       Function is cached using st.cache_resource().

       Parameters
       ----------
       lower_year : int
              Minimum year of listings incorporated into calculation of Phoenixmaps
       upper_year : int
              Maximum year of listings incorporated into calculation of Phoenixmaps
       sample_size: int
              Size of sample


       Returns
       ----------
       list(list(tuple(float, float)))
              List of list of district listings coordinates
       """
       district_listings_file = os.path.join(dir_path, "ressources/district_listings.json")

       districts_listings = []
       # Open file, sort alphabetically
       with open(district_listings_file, "r") as read_file:
              data = json.load(read_file)
              districts = list(data.keys())
              districts.sort()

              # Create listings
              for district in districts:
                     district_listing = []
                     houses = data[district]
                     for house in houses:
                            if lower_year <= int(house["host_since"][:4]) <= upper_year: 
                                   district_listing.append([house["latitude"], house["longitude"]])
                     districts_listings.append(random.sample(district_listing, min(sample_size, len(district_listing))))
       return districts_listings

st.set_page_config(
    page_title="Paris districts",
    page_icon="🥐",
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
       lower_year, upper_year = st.select_slider('Select a range of years', options=[2009, 2013, 2017, 2021], value=(2009, 2021))
       if(lower_year > upper_year):
              a = lower_year
              lower_year = upper_year
              upper_year = a

       show_heatmap = st.checkbox('Show Heatmaps', value=False)
       show_circle_markers = st.checkbox('Show Listings (20 sampled per district)', value=False)

with col_2:
       map = folium.Map(location=[48.8586, 2.389002], zoom_start=12.5)
       folium.TileLayer('cartodbpositron', control=False).add_to(map)

       marker_listings_samples = load_listings_sample(lower_year, upper_year, 20)
       circle_markers = load_circle_markers(marker_listings_samples, colors)
       if show_circle_markers:
              for circle_marker in circle_markers:
                     circle_marker.add_to(map)

       heatmap_listings_samples = load_listings_sample(lower_year, upper_year, 1000)
       heatmaps = load_district_heatmaps(heatmap_listings_samples)
       if show_heatmap:
              for show_heatmap in heatmaps:
                     show_heatmap.add_to(map)

       outline_polygons = load_district_polygons(lower_year, upper_year, colors)
       for polygon in outline_polygons:
              polygon.add_to(map)

       tooltip_polygons = load_tooltip_polygons(colors)
       for polygon in tooltip_polygons:
              polygon.add_to(map)

       st_folium(map, width=2000, height=920)
