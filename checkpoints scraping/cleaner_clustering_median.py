import pandas as pd
import math
import csv
import folium
from collections import defaultdict

R = 6371.0  # Earth radius in kilometers


def haversine_distance(lat1, lon1, lat2, lon2):
    # Calculate the Haversine distance between two points
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def cluster_and_clean(input_file, output_file, distance_threshold_km):
    # Read the locations CSV file into a DataFrame
    locations_df = pd.read_csv(input_file, header=None, names=['col1', 'col2'])

    # Create a dictionary to store clustered points
    clustered_points = defaultdict(list)

    # Iterate over each row in the DataFrame
    for index, row in locations_df.iterrows():
        lat = row['col1']
        lon = row['col2']

        # Check if this point is close enough to any existing cluster
        added_to_cluster = False
        for cluster_center, cluster_points in clustered_points.items():
            center_lat, center_lon = cluster_center

            # Calculate distance between the point and the cluster center
            distance = haversine_distance(lat, lon, center_lat, center_lon)

            # If within the threshold, add to the cluster
            if distance <= distance_threshold_km:
                cluster_points.append((lat, lon))
                added_to_cluster = True
                break

        # If not added to any existing cluster, start a new cluster
        if not added_to_cluster:
            clustered_points[(lat, lon)] = [(lat, lon)]

    # Create a folium map centered around the first location
    m = folium.Map(location=[locations_df['col1'][0], locations_df['col2'][0]], zoom_start=17)
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
              'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
    color_index = 0

    # Create a list to store the cleaned locations
    cleaned_locations = []

    # Iterate through each cluster and calculate median point
    for cluster_center, cluster_points in clustered_points.items():
        cluster_size = len(cluster_points)
        # HERE
        color_index = (color_index + 1) % len(colors)
        # print the color
        print(f"Color: {colors[color_index]}")

        if cluster_size > 1:
            print(f"Cluster size: {cluster_size}")
            # Calculate mean latitude and longitude
            mean_lat = sum(p[0] for p in cluster_points) / cluster_size
            mean_lon = sum(p[1] for p in cluster_points) / cluster_size
            # now select the median point of the cluster
            # as the closest point to the mean
            min_distance = float('inf')
            median_point = None
            for point in cluster_points:

                # Add a marker to the map for the clustered point
                folium.Marker(location=[point[0], point[1]], icon=folium.Icon(color=colors[color_index]),
                                popup=f"Latitude: {point[0]}, Longitude: {point[1]}").add_to(m)

                distance = haversine_distance(mean_lat, mean_lon, point[0], point[1])
                if distance < min_distance:
                    min_distance = distance
                    median_point = point
            cleaned_locations.append(median_point)

        else:
            # If single point, retain as is
            cleaned_locations.append((cluster_center[0], cluster_center[1]))


    # HERE Save the map to an HTML file
    output_file_map = "clusters.html"
    m.save(output_file_map)
    # HERE

    # Convert list of tuples to DataFrame
    cleaned_df = pd.DataFrame(cleaned_locations, columns=['Latitude', 'Longitude'])

    # Write the cleaned DataFrame to a new CSV file without headers
    cleaned_df.to_csv(output_file, index=False, header=False)

    # Print the number of new locations
    print(f"Number of cleaned locations: {len(cleaned_locations)}")


def create_map(input_file):
    # Create a map centered around the first intersection node found
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        first_location = next(reader)

    m = folium.Map(location=[float(first_location[0]), float(first_location[1])], zoom_start=17)

    # Add orange markers for intersection nodes, with coordinates as marker description
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            folium.Marker(location=[float(row[0]), float(row[1])], icon=folium.Icon(color='orange'),
                            popup=f"Latitude: {row[0]}, Longitude: {row[1]}").add_to(m)

    # print the number of points in the map
    with open(input_file, 'r') as f:
        locations = [tuple(map(float, row)) for row in csv.reader(f)]
    print(f"Number of points in the map: {len(locations)}")

    # compute and print the minimum distance between any two points
    min_distance = float('inf')
    for i in range(len(locations)):
        for j in range(i+1, len(locations)):
            distance = haversine_distance(locations[i][0], locations[i][1], locations[j][0], locations[j][1])
            if distance < min_distance:
                min_distance = distance
    print(f"Minimum distance between any two points: {min_distance:.3f} km")

    # color the points with minimum distance in the map with red
    for i in range(len(locations)):
        for j in range(i+1, len(locations)):
            distance = haversine_distance(locations[i][0], locations[i][1], locations[j][0], locations[j][1])
            if distance == min_distance:
                folium.Marker(location=[locations[i][0], locations[i][1]], icon=folium.Icon(color='red')).add_to(m)
                folium.Marker(location=[locations[j][0], locations[j][1]], icon=folium.Icon(color='red')).add_to(m)

    # Save the map to an HTML file
    output_file = "street_intersections_map_cleaned_clustered_median.html"
    m.save(output_file)
    print(f"Map saved to {output_file}")


if __name__ == '__main__':
    # Specify input and output file paths
    input_file_path = 'starting_locations_modified.csv'
    output_file_path = 'cleaned_clustered_median_locations.csv'

    # Specify the distance threshold for clustering in kilometers
    distance_threshold_km = 0.052  # Adjust this value based on your clustering requirements

    # Call the function to cluster and clean the locations
    cluster_and_clean(input_file_path, output_file_path, distance_threshold_km)

    print("Cleaning complete. Results saved to cleaned_clustered_locations.csv.")

    input_file = "cleaned_clustered_median_locations.csv"
    create_map(output_file_path)


    # 43.7188273,10.3905396
