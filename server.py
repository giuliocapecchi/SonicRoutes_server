import os
import json
import math
import pandas as pd
import networkx as nx
import xml.etree.ElementTree as ET
import csv
import requests
from flask import Flask, request, jsonify
import config

app = Flask(__name__)
GOOGLE_MAPS_API_URL = 'https://roads.googleapis.com/v1/snapToRoads'
GOOGLE_MAPS_API_KEY = config.api_key

@app.route('/getRoute', methods=['POST'])
def computeRoute():
    if request.is_json:
        data = request.get_json()
        #print(data)
        mindist = -1.0
        minIndex1 = 0
        checkpoints = pd.read_csv('data/pisa.csv')
        for index, checkpoint in checkpoints.iterrows():
            if mindist == -1.0:
                mindist = haversine(data['point1']['latitude'], data['point1']['longitude'], checkpoint['latitude'], checkpoint['longitude'])
            else:
                if haversine(data['point1']['latitude'], data['point1']['longitude'], checkpoint['latitude'], checkpoint['longitude']) < mindist:
                    mindist = haversine(data['point1']['latitude'], data['point1']['longitude'], checkpoint['latitude'], checkpoint['longitude'])
                    minIndex1 = checkpoint['index']

        mindist2 = -1.0
        minIndex2 = 0
        for _, checkpoint in checkpoints.iterrows():
            if mindist2 == -1.0:
                mindist2 = haversine(data['point2']['latitude'], data['point2']['longitude'], checkpoint['latitude'], checkpoint['longitude'])
            else:
                if haversine(data['point2']['latitude'], data['point2']['longitude'], checkpoint['latitude'], checkpoint['longitude']) < mindist2:
                    mindist2 = haversine(data['point2']['latitude'], data['point2']['longitude'], checkpoint['latitude'], checkpoint['longitude'])
                    minIndex2 = checkpoint['index']

        path = find_best_path('data/grafo_completo.graphml', minIndex1, minIndex2)
        path.insert(0,(data['point1']['latitude'], data['point1']['longitude']))
    
        #print(path)
        
        return jsonify({"path": path}), 200
    else:
        return jsonify({"error": "Request body must be JSON"}), 400

def heuristic_euclidean_distance(node1, node2, graph):
    x1, y1 = graph.nodes[node1]['latitude'], graph.nodes[node1]['longitude']
    x2, y2 = graph.nodes[node2]['latitude'], graph.nodes[node2]['longitude']
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def find_best_path(graph_file, start_node_id, end_node_id):
    graph = build_graph(graph_file)
    heuristic = lambda u, v: heuristic_euclidean_distance(u, v, graph)
    best_path_ids = nx.astar_path(graph, start_node_id, end_node_id, heuristic=heuristic, weight='weight')
    best_path_coords = [(graph.nodes[node]['latitude'], graph.nodes[node]['longitude']) for node in best_path_ids]
    return best_path_coords


@app.route('/getCrossingCoordinates/<int:crossing_id>', methods=['GET'])
def get_crossing(crossing_id):
    checkpoints = pd.read_csv('data/pisa.csv')
    crossing = checkpoints.loc[checkpoints['index'] == crossing_id]
    if not crossing.empty:
        latitude = crossing['latitude'].values[0]
        longitude = crossing['longitude'].values[0]
        return jsonify({"crossing_id": crossing_id, "latitude": latitude, "longitude": longitude}), 200
    else:
        return jsonify({"error": "Crossing not found"}), 404


@app.route('/getCrossings/<string:city>', methods=['GET'])
def get_crossings(city):
    city = city.lower()
    csv_file = 'data/' + city + '.csv'
    if not os.path.exists(csv_file):
        return jsonify({"error": "CSV file not found"}), 404

    crossings = pd.read_csv(csv_file)
    if not crossings.empty:
        crossing_list = []
        for _, crossing in crossings.iterrows():
            crossing_id = crossing['index']
            latitude = crossing['latitude']
            longitude = crossing['longitude']
            streetNames = [name.strip() for name in crossing['street_name'].split(";")] if crossing['street_name'] else []
            crossing_data = {
                "id": crossing_id,
                "coordinates": {"latitude": latitude, "longitude": longitude},
                "streetNames": streetNames
            }
            crossing_list.append(crossing_data)
        return jsonify({"crossings": crossing_list}), 200
    else:
        return jsonify({"error": "No crossings found for the specified city"}), 404



@app.route('/upload', methods=['POST'])
def upload_json():
    if request.is_json:
        data = request.get_json()
        """
        data is flowing in the following format
        {'endCrossingId': 43, 'measurements': 28, 'amplitude': 196.0, 'startCrossingId': 22}
        """

        graphml_file_path = 'data/grafo_completo.graphml'
        # Aggiorna il file GraphML
        update_graphml(data ,graphml_file_path)

        return jsonify({"message": "Data saved successfully"}), 200
    else:
        return jsonify({"error": "Request body must be JSON"}), 400


def update_graphml(data, file_path='data/grafo_completo.graphml'):
    tree = ET.parse(file_path)
    root = tree.getroot()
    remove_namespace(root)

    start_id = data['startCrossingId']
    end_id = data['endCrossingId']
    amplitude = data['amplitude']
    numberOfMeasurements = data['measurements']
    amplitude = amplitude / numberOfMeasurements  # Calcolo dell'ampiezza media
    #print(start_id, end_id)

    updated = False

    print("start_id : ", start_id,"\n end_id : ", end_id)

    for edge in root.findall('.//edge'):
        if (edge.get('source') == str(start_id) and edge.get('target') == str(end_id)) or (edge.get('source') == str(end_id) and edge.get('target') == str(start_id)):
            # prendo count
            current_count = int(edge.findall('data')[1].text)
            print("current_count: ",current_count)
            edge.findall('data')[1].text = str(current_count + 1)
            # prebdo amplitude
            current_amplitude = float(edge.findall('data')[0].text)
            new_amplitude = (current_amplitude * current_count + amplitude) / (current_count + 1)  # Media delle ampiezze
            edge.findall('data')[0].text = str(new_amplitude)
            print("new_amplitude:",new_amplitude)
            updated = True

    if not updated:
        print("edge not present. Updating graphml")
        new_edge = ET.SubElement(root.find('.//graph'), 'edge', source=str(start_id), target=str(end_id))
        ET.SubElement(new_edge, 'data', key='weight').text = str(amplitude)

    tree.write(file_path)



def load_graph_from_json(json_file):
    with open(json_file) as f:
        data = json.load(f)
    return data

def load_nodes_from_csv(csv_file):
    nodes = {}
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            node_id = int(row['index'])
            latitude = float(row['latitude'])
            longitude = float(row['longitude'])
            nodes[node_id] = (latitude, longitude)
    return nodes


def build_graph(graph_file):
    tree = ET.parse(graph_file)
    root = tree.getroot()
    graph = nx.Graph()
    # Rimuovi namespace e aggiungi nodi con coordinate
    for node in root.findall('.//graph'):
        for child in node:
            if remove_namespace(child.tag) == 'node':
                node_id = int(child.get('id'))
                latitude = None
                longitude = None
                for data in child:
                    key = data.get('key')
                    if key == 'latitude':
                        latitude = float(data.text)
                    elif key == 'longitude':
                        longitude = float(data.text)
                if latitude is not None and longitude is not None:
                    graph.add_node(node_id, latitude=latitude, longitude=longitude)
                else:
                    print(f"Missing coordinates for node {node_id}")
    
    # Rimuovi namespace e aggiungi archi con i pesi
    for edge in root.findall('.//graph'):
        for child in edge:
            if remove_namespace(child.tag) == 'edge':
                source = int(child.get('source'))
                target = int(child.get('target'))
                weight = None
                for data in child:
                    if data.get('key') == 'weight':
                        weight = float(data.text)
                if weight is not None:
                    graph.add_edge(source, target, weight=weight)
                else:
                    print(f"Missing weight for edge from {source} to {target}")
    return graph

def snap_to_road(latitude1, longitude1, latitude2, longitude2, path):
    params = {
        'path': f'{latitude1},{longitude1}|{latitude2},{longitude2}',
        'key': GOOGLE_MAPS_API_KEY,
        'interpolate': True
        
    }
    response = requests.get(GOOGLE_MAPS_API_URL, params=params)
    if response.status_code == 200:
        for snapped_point in response.json()['snappedPoints']:
            path.append((snapped_point['location']['latitude'], snapped_point['location']['longitude']))
            
        return path
    else:
        return None

def haversine(lat1, lon1, lat2, lon2):
    # Raggio della Terra in chilometri
    R = 6371.0

    # Converti le coordinate in radianti
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Differenze di latitudine e longitudine
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Applica la formula di Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

# Funzione per aggiornare il file GraphML con i valori del file JSON
def setup_graphml(json_data, file_path='grafo_completo.graphml'):
    # Parse del file GraphML e rimozione del namespace
    tree = ET.parse(file_path)
    root = remove_namespace(tree.getroot())

    # Aggiornamento dei dati nel file GraphML
    for entry in json_data:
        start_id = entry['startCrossingId']
        end_id = entry['endCrossingId']
        count = entry['count']
        amplitude = entry['amplitude']

        for edge in root.findall('.//edge'):
            if edge.get('source') == str(start_id) and edge.get('target') == str(end_id):
                for data in edge.findall('data'):
                    if data.get('key') == 'weight':
                        data.text = str(amplitude)  # Update weight with amplitude value
                        print(f"Updated edge {start_id} -> {end_id} with amplitude {amplitude}")
                    if data.get('key') == 'count':
                        data.text = str(count)  # Update count with count value
                        print(f"Updated edge {start_id} -> {end_id} with count {count}")    
    

    # Salva il file GraphML senza namespace
    new_tree = ET.ElementTree(root)
    new_tree.write(file_path, encoding='utf-8', xml_declaration=True)


def remove_namespace(elem):
    if isinstance(elem, str):
        return elem
    # Rimuovi il namespace dagli attributi
    elem.attrib = {k.split('}')[1] if '}' in k else k: v for k, v in elem.attrib.items()}
    # Rimuovi il namespace dal tag
    elem.tag = elem.tag.split('}')[1] if '}' in elem.tag else elem.tag
    # Ricorsivamente rimuovi il namespace dai figli
    for child in elem:
        remove_namespace(child)
    return elem


if __name__ == '__main__':
    app.run(host=config.ip_address, port=5000, debug = True)
