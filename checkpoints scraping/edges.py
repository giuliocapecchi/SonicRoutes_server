import csv

# Dizionario per memorizzare le strade associate a ciascun nodo
nodes = {}

# Leggi il file CSV e popola il dizionario dei nodi
with open('final_data_2.0.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        node_index = int(row['id'])
        street_names = row['street_name'].split('; ')
        nodes[node_index] = street_names

# Funzione per trovare gli archi con strade in comune
def find_common_edges():
    edges = []
    for node1 in nodes:
        for node2 in nodes:
            if node1 != node2:
                common_streets = set(nodes[node1]) & set(nodes[node2])
                if common_streets:
                    edges.append((node1, node2, '; '.join(common_streets)))
    return edges

# Scrivi gli archi con strade in comune su un nuovo file CSV
def write_edges_to_csv(edges):
    with open('common_edges.csv', 'w', newline='') as csvfile:
        fieldnames = ['source', 'target', 'weight', 'count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for edge in edges:
            writer.writerow({'source': edge[0], 'target': edge[1], 'weight': 10000, 'count': 0})

# Trova gli archi con strade in comune e scrivi su file CSV
common_edges = find_common_edges()
write_edges_to_csv(common_edges)

print("File 'common_edges.csv' creato con successo!")
