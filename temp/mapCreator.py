import folium
import pandas as pd
import json
from branca.colormap import LinearColormap

def leggi_file_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def visualizza_mappa(checkpoints, z_scores):
    # Crea la mappa centrata su una posizione iniziale
    mappa = folium.Map(location=[43.7175, 10.3942], zoom_start=14)
    
    # Crea una colormap che va da verde a rosso
    colormap = LinearColormap(['green', 'yellow', 'red'], vmin=-3, vmax=3, caption='Z-Score dei Rumori')
    
    # Itera sui segmenti stradali e colora i segmenti sulla mappa
    for index, checkpoint in checkpoints.iterrows():
        latitudine = checkpoint['latitude']
        longitudine = checkpoint['longitude']
        street_name = checkpoint['street_name']
        
        # Aggiungi un marker per ogni checkpoint
        folium.Marker(location=[latitudine, longitudine], popup=street_name).add_to(mappa)
    
    # Itera sui dati dei segmenti stradali e colora i segmenti sulla mappa
    for z_score_data in z_scores:
        start_crossing_id = z_score_data['startCrossingId']
        end_crossing_id = z_score_data['endCrossingId']
        z_score = z_score_data['z_score']
        
        # Trova i checkpoint corrispondenti agli incroci di inizio e fine
        start_checkpoint = checkpoints.loc[checkpoints['index'] == start_crossing_id]
        end_checkpoint = checkpoints.loc[checkpoints['index'] == end_crossing_id]
        
        # Estrai le coordinate dei checkpoint di inizio e fine
        start_lat, start_lon = start_checkpoint['latitude'].values[0], start_checkpoint['longitude'].values[0]
        end_lat, end_lon = end_checkpoint['latitude'].values[0], end_checkpoint['longitude'].values[0]
        
        # Calcola il colore in base allo z-score
        colore = colormap(z_score)
        
        # Crea il segmento stradale sulla mappa
        folium.PolyLine(locations=[[start_lat, start_lon], [end_lat, end_lon]], color=colore, weight=5).add_to(mappa)
    
    # Aggiungi la legenda alla mappa
    colormap.add_to(mappa)
    
    # Salva la mappa come file HTML
    mappa.save('mappa_checkpoint_colored.html')

def main():
    # Carica i checkpoint da file CSV
    checkpoints = pd.read_csv('data/intersections_clustered.csv')
    
    # Carica i dati di z-score dei rumori da file JSON
    z_scores = leggi_file_json('data/z_scores_rumori.json')
    
    # Visualizza la mappa con i checkpoint collegati e colorati
    visualizza_mappa(checkpoints, z_scores)

if __name__ == "__main__":
    main()
