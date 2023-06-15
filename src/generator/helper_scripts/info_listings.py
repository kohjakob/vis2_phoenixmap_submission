import csv

filtered_file = "Filtered_Listings.csv"
neighbourhood_column = "neighbourhood"

unique_neighbourhoods = set()

with open(filtered_file, "r", newline="", encoding='utf-8-sig', ) as file:
    reader = csv.DictReader(file)
    for row in reader:
        neighbourhood = row[neighbourhood_column]
        unique_neighbourhoods.add(neighbourhood)

num_unique_neighbourhoods = len(unique_neighbourhoods)

print("Number of unique neighbourhoods:", num_unique_neighbourhoods)
print("List of unique neighbourhoods:")
for neighbourhood in unique_neighbourhoods:
    print(neighbourhood)