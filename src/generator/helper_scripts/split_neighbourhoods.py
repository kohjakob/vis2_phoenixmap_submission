import csv
import json

filtered_file = "Filtered_Listings.csv"
neighbourhood_column = "neighbourhood"
host_since_column = "host_since"
latitude_column = "latitude"
longitude_column = "longitude"

neighbourhood_data = {}

with open(filtered_file, "r", encoding='utf-8-sig', newline="") as file:
    reader = csv.DictReader(file)
    for row in reader:
        neighbourhood = row[neighbourhood_column]
        latitude = float(row[latitude_column])
        longitude = float(row[longitude_column])
        host_since = str(row[host_since_column])
        
        if neighbourhood not in neighbourhood_data:
            neighbourhood_data[neighbourhood] = []

        if row[host_since_column] != "":
            neighbourhood_data[neighbourhood].append({"latitude": latitude, "longitude": longitude, "host_since": host_since})

# Convert to JSON
json_data = json.dumps(neighbourhood_data, indent=4)

# Save JSON to a file
output_file = "neighbourhood_data.json"
with open(output_file, "w") as outfile:
    outfile.write(json_data)

print(f"Neighbourhood data saved to {output_file}.")
