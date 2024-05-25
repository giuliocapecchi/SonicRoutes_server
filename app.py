import statistics
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import folium
from branca.colormap import LinearColormap
import pandas as pd
import networkx as nx
import pandas as pd
import networkx as nx
import xml.etree.ElementTree as ET
from flask import Flask
import config


app = Flask(__name__)

# Pagina principale
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mappa_count')
def mappa_count():
    checkpoints = pd.read_csv('data/pisa.csv')

    graph = build_graph('data/grafo_completo.graphml')
    
    # Estrai il massimo count
    max_count = max(data['count'] for _, _, data in graph.edges(data=True) if 'count' in data)
    
    # Crea una colormap che va da verde a rosso basata sul massimo conteggio
    colormap = LinearColormap(['green', 'yellow', 'red'], vmin=0, vmax=max_count, caption='Count dei Rumori')
    
    # Crea la mappa
    mappa = folium.Map(location=[43.7175, 10.3942], zoom_start=16)
    
    # Itera sui segmenti stradali e colora i segmenti sulla mappa
    for source, target, data in graph.edges(data=True):
        start_lat = graph.nodes[source]['latitude']
        start_lon = graph.nodes[source]['longitude']
        end_lat = graph.nodes[target]['latitude']
        end_lon = graph.nodes[target]['longitude']
        count = data.get('count')
        
        if count is not None:
            # Calcola il colore in base al conteggio dei rumori
            colore = colormap(count)
            
            # Crea il popup per il segmento
            popup_text = f"Count: {count}"
            
            # Crea il segmento stradale sulla mappa con il popup
            folium.PolyLine(locations=[[start_lat, start_lon], [end_lat, end_lon]], color=colore, weight=5, popup=popup_text).add_to(mappa)
    
    for _, checkpoint in checkpoints.iterrows():
        latitudine = checkpoint['latitude']
        longitudine = checkpoint['longitude']
        street_name = checkpoint['street_name']
        id = checkpoint["index"]
        
        # Aggiungi un marker per ogni checkpoint
        folium.Marker(location=[latitudine, longitudine], popup=f"{id}, {street_name}").add_to(mappa)

    # Aggiungi la legenda alla mappa
    colormap.add_to(mappa)

    # Aggiungo il bottone per tornare alla home
    mappa.get_root().html.add_child(folium.Element('''
        <div id="button-container" style="position: absolute; bottom: 20px; right: 20px; z-index: 1000;">
            <button style="display: block; width: 40vh; height: auto; margin: 20px auto; padding: 15px; text-align: center; text-decoration: none; color: #fff; background-color: #007bff; border-radius: 8px; transition: background-color 0.3s ease; font-size: 2em; box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);" onclick="window.location.href='/'">Go back</button>
        </div>
    '''))

    # Salva la mappa come file HTML temporaneo
    mappa.save('templates/mappa_count.html')
    
    return render_template('mappa_count.html')

def get_edge_color(weight):
    if weight > 5000:
        return 'red'
    else:
        return colormap(weight)
    
colormap = LinearColormap(['green', 'yellow', 'red'], vmin=0, vmax=5000, caption='Noise')

def get_edge_color(weight):
    if weight > 5000:
        return 'red'
    else:
        return colormap(weight)

@app.route('/mappa_rumori')
def mappa_rumore():
    checkpoints = pd.read_csv('data/pisa.csv')

    graph = build_graph('data/grafo_completo.graphml')
    # Crea la mappa
    mappa = folium.Map(location=[43.7175, 10.3942], zoom_start=16)
    
    # Itera sui segmenti stradali e colora i segmenti sulla mappa
    for source, target, data in graph.edges(data=True):
        start_lat = graph.nodes[source]['latitude']
        start_lon = graph.nodes[source]['longitude']
        end_lat = graph.nodes[target]['latitude']
        end_lon = graph.nodes[target]['longitude']
        noise = round(data['weight'],3)
        colore = get_edge_color(noise)
        
        # Crea il segmento stradale sulla mappa
        popup_text = f"Average: {noise}"
        folium.PolyLine(locations=[[start_lat, start_lon], [end_lat, end_lon]], color=colore, weight=5, popup=popup_text).add_to(mappa)
    
    for _, checkpoint in checkpoints.iterrows():
        latitudine = checkpoint['latitude']
        longitudine = checkpoint['longitude']
        street_name = checkpoint['street_name']
        id = checkpoint["index"]

        # Aggiungi un marker per ogni checkpoint
        folium.Marker(location=[latitudine, longitudine], popup=f"{id}, {street_name}").add_to(mappa)

    # Aggiungi la legenda alla mappa
    colormap.add_to(mappa)

    # Aggiungo il bottone per tornare alla home
    mappa.get_root().html.add_child(folium.Element('''
        <div id="button-container" style="position: absolute; bottom: 20px; right: 20px; z-index: 1000;">
            <button style="display: block; width: 40vh; height: auto; margin: 20px auto; padding: 15px; text-align: center; text-decoration: none; color: #fff; background-color: #007bff; border-radius: 8px; transition: background-color 0.3s ease; font-size: 2em; box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);" onclick="window.location.href='/'">Go back</button>
        </div>
    '''))

    # Salva la mappa come file HTML
    mappa.save('templates/mappa_rumori.html')
    
    return render_template('mappa_rumori.html')


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
                count = None
                for data in child:
                    if data.get('key') == 'weight':
                        weight = float(data.text)
                    if data.get('key') == 'count':
                        count = float(data.text)
                if weight is not None and count is not None:
                    graph.add_edge(source, target, weight=weight, count=count)
                else:
                    print(f"Missing weight or count for edge from {source} to {target}")
    return graph

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


def calculate_graph_metrics(graph_file):
    G = build_graph(graph_file)
    
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    
    density = round(nx.density(G), 3)
    degrees = nx.degree(G) # the result is a tuple
    list_degrees = [degree for _, degree in degrees]
    avg_degree = round(statistics.mean(list_degrees), 3)
    median_degree = round(statistics.median(list_degrees), 3)
    assortativity_degree = round(nx.degree_assortativity_coefficient(G), 3)
    clustering_coeffs = nx.clustering(G).values()
    avg_clustering_coeff = round(statistics.mean(clustering_coeffs), 3)
    median_clustering_coeff = round(statistics.median(clustering_coeffs), 3)

    # for 'weight' label
    strengths = nx.degree(G, weight="weight")
    list_strengths = [strength for _, strength in strengths]
    avg_weigth_strength = round(statistics.mean(list_strengths), 3)
    median_weigth_strength = round(statistics.median(list_strengths), 3)
    assortativity_weigth_strength = round(nx.degree_assortativity_coefficient(G, weight='weight'), 3)
    clustering_coeffs_weight_weighted = nx.clustering(G, weight='weight').values()
    avg_clustering_coeff_weigth_weighted = round(statistics.mean(clustering_coeffs_weight_weighted), 3)
    median_clustering_coeff_weigth_weighted = round(statistics.median(clustering_coeffs_weight_weighted), 3)

    # for 'count' label
    count_strengths = nx.degree(G, weight="count")
    list_count_strengths = [strength for _, strength in count_strengths]
    avg_count_strength = round(statistics.mean(list_count_strengths), 3)
    median_count_strength = round(statistics.median(list_count_strengths), 3)
    assortativity_count_strength = round(nx.degree_assortativity_coefficient(G, weight='count'), 3)
    clustering_coeffs_count_weighted = nx.clustering(G, weight='count').values()
    avg_clustering_coeff_count_weighted = round(statistics.mean(clustering_coeffs_count_weighted), 3)
    median_clustering_coeff_count_weighted = round(statistics.median(clustering_coeffs_count_weighted), 3)

    
    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "density": density,
        "avg_degree": avg_degree,
        "median_degree": median_degree,
        "assortativity_degree": assortativity_degree,
        "avg_clustering_coeff": avg_clustering_coeff,
        "median_clustering_coeff": median_clustering_coeff,

        "avg_strength": avg_weigth_strength,
        "median_strength": median_weigth_strength,
        "assortativity_strength": assortativity_weigth_strength,
        "avg_clustering_coeff_weigth_weighted": avg_clustering_coeff_weigth_weighted,
        "median_clustering_coeff_weigth_weighted": median_clustering_coeff_weigth_weighted,

        "avg_count_strength": avg_count_strength,
        "median_count_strength": median_count_strength,
        "assortativity_count_strength": assortativity_count_strength,
        "avg_clustering_coeff_count_weighted": avg_clustering_coeff_count_weighted,
        "median_clustering_coeff_count_weighted": median_clustering_coeff_count_weighted
    
    }


@app.route('/metrics')
def metrics():
    graph_file = "data/grafo_completo.graphml"
    graph_metrics = calculate_graph_metrics(graph_file)
    print(graph_metrics)
    return render_template('metrics.html', **graph_metrics)


if __name__ == '__main__':
    checkpoints = pd.read_csv('data/pisa.csv')
    app.run(host=config.ip_address, port=5001, debug=True)
