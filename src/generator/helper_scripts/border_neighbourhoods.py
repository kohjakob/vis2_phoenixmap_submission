import json
import geopandas as gpd


neighbourhood_data = {}

shapefile_path = "arrondissements.shp"
data = gpd.read_file(shapefile_path)
district_border_polygon_coords = []
for geometry, district_name in zip(data['geometry'], data["l_aroff"]):
    if geometry.geom_type == 'Polygon':
        district_border_polygon_coords.append(list(geometry.exterior.coords))

for polygon, district_name in zip(district_border_polygon_coords, data["l_aroff"]):
    border_points = []
    for entry in polygon:
        border_points.append({"latitude": entry[1], "longitude": entry[0]})
    neighbourhood_data[district_name] = border_points

json_data = json.dumps(neighbourhood_data, indent=4)

# Save JSON to a file
output_file = "neighbourhood_borders.json"
with open(output_file, "w") as outfile:
    outfile.write(json_data)