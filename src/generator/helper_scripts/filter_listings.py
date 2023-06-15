import csv

#From the cols in Listings.csv, we are interested in:
#listing_id,name,host_since,neighbourhood,district,city,latitude,longitude
original_file = "Listings.csv"
filtered_file = "Filtered_Listings.csv"
columns_to_keep = ["neighbourhood", "host_since", "latitude", "longitude"]

with open(original_file, "r", encoding='utf-8-sig', newline="") as infile, open(filtered_file, "w", newline="", encoding='utf-8-sig') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=columns_to_keep)
    
    writer.writeheader()  # Write the header with the selected columns
    
    for row in reader:
        if row["city"] == "Paris":
            filtered_row = {col: row[col] for col in columns_to_keep}
            writer.writerow(filtered_row)
