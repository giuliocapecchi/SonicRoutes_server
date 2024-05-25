import folium
import csv

with open("locations_solved.csv", "r") as f:
    reader = csv.reader(f)
    index = 0
    for row in reader:
        if index == 0:
            m = folium.Map(location=[float(row[0]), float(row[1])], zoom_start=17)
        folium.Marker(location=[float(row[0]), float(row[1])], icon=folium.Icon(color='blue'),
                        popup=f"Latitude: {row[0]}, Longitude: {row[1]}").add_to(m)
        index += 1

    output_file = "locations_solved_map.html"
    m.save(output_file)
    print(f"Map saved to {output_file}")
    print(f"Number of points in the map: {index}")
