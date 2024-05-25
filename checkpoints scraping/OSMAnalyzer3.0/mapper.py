import folium
import pandas as pd

def plot_points_on_map(csv_file):
    # Read CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Create a map centered around the first point in the DataFrame
    if not df.empty:
        map_center = [df.iloc[0]['latitude'], df.iloc[0]['longitude']]
    else:
        map_center = [0, 0]  # Default center if DataFrame is empty

    map_osm = folium.Map(location=map_center, zoom_start=17)  # Initialize map

    # Iterate over DataFrame rows and add markers for each point
    for index, row in df.iterrows():
        # Extract latitude, longitude, and tags
        lat = row['latitude']
        lon = row['longitude']
        tags = row['tags']

        # Create popup HTML content with tags information
        popup_html = f"<b>Latitude:</b> {lat}<br><b>Longitude:</b> {lon}<br><b>Tags:</b><br>{tags}"

        # Add marker to the map
        folium.Marker([lat, lon], popup=folium.Popup(popup_html, max_width=300)).add_to(map_osm)

    # Save the map to an HTML file
    map_osm.save("points_map.html")

    print("Map created and saved to 'points_map.html'. Open this file in a web browser to view the map.")

if __name__ == '__main__':
    csv_file_path = 'intersections.csv'  # Path to the CSV file produced earlier

    # Plot points on map using Folium
    plot_points_on_map(csv_file_path)

    # launch an external script named mapper.py
    # subprocess.run(["python", "mapper.py"])
