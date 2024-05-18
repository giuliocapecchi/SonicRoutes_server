import folium
import pandas as pd
import json
from branca.colormap import LinearColormap

def leggi_file_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def visualizza_mappa(checkpoints, noise_data):
    # Crea la mappa centrata su una posizione iniziale
    mappa = folium.Map(location=[43.7175, 10.3942], zoom_start=14)
    
    # Estrai il massimo conteggio di rumori
    max_count = max(entry['count'] for entry in noise_data)
    
    # Crea una colormap che va da verde a rosso basata sul massimo conteggio
    colormap = LinearColormap(['green', 'yellow', 'red'], vmin=0, vmax=max_count, caption='Count dei Rumori')
    
    # Itera sui segmenti stradali e colora i segmenti sulla mappa
    for noise_entry in noise_data:
        start_crossing_id = noise_entry['startCrossingId']
        end_crossing_id = noise_entry['endCrossingId']
        count = noise_entry['count']
        
        # Trova i checkpoint corrispondenti agli incroci di inizio e fine
        start_checkpoint = checkpoints.loc[checkpoints['index'] == start_crossing_id]
        end_checkpoint = checkpoints.loc[checkpoints['index'] == end_crossing_id]
        
        # Estrai le coordinate dei checkpoint di inizio e fine
        start_lat, start_lon = start_checkpoint['latitude'].values[0], start_checkpoint['longitude'].values[0]
        end_lat, end_lon = end_checkpoint['latitude'].values[0], end_checkpoint['longitude'].values[0]
        
        # Calcola il colore in base al conteggio dei rumori
        colore = colormap(count)
        
        # Crea il segmento stradale sulla mappa
        folium.PolyLine(locations=[[start_lat, start_lon], [end_lat, end_lon]], color=colore, weight=5).add_to(mappa)
    
    # Aggiungi un marker per ogni checkpoint
    for index, checkpoint in checkpoints.iterrows():
        latitudine = checkpoint['latitude']
        longitudine = checkpoint['longitude']
        street_name = checkpoint['street_name']
        
        # Aggiungi un marker per ogni checkpoint
        folium.Marker(location=[latitudine, longitudine], popup=street_name).add_to(mappa)
    
    # Aggiungi la legenda alla mappa
    colormap.add_to(mappa)
    
    # Salva la mappa come file HTML
    mappa.save('mappa_checkpoint_colored_by_count.html')

def main():
    # Carica i checkpoint da file CSV
    checkpoints = pd.read_csv('data/intersections_clustered.csv')
    
    # Carica i dati di rumori da file JSON
    noise_data = leggi_file_json('data/data.json')
    
    # Visualizza la mappa con i segmenti stradali collegati e colorati in base al conteggio dei rumori e con i marker per i checkpoint
    visualizza_mappa(checkpoints, noise_data)

if __name__ == "__main__":
    main()
