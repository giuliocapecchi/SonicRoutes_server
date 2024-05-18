import folium
from folium import plugins
import json

# Carica i dati dal file JSON
with open('data/data.json') as f:
    data = json.load(f)

# Inizializza la mappa centrata sulla prima posizione
mymap = folium.Map(location=[data[0]['latitude'], data[0]['longitude']], zoom_start=10)

# Inizializza il plugin HeatMap
heat_data = []
for d in data:
    heat_data.append([d['latitude'], d['longitude'], d['amplitude']])

# Aggiungi la heatmap alla mappa
plugins.HeatMap(heat_data).add_to(mymap)

# Disegna il percorso sulla mappa
for i in range(len(data) - 1):
    folium.PolyLine(locations=[[data[i]['latitude'], data[i]['longitude']],
                               [data[i+1]['latitude'], data[i+1]['longitude']]],
                    color='blue').add_to(mymap)

# Visualizza la mappa
mymap.save("data/heatmap.html")

