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
    locations_df = pd.read_csv(input_file)

    # Create a dictionary to store clustered points
    clustered_points = defaultdict(list)

    # Iterate over each row in the DataFrame
    for index, row in locations_df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        tags = row['tags']
        street_name = row['street_name']
        street_counter = row['street_counter']

        # Check if this point is close enough to any existing cluster
        added_to_cluster = False
        for cluster_center, cluster_points in clustered_points.items():
            center_lat, center_lon, center_tags, center_street, center_street_counter = cluster_center

            # Calculate distance between the point and the cluster center
            distance = haversine_distance(lat, lon, center_lat, center_lon)

            # If within the threshold, add to the cluster
            if distance <= distance_threshold_km:
                cluster_points.append((lat, lon, tags, street_name, street_counter))
                added_to_cluster = True
                break

        # If not added to any existing cluster, start a new cluster
        if not added_to_cluster:
            clustered_points[(lat, lon, tags, street_name, street_counter)] = [(lat, lon, tags, street_name, street_counter)]

    # Create a folium map centered around the first location
    m = folium.Map(location=[locations_df['latitude'][0], locations_df['longitude'][0]], zoom_start=17)
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
              'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
    color_index = 0

    # Create a list to store the cleaned locations
    cleaned_locations = []

    # Iterate through each cluster and calculate median point
    for cluster_center, cluster_points in clustered_points.items():
        cluster_size = len(cluster_points)
        color_index = (color_index + 1) % len(colors)

        if cluster_size > 1:
            print(f"Cluster size: {cluster_size}")

            # find the point in cluster with the most street names
            max_street_counter = 0
            median_point = None
            min_distance = float('inf')

            for point in cluster_points:

                # Calculate mean latitude and longitude
                mean_lat = sum(p[0] for p in cluster_points) / cluster_size
                mean_lon = sum(p[1] for p in cluster_points) / cluster_size
                # now select the median point of the cluster
                # as the closest point to the mean

                # Add a marker to the map for the clustered point
                folium.Marker(location=[point[0], point[1]], icon=folium.Icon(color=colors[color_index]),
                              popup=f"Latitude: {point[0]}, Longitude: {point[1]}, {point[3]}").add_to(m)

                if point[4] > max_street_counter:
                    max_street_counter = point[4]
                    median_point = point
                    min_distance = haversine_distance(mean_lat, mean_lon, point[0], point[1])

                elif point[4] == max_street_counter:
                    distance = haversine_distance(mean_lat, mean_lon, point[0], point[1])
                    if distance < min_distance:
                        min_distance = distance
                        median_point = point

            # add to the median all the street names of the cluster avoiding duplicates and update the street_counter
            street_names = set()
            for point in cluster_points:
                street_names.update(point[3].split(', '))
            median_point = (median_point[0], median_point[1], median_point[2], ', '.join(street_names), len(street_names))


            # if no point has street_counter, then select the first point
            #if median_point is None:
            #    median_point = cluster_points[0]

            cleaned_locations.append(median_point)

        else:
            # If single point, retain as is
            cleaned_locations.append((cluster_center[0], cluster_center[1], cluster_center[2], cluster_center[3], cluster_center[4]))


    # Save the map to an HTML file
    output_file_map = "clusters.html"
    m.save(output_file_map)

    # Convert list of tuples to DataFrame
    cleaned_df = pd.DataFrame(cleaned_locations, columns=['latitude', 'longitude', 'tags', 'street_name', "street_counter"])

    # Write the cleaned DataFrame to a new CSV file without headers
    cleaned_df.to_csv(output_file, index=False)

    # Print the number of new locations
    print(f"Number of cleaned locations: {len(cleaned_locations)}")


def create_map(input_file):
    # Create a map centered around the first intersection node found, considering the header
    with open(input_file, 'r') as f:
        # skip the header
        next(f)
        first_location = next(f).split(',')

    m = folium.Map(location=[float(first_location[0]), float(first_location[1])], zoom_start=17)

    # Add orange markers for intersection nodes, with coordinates as marker description
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        # skip the header
        next(reader)
        for row in reader:
            folium.Marker(location=[float(row[0]), float(row[1])], icon=folium.Icon(color='orange'),
                            popup=f"Latitude: {row[0]}, Longitude: {row[1]}, Street Name: {row[3]}").add_to(m)

    # print the number of points in the map
    with open(input_file, 'r') as f:
        # skip the header
        next(f)
        locations = list(csv.reader(f))
        print(locations)
    print(f"Number of points: {len(locations)}")

    # compute and print the minimum distance between any two points
    min_distance = float('inf')
    for i in range(len(locations)):
        for j in range(i+1, len(locations)):
            distance = haversine_distance(float(locations[i][0]), float(locations[i][1]), float(locations[j][0]), float(locations[j][1]))
            if distance < min_distance:
                min_distance = distance
    print(f"Minimum distance between any two points: {min_distance:.3f} km")

    # color the points with minimum distance in the map with red
    for i in range(len(locations)):
        for j in range(i+1, len(locations)):
            distance = haversine_distance(float(locations[i][0]), float(locations[i][1]), float(locations[j][0]), float(locations[j][1]))
            if distance == min_distance:
                folium.Marker(location=[locations[i][0], locations[i][1]], icon=folium.Icon(color='red')).add_to(m)
                folium.Marker(location=[locations[j][0], locations[j][1]], icon=folium.Icon(color='red')).add_to(m)

    # Save the map to an HTML file
    output_file = "points_map_clustered.html"
    m.save(output_file)
    print(f"Map saved to {output_file}")


def complete_data(input_file_path):
    # read the csv file
    df = pd.read_csv(input_file_path)

    # replace the field street_name removing duplicates
    df['street_name'] = df['street_name'].apply(lambda x: ', '.join(list(set(x.split(', ')))))
    print(df['street_name'])

    # add a new field with the number of street names
    df['street_counter'] = df['street_name'].apply(lambda x: len(x.split(', ')))

    # remove all the rows with street_counter <= 1
    df = df[df['street_counter'] > 1]

    # save the new data to the same file
    df.to_csv(input_file_path, index=False)
    print("Data completed.")


if __name__ == '__main__':
    # Specify input and output file paths
    input_file_path = 'intersections.csv'
    output_file_path = 'intersections_clustered_with_tags.csv'

    # Specify the distance threshold for clustering in kilometers
    distance_threshold_km = 0.052  # Adjust this value based on your clustering requirements

    complete_data(input_file_path)

    # Call the function to cluster and clean the locations
    cluster_and_clean(input_file_path, output_file_path, distance_threshold_km)

    print("Cleaning complete. Results saved to intersections_clustered_with_tags.csv.")

    create_map(output_file_path)

