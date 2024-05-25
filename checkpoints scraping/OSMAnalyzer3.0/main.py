import osmium
import csv
import subprocess
from collections import defaultdict


class IntersectionHandler(osmium.SimpleHandler):
    def __init__(self, output_csv):
        super(IntersectionHandler, self).__init__()
        self.output_csv = output_csv
        self.csv_writer = csv.writer(output_csv)
        self.intersections = defaultdict(list)
        self.header_written = False  # Track if header has been written

    def way(self, w):
        if 'highway' in w.tags and not w.is_closed() and len(w.nodes) > 1:
            if self.is_car_accessible(w):
                tags_dict = dict(w.tags)
                street_name = tags_dict.get('name', 'N/A')
                for node_ref in w.nodes:
                    self.intersections[node_ref.ref].append((node_ref.location.lat, node_ref.location.lon, tags_dict, street_name))

    def is_car_accessible(self, way):
        car_accessible_tags = ['primary', 'secondary', 'tertiary', 'unclassified', 'residential']
        return any(tag in way.tags.get('highway', '') for tag in car_accessible_tags)

    def finalize_intersections(self):
        # Write header row if not already written
        if not self.header_written:
            self.csv_writer.writerow(['latitude', 'longitude', 'tags', 'street_name'])
            self.header_written = True

        intersection_count = 0
        for node_ref, locations in self.intersections.items():
            if len(locations) > 1:  # Only consider nodes with multiple streets (intersections)
                lat, lon, tags, street_names = zip(*locations)
                self.csv_writer.writerow([lat[0], lon[0], tags[0], ', '.join(street_names)])
                intersection_count += 1
        print(f"Found {intersection_count} intersections.")

if __name__ == '__main__':
    input_osm_file = 'map_pisa.osm'  # Replace with your OSM file path
    output_csv_file = 'intersections.csv'  # Output CSV file path

    with open(output_csv_file, 'w', newline='', encoding='utf-8') as output_csv:
        handler = IntersectionHandler(output_csv)
        handler.apply_file(input_osm_file, locations=True)
        handler.finalize_intersections()

    print(f"Intersection extraction completed. Results saved to '{output_csv_file}'.")

    subprocess.run(["python", "mapper.py"])

    subprocess.run(["python", "clustering.py"])

    subprocess.run(["python", "csv_cleaner.py"])
